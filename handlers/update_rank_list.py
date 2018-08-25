"""
Created by Gotham on 04-08-2018.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler
import flood_protection
from utility import Utility
import urllib3
import sqlite3
import ratings
from handlers import not_registered
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
timeouts = flood_protection.Spam_settings()
UPDA = 10000


class UpdateHandler:
    def __init__(self, mount_point, fallback):
        self.mount_point = mount_point
        self.fallback = fallback
        self.rating_obj = ratings.Rating()
        self.utility = Utility(mount_point)
        self.conv_handler = ConversationHandler(
            entry_points=[CommandHandler('update', self.updatesel)],
            allow_reentry=True,
            states={
                UPDA: [CallbackQueryHandler(self.updasel, pattern=r'\w*upd5\b')]
            },
            fallbacks=[fallback]
        )

    @staticmethod
    @timeouts.wrapper
    def updatesel(bot, update):
        keyboard = [[InlineKeyboardButton("Hackerearth", callback_data='HEupd5'),
                     InlineKeyboardButton("Hackerrank", callback_data='HRupd5')],
                    [InlineKeyboardButton("Codechef", callback_data='CCupd5'),
                     InlineKeyboardButton("Spoj", callback_data='SPupd5')],
                    [InlineKeyboardButton("Codeforces", callback_data='CFupd5'),
                     InlineKeyboardButton("ALL", callback_data='ALLupd5')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("PLEASE SELECT THE JUDGE FROM WHICH YOU WANT TO UPDATE YOUR PROFILE",
                                  reply_markup=reply_markup)
        return UPDA

    # FUNCTION TO UPDATE PARTICULR ENTRY USER SELECTED
    def updasel(self, bot, update):
        query = update.callback_query
        val = query.data
        val = str(val).replace("upd5", "")
        a = str(query.from_user.id)
        conn = sqlite3.connect(self.mount_point + 'coders1.db')
        c = conn.cursor()
        c.execute("SELECT id FROM handles WHERE id=(?)", (a,))
        if not not_registered.NotRegistered.fetchone(c, query, bot):
            conn.close()
            return ConversationHandler.END
        if val == "ALL":
            # IF USER SELECTED ALL UPDATING ALL HIS VALUES
            c.execute('SELECT id, HE, HR, CC, SP, CF FROM handles WHERE id=(?)', (a,))
            self.utility.update_function(c)
            bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        else:
            # ELSE ONLY UPDATING THE PARTICULAR ENTRY
            c.execute("SELECT " + val + " FROM handles WHERE id=(?)", (a,))
            for row in c.fetchall():
                if row[0] == "" or row[0] is None:
                    bot.edit_message_text(text='You are not registered to the bot with' + val,
                                          chat_id=query.message.chat_id,
                                          message_id=query.message.message_id)
                    conn.close()
                    return ConversationHandler.END
                else:
                    print(row[0])
                    i = 0
                    while i < 5:
                        ans = self.rating_obj.getAllData(val, str(row[0]))
                        if ans is not None:
                            break
                        i = i + 1
                    c.execute("UPDATE datas SET " + val + " = (?)  WHERE id = (?) ", (ans, a))
                    if not val == 'SP':
                        rating = self.rating_obj.parse_rating(val, ans)
                        c.execute("UPDATE priority SET " + val + " = (?) WHERE id = (?) ", (rating, a))
                bot.edit_message_text(text="" + ans, chat_id=query.message.chat_id, message_id=query.message.message_id)
            # RECREATING ALL THE XLMX FILES
            if val == 'SP':
                mysel = c.execute("SELECT name, " + val + " FROM datas")
                self.utility.xlsx_creator(mysel, self.mount_point + val + ".xlsx")
            else:
                mysel = c.execute(
                    "SELECT datas.name, datas." + val + " FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority." + val + " AS FLOAT) DESC")
                self.utility.xlsx_creator(mysel, self.mount_point + val + ".xlsx")
            mysel = c.execute(
                "SELECT datas.name, datas.HE, datas.HR, datas.SP, datas.CF, datas.CC FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority.CF AS FLOAT) DESC, CAST(priority.CC AS FLOAT) DESC, CAST(priority.HR AS FLOAT) DESC, CAST(priority.HE AS FLOAT) DESC")
            self.utility.xlsx_creator(mysel, self.mount_point + 'all.xlsx')
        bot.send_message(text='Successfully updated',
                         chat_id=query.message.chat_id)
        conn.commit()
        conn.close()
        return ConversationHandler.END
