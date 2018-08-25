"""
Created by Gotham on 04-08-2018.
"""
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters
import flood_protection
import sqlite3
import json
import time
import os
from utility import Utility
timeouts = flood_protection.Spam_settings()
BDC, DB, CF = range(12000, 12003)


class AdminHandle:
    def __init__(self, mount_point, admin_list, fallback):
        self.admin_list = admin_list
        self.mount_point = mount_point
        self.utility = Utility(mount_point)
        self.conv_handler1 = ConversationHandler(
            entry_points=[CommandHandler('broadcast', self.broadcast)],
            allow_reentry=True,
            states={
                BDC: [MessageHandler(Filters.text, self.broadcast_message)]
            },
            fallbacks=[fallback]
        )
        self.conv_handler2 = ConversationHandler(
            entry_points=[CommandHandler('senddb', self.getDb)],
            allow_reentry=True,
            states={
                DB: [MessageHandler(Filters.document, self.db)]
            },
            fallbacks=[fallback]
        )

    # START OF ADMIN CONVERSATION HANDLER TO BROADCAST MESSAGE
    @timeouts.wrapper_for_class_methods
    def broadcast(self, bot, update):
        if self.not_admin(update):
            return ConversationHandler.END
        update.message.reply_text("Send your message")
        return BDC

    def broadcast_message(self, bot, update):
        message = update.message.text
        conn = sqlite3.connect(self.mount_point + 'coders1.db')
        c = conn.cursor()
        c.execute('select id from handles union select id from subscribers')
        for row in c.fetchall():
            try:
                bot.send_message(text=message, chat_id=row[0])
            except:
                pass
            time.sleep(1)
        c.close()
        conn.close()
        return ConversationHandler.END

    # END OF ADMIN CONVERSATION HANDLER TO BROADCAST MESSAGE

    # START OF ADMIN CONVERSATION HANDLER TO REPLACE THE DATABASE
    @timeouts.wrapper_for_class_methods
    def getDb(self, bot, update):
        if self.not_admin(update):
            return ConversationHandler.END
        update.message.reply_text("send your sqlite database")
        return DB

    def db(self, bot, update):
        file_id = update.message.document.file_id
        newFile = bot.get_file(file_id)
        newFile.download(self.mount_point + 'coders1.db')
        update.message.reply_text("saved")
        return ConversationHandler.END

    # END OF ADMIN CONVERSATION HANDLER TO REPLACE THE DATABASE
    def not_admin(self, update):
        if not str(update.message.chat_id) in self.admin_list:
            update.message.reply_text("sorry you are not an admin")
            return True
        else:
            return False

    # ADMIN COMMAND HANDLER FOR GETTING THE DATABASE
    @timeouts.wrapper_for_class_methods
    def givememydb(self, bot, update):
        if self.not_admin(update):
            return
        bot.send_document(chat_id=update.message.chat_id, document=open(self.mount_point + 'coders1.db', 'rb'))

    # ADMIN COMMAND HANDLER FOR GETTING THE CODEFORCES JSON
    @timeouts.wrapper_for_class_methods
    def getcfjson(self, bot, update):
        if self.not_admin(update):
            return
        bot.send_document(chat_id=update.message.chat_id, document=open(self.mount_point + 'codeforces.json', 'rb'))

    # ADMIN COMMAND HANDLER FUNCTION TO GET THE DETAILS OF HANDLES OF ALL THE USERS IN DATABASE
    @timeouts.wrapper_for_class_methods
    def adminhandle(self, bot, update):
        if self.not_admin(update):
            return
        conn = sqlite3.connect(self.mount_point + 'coders1.db')
        c = conn.cursor()
        mysel = c.execute("SELECT * FROM handles")
        self.utility.xlsx_creator(mysel, "admin.xlsx")
        bot.send_document(chat_id=update.message.chat_id, document=open('admin.xlsx', 'rb'))
        os.remove('admin.xlsx')
        conn.close()
