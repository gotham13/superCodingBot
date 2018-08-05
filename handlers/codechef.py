"""
Created by Gotham on 03-08-2018.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler
import flood_protection
import random
timeouts = flood_protection.Spam_settings()
QSELCC = 2000


class CcHandler:
    def __init__(self, cc_dict, fallback):
        self.cc_dict = cc_dict
        self.conv_handler = ConversationHandler(
            entry_points=[CommandHandler('randomcc', self.randomcc)],
            allow_reentry=True,
            states={

                QSELCC: [CallbackQueryHandler(self.qselcc, pattern=r'\w*cc1\b')]

            },
            fallbacks=[fallback]
        )

    @staticmethod
    @timeouts.wrapper
    def randomcc(bot, update):
        keyboard = [[InlineKeyboardButton("Beginner", callback_data='BEGINNERcc1'),
                     InlineKeyboardButton("Easy", callback_data='EASYcc1')],
                    [InlineKeyboardButton("Medium", callback_data='MEDIUMcc1'),
                     InlineKeyboardButton("Hard", callback_data='HARDcc1')],
                    [InlineKeyboardButton("Challenge", callback_data='CHALLENGEcc1'),
                     InlineKeyboardButton("Peer", callback_data='PEERcc1')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Please select the type of question', reply_markup=reply_markup)
        return QSELCC

    # FUNCTION FOR SENDING THE RANDOM QUESTION TO USER ACCORDING TO HIS CHOICE
    def qselcc(self, bot, update):
        query = update.callback_query
        val = query.data
        if val == 'BEGINNERcc1':
            strn = random.choice(self.cc_dict['school']).text
        if val == 'EASYcc1':
            strn = random.choice(self.cc_dict['easy']).text
        if val == 'MEDIUMcc1':
            strn = random.choice(self.cc_dict['medium']).text
        if val == 'HARDcc1':
            strn = random.choice(self.cc_dict['hard']).text
        if val == 'CHALLENGEcc1':
            strn = random.choice(self.cc_dict['challenge']).text
        if val == 'PEERcc1':
            strn = random.choice(self.cc_dict['peer']).text
        val = str(val).replace("cc1", "")
        bot.edit_message_text(
            text="Random " + val + " question from codechef\n\n" + "https://www.codechef.com/problems/" + strn,
            chat_id=query.message.chat_id,
            message_id=query.message.message_id)
        return ConversationHandler.END

    def change_cc(self, cc_dict):
        self.cc_dict = cc_dict

    def get_cc(self):
        return self.cc_dict
