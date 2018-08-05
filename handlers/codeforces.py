"""
Created by Gotham on 31-07-2018.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler
import flood_protection
import random
import os
import shutil
import json
timeouts = flood_protection.Spam_settings()

QSELCF = 1000


class CfHandler:
    def __init__(self, mount_point, fallback):
        if not os.path.exists(mount_point + 'codeforces.json'):
            shutil.copy('codeforces.json', mount_point + 'codeforces.json')
        with open(mount_point + 'codeforces.json', 'r') as codeforces:
            self.qcf = json.load(codeforces)
        self.conv_handler10 = ConversationHandler(
            entry_points=[CommandHandler('randomcf', self.randomcf)],
            allow_reentry=True,
            states={
                QSELCF: [CallbackQueryHandler(self.qselcf, pattern=r'\w*cf1\b')]
            },
            fallbacks=[fallback]
        )

    # START OF CONVERSATION HANDLER FOR GETTING RANDOM QUESTION FROM CODEFORCES
    # FUNCTION TO GET INPUT ABOUT THE TYPE OF QUESTION FROM USER
    @staticmethod
    @timeouts.wrapper
    def randomcf(bot, update):
        keyboard = [[InlineKeyboardButton("A", callback_data='Acf1'),
                     InlineKeyboardButton("B", callback_data='Bcf1'), InlineKeyboardButton("C", callback_data='Ccf1')],
                    [InlineKeyboardButton("D", callback_data='Dcf1'),
                     InlineKeyboardButton("E", callback_data='Ecf1'), InlineKeyboardButton("F", callback_data='Fcf1')],
                    [InlineKeyboardButton("OTHERS", callback_data='OTHERScf1')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Please select the type of question', reply_markup=reply_markup)
        return QSELCF

    # FUNCTION FOR SENDING THE RANDOM QUESTION TO USER ACCORDING TO HIS CHOICE
    def qselcf(self, bot, update):
        query = update.callback_query
        val = query.data
        if val == 'Acf1':
            strn = self.get_random_ques('A')
        elif val == 'Bcf1':
            strn = self.get_random_ques('B')
        elif val == 'Ccf1':
            strn = self.get_random_ques('C')
        elif val == 'Dcf1':
            strn = self.get_random_ques('D')
        elif val == 'Ecf1':
            strn = self.get_random_ques('E')
        elif val == 'Fcf1':
            strn = self.get_random_ques('F')
        elif val == 'OTHERScf1':
            strn = self.get_random_ques('OTHERS')
        val = str(val).replace("cf1", "")
        bot.edit_message_text(
            text="Random " + val + " question from codeforces\n\n" + strn,
            chat_id=query.message.chat_id,
            message_id=query.message.message_id)
        return ConversationHandler.END
        # END OF CONVERSATION HANDLER FOR GETTING RANDOM QUESTION FROM CODEFORCES

    def change_cf(self, qcf):
        self.qcf = qcf

    def get_random_ques(self, q_type):
        return random.choice(self.qcf[q_type])
