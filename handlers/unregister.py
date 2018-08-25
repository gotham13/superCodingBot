"""
Created by Gotham on 04-08-2018.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler
import flood_protection
import sqlite3
from handlers import not_registered
from utility import Utility
timeouts = flood_protection.Spam_settings()
REMOVER = 6000


class UnregHandler():
    def __init__(self, mount_point, fallback):
        self.utility = Utility(mount_point)
        self.mount_point = mount_point
        self.conv_handler = ConversationHandler(
            entry_points=[CommandHandler('unregister', self.unregister)],
            allow_reentry=True,
            states={
                REMOVER: [CallbackQueryHandler(self.remover, pattern=r'\w*rem2\b')]
            },
            fallbacks=[fallback]
        )

    @staticmethod
    @timeouts.wrapper
    def unregister(bot, update):
        keyboard = [[InlineKeyboardButton("Hackerearth", callback_data='HErem2'),
                     InlineKeyboardButton("Hackerrank", callback_data='HRrem2')],
                    [InlineKeyboardButton("Codechef", callback_data='CCrem2'),
                     InlineKeyboardButton("Spoj", callback_data='SPrem2')],
                    [InlineKeyboardButton("Codeforces", callback_data='CFrem2'),
                     InlineKeyboardButton("ALL", callback_data='ALLrem2')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Select the judge you want to unregister from", reply_markup=reply_markup)
        return REMOVER

    # FUNCTION FOR REMOVING DATA FROM DATABASE ACCORDING TO USERS CHOICE
    def remover(self, bot, update):
        query = update.callback_query
        val = query.data
        val = str(val).replace("rem2", "")
        conn = sqlite3.connect(self.mount_point + 'coders1.db')
        c = conn.cursor()
        a = str(query.from_user.id)
        c.execute("SELECT id FROM handles WHERE id=(?)", (a,))
        if not not_registered.NotRegistered.fetchone(c, query, bot):
            conn.close()
            return ConversationHandler.END
        if val == "ALL":
            # IF USER CHOSE ALL THEN DELETING HIS ENTIRE ROW FROM TABLES
            c.execute("DELETE FROM datas WHERE id = (?)", (a,))
            c.execute("DELETE FROM handles WHERE id = (?)", (a,))
            c.execute("DELETE FROM priority WHERE id = (?)", (a,))
            conn.commit()
            bot.edit_message_text(text='Unregistering please wait',
                                  chat_id=query.message.chat_id,
                                  message_id=query.message.message_id)
            # RECREATING ALL XLSX FILES
            self.utility.recreate_xlsx(c)
        else:
            c.execute("SELECT " + val + " FROM handles WHERE id=(?)", (a,))
            for row in c:
                if row[0] is None or row[0] == "":
                    bot.edit_message_text(
                        text='You are not registered to the bot. Please register using /register command',
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id)
                    conn.close()
                    return ConversationHandler.END
            # OTHER WISE REMOVING THE PARTICULAR ENTRY
            c.execute("UPDATE datas SET " + val + " = (?)  WHERE id = (?) ", ("", a))
            c.execute("UPDATE handles SET " + val + " = (?)  WHERE id = (?) ", ("", a))
            if not val == 'SP':
                c.execute("UPDATE priority SET " + val + " = (?)  WHERE id = (?) ", ("", a))
            conn.commit()
            bot.edit_message_text(text='Unregistering please wait',
                                  chat_id=query.message.chat_id,
                                  message_id=query.message.message_id)
            c.execute("SELECT name, " + val + " FROM datas")
            # RECREATING XLSX FILE
            if not val == 'SP':
                mysel = c.execute(
                    "SELECT datas.name, datas." + val + " FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority." + val + " AS FLOAT) DESC")
                self.utility.xlsx_creator(mysel, self.mount_point + val + ".xlsx")
            else:
                mysel = c.execute("SELECT name, " + val + " FROM datas")
                self.utility.xlsx_creator(mysel, self.mount_point + val + ".xlsx")

        c.execute("SELECT HE, HR, SP, CF, CC FROM handles WHERE id =(?)", (a,))
        count = 0
        for row in c:
            for i in row:
                if i is None or i == "":
                    count = count + 1
        if count == 5:
            c.execute("DELETE FROM datas WHERE id = (?)", (a,))
            c.execute("DELETE FROM handles WHERE id = (?)", (a,))
            c.execute("DELETE FROM priority WHERE id = (?)", (a,))
            conn.commit()
        mysel = c.execute(
            "SELECT datas.name, datas.HE, datas.HR, datas.SP, datas.CF, datas.CC FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority.CF AS FLOAT) DESC, CAST(priority.CC AS FLOAT) DESC, CAST(priority.HR AS FLOAT) DESC, CAST(priority.HE AS FLOAT) DESC")
        self.utility.xlsx_creator(mysel, self.mount_point + 'all.xlsx')
        bot.send_message(chat_id=query.message.chat_id, text="Successfully unregistered")
        conn.commit()
        conn.close()
        return ConversationHandler.END
