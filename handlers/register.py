"""
Created by Gotham on 03-08-2018.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import flood_protection
import sqlite3
from utility import Utility
import ratings
timeouts = flood_protection.Spam_settings()
NAME, JUDGE, HANDLE = range(3000, 3003)


class RegHandler:
    def __init__(self, mount_point, fallback):
        self.mount_point = mount_point
        self.conv_handler = ConversationHandler(
            entry_points=[CommandHandler('register', self.register)],
            allow_reentry=True,
            states={

                NAME: [MessageHandler(Filters.text, self.name, pass_user_data=True)],

                JUDGE: [CallbackQueryHandler(self.judge, pass_user_data=True, pattern=r'\w*reg1\b')],

                HANDLE: [MessageHandler(Filters.text, self.handle, pass_user_data=True)]
            },

            fallbacks=[fallback]
        )

    @staticmethod
    @timeouts.wrapper
    def register(bot, update):
        update.message.reply_text('Hi,please enter your name ', reply_markup=ForceReply(True))
        return NAME

    @staticmethod
    def name(bot, update, user_data):
        user_data['name'] = update.message.text.upper()
        keyboard = [[InlineKeyboardButton("Hackerearth", callback_data='HEreg1'),
                     InlineKeyboardButton("Hackerrank", callback_data='HRreg1')],
                    [InlineKeyboardButton("Codechef", callback_data='CCreg1'),
                     InlineKeyboardButton("Spoj", callback_data='SPreg1')],
                    [InlineKeyboardButton("Codeforces", callback_data='CFreg1')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('please enter the online judge you want to setup with  the bot',
                                  reply_markup=reply_markup)
        return JUDGE

    @staticmethod
    def judge(bot, update, user_data):
        query = update.callback_query
        choices = ['HEreg1', 'HRreg1', 'CFreg1', 'CCreg1', 'SPreg1']
        if query.data not in choices:
            return ConversationHandler.END
        user_data['code'] = str(query.data).replace("reg1", "")
        bot.edit_message_text(text='selected',
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        bot.send_message(chat_id=query.message.chat_id, text="please enter your handle",reply_markup=ForceReply(True))
        return HANDLE

    def handle(self, bot, update, user_data):
        user = str(update.message.from_user.id)
        handle1 = update.message.text
        name1 = user_data['name']
        code1 = user_data['code']
        rating_obj = ratings.Rating()
        all_data = rating_obj.getAllData(code1, handle1)
        if all_data is None:
            update.message.reply_text('wrong id')
            user_data.clear()
            return ConversationHandler.END
        conn = sqlite3.connect(self.mount_point + 'coders1.db')
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO datas (id, name, " + code1 + ") VALUES (?, ?, ?)", (user, name1, all_data))
        c.execute("INSERT OR IGNORE INTO handles (id, name, " + code1 + ") VALUES (?, ?, ?)", (user, name1, handle1))
        if c.rowcount == 0:
            c.execute("UPDATE datas SET " + code1 + " = (?) , name= (?) WHERE id = (?) ", (all_data, name1, user))
            c.execute("UPDATE handles SET " + code1 + " = (?) , name= (?) WHERE id = (?) ", (handle1, name1, user))
        if code1 == 'SP':
            c.execute("INSERT OR IGNORE INTO priority (id) VALUES(?)", (user,))
        else:
            rating = rating_obj.parse_rating(code1, all_data)
            c.execute("INSERT OR IGNORE INTO priority (id," + code1 + ") VALUES(?, ?)", (user, rating))
            if c.rowcount == 0:
                c.execute("UPDATE  priority SET " + code1 + " = (?) WHERE id = (?) ", (rating, user))
        conn.commit()
        # BELOW LINES ARE USED TO CREATE XLSX FILES OF ALL SORTS OF RANKLIST
        # SO WHEN USER ASKS FOR RANKLIST THERE IS NO DELAY
        mysel = c.execute(
            "SELECT datas.name, datas.HE, datas.HR, datas.SP, datas.CF, datas.CC FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority.CF AS FLOAT) DESC, CAST(priority.CC AS FLOAT) DESC, CAST(priority.HR AS FLOAT) DESC, CAST(priority.HE AS FLOAT) DESC")
        Utility.xlsx_creator(mysel, self.mount_point + 'all.xlsx')
        if code1 == 'SP':
            mysel = c.execute("SELECT name, " + code1 + " FROM datas")
            Utility.xlsx_creator(mysel, self.mount_point + code1 + ".xlsx")
        else:
            mysel = c.execute(
                "SELECT datas.name, datas." + code1 + " FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority." + code1 + " AS FLOAT) DESC")
            Utility.xlsx_creator(mysel, self.mount_point + code1 + ".xlsx")
        conn.close()
        update.message.reply_text("Succesfully Registered")
        update.message.reply_text(name1 + "    \n" + all_data)
        user_data.clear()
        return ConversationHandler.END
