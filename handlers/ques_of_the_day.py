"""
Created by Gotham on 04-08-2018.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler
import flood_protection
import sqlite3
timeouts = flood_protection.Spam_settings()
SUBSEL, SUB, UNSUB = range(7000, 7003)


class QuesHandler:
    def __init__(self, mount_point, fallback):
        self.mount_point = mount_point
        self.conv_handler = ConversationHandler(
            entry_points=[CommandHandler('subscribe', self.subscribe)],
            allow_reentry=True,
            states={
                SUBSEL: [CallbackQueryHandler(self.subsel, pattern=r'\w*sub3\b', pass_user_data=True)],
                SUB: [CallbackQueryHandler(self.sub, pattern=r'\w*sub2\b', pass_user_data=True)]
            },
            fallbacks=[fallback]
        )
        self.conv_handler1 = ConversationHandler(
            entry_points=[CommandHandler('unsubscribe', self.unsubsel)],
            allow_reentry=True,
            states={
                UNSUB: [CallbackQueryHandler(self.unsub, pattern=r'\w*unsub4\b')]
            },
            fallbacks=[fallback]
        )

    @staticmethod
    @timeouts.wrapper
    def subscribe(bot, update):
        if update.message.chat_id < 0:
            update.message.reply_text(
                "I detected this is a group\nIf you subscribe here I will send questions to the group\nTo get questions to yourself subscribe to me in personal message")
        keyboard = [[InlineKeyboardButton("CODEFORCES", callback_data='CFsub3'),
                     InlineKeyboardButton("CODECHEF", callback_data='CCsub3')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(
            text="Please select the website to which you wish to subscribe for getting question of the day",
            chat_id=update.message.chat_id, reply_markup=reply_markup)
        return SUBSEL

    @staticmethod
    def subsel(bot, update, user_data):
        query = update.callback_query
        val = query.data
        if val == 'CCsub3':
            user_data['website'] = 'codechef'
            keyboard = [[InlineKeyboardButton("Beginner", callback_data='BEGINNERsub2'),
                         InlineKeyboardButton("Easy", callback_data='EASYsub2')],
                        [InlineKeyboardButton("Medium", callback_data='MEDIUMsub2'),
                         InlineKeyboardButton("Hard", callback_data='HARDsub2')],
                        [InlineKeyboardButton("Challenge", callback_data='CHALLENGEsub2'),
                         InlineKeyboardButton("Peer", callback_data='PEERsub2')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,
                                  text="Please select", reply_markup=reply_markup)
            return SUB
        elif val == 'CFsub3':
            user_data['website'] = 'codeforces'
            keyboard = [[InlineKeyboardButton("A", callback_data='Asub2'),
                         InlineKeyboardButton("B", callback_data='Bsub2'),
                         InlineKeyboardButton("C", callback_data='Csub2')],
                        [InlineKeyboardButton("D", callback_data='Dsub2'),
                         InlineKeyboardButton("E", callback_data='Esub2'),
                         InlineKeyboardButton("F", callback_data='Fsub2')],
                        [InlineKeyboardButton("OTHERS", callback_data='OTHERSsub2')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,
                                  text="Please select", reply_markup=reply_markup)
            return SUB

    def sub(self, bot, update, user_data):
        conn = sqlite3.connect(self.mount_point + 'coders1.db')
        query = update.callback_query
        val = query.data
        val = str(val).replace("sub2", "")
        a = str(query.message.chat_id)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO subscribers (id," + val + ") VALUES (?,1)", (a,))
        if c.rowcount == 0:
            c.execute("UPDATE subscribers SET " + val + " =1 WHERE id = (?) ", (a,))
        conn.commit()
        conn.close()
        bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,
                              text="I will send you a question of type " + val + " everyday from " + user_data[
                                  'website'] + " \nyou can use command /unsubscribe to unsubscribe ")
        user_data.clear()
        return ConversationHandler.END

    @timeouts.wrapper_for_class_methods
    def unsubsel(self, bot, update):
        names = ['', 'BEGINNER', 'EASY', 'MEDIUM', 'HARD', 'CHALLENGE', 'PEER', 'A', 'B', 'C', 'D', 'E', 'F', 'OTHERS']
        conn = sqlite3.connect(self.mount_point + 'coders1.db')
        c = conn.cursor()
        c.execute("SELECT id FROM subscribers WHERE id=(?)", (str(update.message.chat_id),))
        if not c.fetchone():
            update.message.reply_text("You are not subscribed to question of the day use /subscribe to subscribe")
            c.close()
            return ConversationHandler.END
        else:
            c.execute("SELECT * FROM subscribers WHERE id=(?)", (str(update.message.chat_id),))
            keyboard = []
            for row in c.fetchall():
                for i in range(1, len(row)):
                    if i <= 6:
                        site = "CODECHEF"
                    else:
                        site = "CODEFORCES"
                    if row[i] == 1:
                        keyboard.append(
                            [InlineKeyboardButton(site + ' ' + names[i], callback_data=names[i] + 'unsub4')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text("Select the one you want to unsubscribe from", reply_markup=reply_markup)
            c.close()
            conn.close()
            return UNSUB

    def unsub(self, bot, update):
        names = ['', 'BEGINNER', 'EASY', 'MEDIUM', 'HARD', 'CHALLENGE', 'PEER', 'A', 'B', 'C', 'D', 'E', 'F', 'OTHERS']
        query = update.callback_query
        val = query.data
        val = str(val).replace("unsub4", "")
        a = str(query.message.chat_id)
        conn = sqlite3.connect(self.mount_point + 'coders1.db')
        c = conn.cursor()
        c.execute("UPDATE subscribers SET " + val + " = 0 WHERE id = (?) ", (a,))
        conn.commit()
        c.execute("SELECT * FROM subscribers WHERE id=(?)", (a,))
        count = 0
        for row in c.fetchall():
            for i in row:
                if i == 0:
                    count = count + 1
        if count == len(names) - 1:
            c.execute("DELETE FROM subscribers WHERE id=(?)", (a,))
            conn.commit()
        bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text="unsubscribed")
        c.close()
        conn.close()
        return ConversationHandler.END