"""
Created by Gotham on 03-08-2018.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import flood_protection
from helper import HackerRankAPI
from utility import Utility
import os
timeouts = flood_protection.Spam_settings()
LANG, OTHER, CODE, DECODE, FILE, TESTCASES, FILETEST = range(4000, 4007)


class ComHandler:
    def __init__(self, api_key, fallback):
        self.compiler = HackerRankAPI(api_key=api_key)
        self.conv_handler = ConversationHandler(
            entry_points=[CommandHandler('compiler', self.compilers)],
            allow_reentry=True,
            states={
                LANG: [CallbackQueryHandler(self.lang, pass_user_data=True, pattern=r'\w*comp1\b')],
                CODE: [CallbackQueryHandler(self.code, pass_user_data=True, pattern=r'\w*so1\b')],
                DECODE: [MessageHandler(Filters.text, self.decode, pass_user_data=True)],
                TESTCASES: [MessageHandler(Filters.text, self.testcases, pass_user_data=True)],
                OTHER: [MessageHandler(Filters.text, self.other, pass_user_data=True)],
                FILE: [MessageHandler(Filters.document, self.filer, pass_user_data=True)],
                FILETEST: [MessageHandler(Filters.document, self.filetest, pass_user_data=True)]
            },
            fallbacks=[fallback]
        )

    @staticmethod
    @timeouts.wrapper
    def compilers(bot, update):
        keyboard = [[InlineKeyboardButton("C++", callback_data='cppcomp1'),
                     InlineKeyboardButton("Python", callback_data='pythoncomp1')],
                    [InlineKeyboardButton("C", callback_data='ccomp1'),
                     InlineKeyboardButton("Java", callback_data='javacomp1')],
                    [InlineKeyboardButton("Python3", callback_data='python3comp1'),
                     InlineKeyboardButton("Java8", callback_data='java8comp1')],
                    [InlineKeyboardButton("Other", callback_data='othercomp1')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Please select the language', reply_markup=reply_markup)
        return LANG

    # FUNCTION TO GET THE PROGRAMMING LANGUAGE
    def lang(self, bot, update, user_data):
        query = update.callback_query
        val = query.data
        val = str(val).replace("comp1", "")
        if val == "other":
            # IF USER CHOOSES OTHER
            s1 = ""
            for language in self.compiler.supportedlanguages():
                s1 = s1 + language + ", "
            bot.edit_message_text(text="" + s1[:-2], chat_id=query.message.chat_id,
                                  message_id=query.message.message_id)
            bot.send_message(chat_id=query.message.chat_id,
                             text="Enter the name of a language from the above list",
                             reply_markup=ForceReply(True))
            return OTHER
        else:
            # ELSE ASKING WETHER HE WANTS TO SEND SOURCE CODE OR A .TXT FILE
            user_data['lang'] = val
            keyboard = [[InlineKeyboardButton("Enter Source Code", callback_data='codeso1'),
                         InlineKeyboardButton("Send a .txt file", callback_data='fileso1')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.edit_message_text(text="please select", reply_markup=reply_markup, chat_id=query.message.chat_id,
                                  message_id=query.message.message_id)
            return CODE

    # FUNCTION TO GET THE SOURCE CODE OR .TXT FILE AS INPUT
    @staticmethod
    def code(bot, update, user_data):
        query = update.callback_query
        val = query.data
        val = str(val).replace("so1", "")
        if val == "code":
            bot.edit_message_text(
                text="selected",
                chat_id=query.message.chat_id, message_id=query.message.message_id)
            bot.send_message(chat_id=query.message.chat_id, text="please enter your code\n"
                                                                  "Please make sure that "
                                                                  "the first line is not a comment line",
                             reply_markup=ForceReply(True))
            return DECODE
        elif val == "file":
            bot.edit_message_text(text="please send your .txt file\nMaximum size 2mb", chat_id=query.message.chat_id,
                                  message_id=query.message.message_id)
            return FILE
        else:
            return ConversationHandler.END

    # FUNCTION TO GET TESTCASE FILE
    def filetest(self, bot, update, user_data):
        file_id = update.message.document.file_id
        if ComHandler.check_file_size(update):
            return ConversationHandler.END
        newFile = bot.get_file(file_id)
        newFile.download('test.txt')
        with open('test.txt', 'rt') as f:
            source = f.read()
        s1 = (str(user_data['code'])).replace("«", "<<").replace("»", ">>")
        result = self.compiler.run({'source': s1,
                               'lang': user_data['lang'],
                               'testcases': [source]
                               })
        Utility.paginate(bot, update, result)
        user_data.clear()
        os.remove('test.txt')
        return ConversationHandler.END

    @staticmethod
    def check_file_size(update):
        file_size = update.message.document.file_size
        if file_size > 2097152:
            update.message.reply_text("FILE SIZE GREATER THAN 2 MB")
            return True
        return False

    # FUNCTION TO DOWNLOAD THE FILE SENT AND EXTRACT ITS CONTENTS
    @staticmethod
    def filer(bot, update, user_data):
        file_id = update.message.document.file_id
        if ComHandler.check_file_size(update):
            return ConversationHandler.END
        newFile = bot.get_file(file_id)
        newFile.download('abcd.txt')
        with open('abcd.txt', 'r') as f:
            source = f.read()
        user_data['code'] = source
        custom_keyboard = [['#no test case', '#send a .txt file']]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True, resize_keybord=True)
        update.message.reply_text(
            'Please send test cases together as you would do in online ide\nIf you dont want to provide test cases select #no test case\n I you want to send test cases as .txt file select #send a .txt file',
            reply_markup=reply_markup)
        # REMOVING THE FILE AFTER PROCESS IS COMPLETE
        os.remove('abcd.txt')
        return TESTCASES

    # FUNCTION TO GET THE SOURCE CODE SENT BY USER
    @staticmethod
    def decode(bot, update, user_data):
        user_data['code'] = update.message.text
        custom_keyboard = [['#no test case', '#send a .txt file']]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True, resize_keybord=True)
        update.message.reply_text(
            'Please send test cases together as you would do in online ide\nIf you dont want to provide test cases select #no test case\n I you want to send test cases as .txt file select #send a .txt file',
            reply_markup=reply_markup)
        return TESTCASES

    # FUNCTION TO GET THE TEST CASES FROM THE USER
    def testcases(self, bot, update, user_data):
        markup = ReplyKeyboardRemove()
        s = update.message.text
        if s == "#send a .txt file":
            update.message.reply_text("Please send your testcases as a .txt file\nMaximum size 2mb",
                                      reply_markup=markup)
            return FILETEST
            # CONVERTING UNICODE CHARACTER TO DOUBLE GREATER THAN OR LESS THAN
            # WEIRD
        s1 = (str(user_data['code'])).replace("«", "<<").replace("»", ">>")
        if s == "#no test case":
            # USING COMPILER FUNCTION FROM helper.py script
            result = self.compiler.run({'source': s1,
                                   'lang': user_data['lang']
                                   })
            # GETTING OUTPUT FROM result CLASS in helper.py script
            Utility.paginate(bot, update, result)
        else:
            # AGAIN THE SAME DRILL
            result = self.compiler.run({'source': s1,
                                   'lang': user_data['lang'],
                                   'testcases': [s]
                                   })
            Utility.paginate(bot, update, result)
        user_data.clear()
        return ConversationHandler.END

    # FUNCTION FOR THE CASE WHERE USER HAD SELECTED OTHER
    @staticmethod
    def other(bot, update, user_data):
        s = update.message.text
        user_data['lang'] = s
        keyboard = [[InlineKeyboardButton("Enter Source Code", callback_data='codeso1'),
                     InlineKeyboardButton("Send a file", callback_data='fileso1')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("please select", reply_markup=reply_markup)
        return CODE
