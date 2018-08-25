"""
Created by Gotham on 04-08-2018.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
import flood_protection
import sqlite3
import os
timeouts = flood_protection.Spam_settings()
from utility import Utility
HOLO, SELECTION, SOLO, POLO, XOLO = range(8000, 8005)


class RankListHandler:
    def __init__(self, mount_point, fallback):
        self.mount_point = mount_point
        self.utility = Utility(mount_point)
        self.conv_handler = ConversationHandler(
            entry_points=[CommandHandler('ranklist', self.ranklist)],
            allow_reentry=True,
            states={

                SELECTION: [CallbackQueryHandler(self.selection, pattern=r'\w*sel1\b')],
                HOLO: [CallbackQueryHandler(self.holo, pattern=r'\w*list6\b')],
                SOLO: [CallbackQueryHandler(self.solo, pattern=r'\w*list7\b')],
                POLO: [MessageHandler(Filters.text, self.polo, pass_user_data=True)],
                XOLO: [CallbackQueryHandler(self.xolo, pass_user_data=True, pattern=r'\w*list8\b')]
            },

            fallbacks=[fallback]
        )

    @staticmethod
    @timeouts.wrapper
    def ranklist(bot, update):
        keyboard = [[InlineKeyboardButton("EVERY ONE", callback_data='allsel1'),
                     InlineKeyboardButton("MINE", callback_data='minesel1')],
                    [InlineKeyboardButton("GET BY NAME", callback_data='getNamesel1')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Please select the ranklist you want", reply_markup=reply_markup)
        return SELECTION

    # FUNCTION TO GET THE USER REQUEST AND SHOW MENU OF RANKLISTS
    def selection(self, bot, update):
        query = update.callback_query
        val = query.data
        val = str(val).replace("sel1", "")
        if val == "all":
            keyboard = [[InlineKeyboardButton("Hackerearth", callback_data='HElist6'),
                         InlineKeyboardButton("Hackerrank", callback_data='HRlist6')],
                        [InlineKeyboardButton("Codechef", callback_data='CClist6'),
                         InlineKeyboardButton("Spoj", callback_data='SPlist6')],
                        [InlineKeyboardButton("Codeforces", callback_data='CFlist6'),
                         InlineKeyboardButton("ALL", callback_data='ALLlist6')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.edit_message_text(text='please select the judge or select all for showing all',
                                  reply_markup=reply_markup,
                                  chat_id=query.message.chat_id,
                                  message_id=query.message.message_id)
            return HOLO
        elif val == "mine":
            conn = sqlite3.connect(self.mount_point + 'coders1.db')
            c = conn.cursor()
            print(str(query.from_user.id))
            c.execute("SELECT id FROM datas WHERE id=" + str(query.from_user.id))
            if c.fetchone():
                keyboard = [[InlineKeyboardButton("Hackerearth", callback_data='HElist7'),
                             InlineKeyboardButton("Hackerrank", callback_data='HRlist7')],
                            [InlineKeyboardButton("Codechef", callback_data='CClist7'),
                             InlineKeyboardButton("Spoj", callback_data='SPlist7')],
                            [InlineKeyboardButton("Codeforces", callback_data='CFlist7'),
                             InlineKeyboardButton("ALL", callback_data='ALLlist7')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                bot.edit_message_text(text='please select the judge or select all for showing all',
                                      reply_markup=reply_markup,
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id)
                c.close()
                return SOLO
            else:
                conn.close()
                bot.edit_message_text(
                    text='You are not registered to the bot. please register to it using /register command',
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id)
                return ConversationHandler.END

        elif val == "getName":
            bot.edit_message_text(text='selected',
                                  chat_id=query.message.chat_id,
                                  message_id=query.message.message_id)
            bot.send_message(text="please enter the name", chat_id=query.message.chat_id, reply_markup=ForceReply(True))
            return POLO
        else:
            return ConversationHandler.END

    # FUNCTION TO GET THE USERS RANKLIST
    def solo(self, bot, update):
        query = update.callback_query
        val = query.data
        choices = ['HElist7', 'HRlist7', 'CClist7', 'SPlist7', 'CFlist7', 'ALLlist7']
        if val not in choices:
            return ConversationHandler.END
        val = str(val).replace("list7", "")
        conn = sqlite3.connect(self.mount_point + 'coders1.db')
        c = conn.cursor()
        if val == "ALL":
            a = str(query.from_user.id)
            bot.edit_message_text(text='Sending please wait',
                                  chat_id=query.message.chat_id,
                                  message_id=query.message.message_id)
            mysel = c.execute("SELECT name, HE, HR, SP, CC, CF FROM datas WHERE id=" + a)
            self.utility.xlsx_creator(mysel, 'me.xlsx')
            bot.send_document(chat_id=query.message.chat_id, document=open('me.xlsx', 'rb'))
            os.remove('me.xlsx')
        else:
            a = str(query.from_user.id)
            c.execute("SELECT " + val + " FROM datas WHERE id=" + a)
            for i in c.fetchall():
                if i[0] is None or i[0] == "":
                    bot.edit_message_text(text="NOT REGISTERED",
                                          chat_id=query.message.chat_id,
                                          message_id=query.message.message_id)
                else:
                    bot.edit_message_text(text="" + i[0],
                                          chat_id=query.message.chat_id,
                                          message_id=query.message.message_id)
        conn.commit()
        conn.close()
        return ConversationHandler.END

    # FUNCTION TO GET THE RANKLIST MENU OF THE USER BY SEARCHING HIS NAME
    def polo(self, bot, update, user_data):
        msg = update.message.text.upper()
        conn = sqlite3.connect(self.mount_point + 'coders1.db')
        c = conn.cursor()
        c.execute("SELECT name FROM handles WHERE name=(?)", (msg,))
        if c.fetchone():
            keyboard = [[InlineKeyboardButton("Hackerearth", callback_data='HElist8'),
                         InlineKeyboardButton("Hackerrank", callback_data='HRlist8')],
                        [InlineKeyboardButton("Codechef", callback_data='CClist8'),
                         InlineKeyboardButton("Spoj", callback_data='SPlist8')],
                        [InlineKeyboardButton("Codeforces", callback_data='CFlist8'),
                         InlineKeyboardButton("ALL", callback_data='ALLlist8')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text('please select the judge or select all for showing all',
                                      reply_markup=reply_markup)
            user_data['name1'] = msg
            conn.close()
            return XOLO
        else:
            conn.close()
            update.message.reply_text("Sorry this name is not registered with me.")
            return ConversationHandler.END

    # FUNCTION TO SHOW THE KIND OF RANKLIST USER WANTS
    def xolo(self, bot, update, user_data):
        query = update.callback_query
        val = query.data
        choices = ['HElist8', 'HRlist8', 'CClist8', 'SPlist8', 'CFlist8', 'ALLlist8']
        if val not in choices:
            return ConversationHandler.END
        val = str(val).replace("list8", "")
        name1 = user_data['name1']
        conn = sqlite3.connect(self.mount_point + 'coders1.db')
        c = conn.cursor()
        if val == "ALL":
            bot.edit_message_text(text='Sending please wait',
                                  chat_id=query.message.chat_id,
                                  message_id=query.message.message_id)
            mysel = c.execute("SELECT name, HE, HR, SP, CC, CF FROM datas WHERE name=(?)", (name1,))
            self.utility.xlsx_creator(mysel, 'det.xlsx')
            bot.send_document(chat_id=query.message.chat_id, document=open('det.xlsx', 'rb'))
            os.remove('det.xlsx')
        else:
            c.execute("SELECT " + val + " FROM datas WHERE name=(?)", (name1,))
            for i in c.fetchall():
                if i[0] is None or i[0] == "":
                    bot.edit_message_text(text="Not Registered",
                                          chat_id=query.message.chat_id,
                                          message_id=query.message.message_id)
                else:
                    bot.edit_message_text(text="" + i[0],
                                          chat_id=query.message.chat_id,
                                          message_id=query.message.message_id)
        user_data.clear()
        conn.close()
        return ConversationHandler.END

    # FUNCTION TO SHOW THE RANKLIST OF ALL THE PEOPLE
    def holo(self, bot, update):
        query = update.callback_query
        val = query.data
        choices = ['HElist6', 'HRlist6', 'CClist6', 'SPlist6', 'CFlist6', 'ALLlist6']
        if val not in choices:
            return ConversationHandler.END
        val = str(val).replace("list6", "")
        if val == "ALL":
            try:
                bot.edit_message_text(text='I am sending you the details',
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id)
                bot.send_document(chat_id=query.message.chat_id, document=open(self.mount_point + 'all.xlsx', 'rb'))
            except FileNotFoundError:
                bot.edit_message_text(text='Sorry no entry found',
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id)
                return ConversationHandler.END
        else:
            try:
                bot.edit_message_text(text='I am sending you the details',
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id)
                bot.send_document(chat_id=query.message.chat_id, document=open(self.mount_point + val + ".xlsx", 'rb'))
            except FileNotFoundError:
                bot.edit_message_text(text='Sorry no entry found',
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id)
                return ConversationHandler.END
        return ConversationHandler.END