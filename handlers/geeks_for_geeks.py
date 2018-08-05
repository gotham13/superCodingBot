"""
Created by Gotham on 04-08-2018.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler
import flood_protection
import json
timeouts = flood_protection.Spam_settings()
GFG1, GFG2, GFG3 = range(11000, 11003)


class GeeksForGeeksHandler:
    def __init__(self, fallback):
        self.conv_handler = ConversationHandler(
            entry_points=[CommandHandler('geeksforgeeks', self.gfg)],
            allow_reentry=True,
            states={
                GFG1: [CallbackQueryHandler(self.gfg1, pass_user_data=True, pattern=r'\w*gfg1\b')],
                GFG2: [CallbackQueryHandler(self.gfg2, pass_user_data=True, pattern='^.*gfg2.*$')],
                GFG3: [CallbackQueryHandler(self.gfg3, pass_user_data=True, pattern='^.*gfg3.*$')]
            },
            fallbacks=[fallback]
        )

    @staticmethod
    @timeouts.wrapper
    def gfg(bot, update):
        keyboard = [[InlineKeyboardButton("ALGORITHMS", callback_data='Algorithmsgfg1'),
                     InlineKeyboardButton("DATA STRUCTURES", callback_data='DSgfg1')],
                    [InlineKeyboardButton("GATE", callback_data='GATEgfg1'),
                     InlineKeyboardButton("INTERVIEW", callback_data='Interviewgfg1')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("please select", reply_markup=reply_markup)
        return GFG1

    # FUNCTION TO SHOW SUBMENU 1
    @staticmethod
    def gfg1(bot, update, user_data):
        query = update.callback_query
        val = query.data
        val = str(val).replace("gfg1", "")
        val = val + ".json"
        user_data['gfg'] = val
        if val == "Algorithms.json":
            keyboard = [[InlineKeyboardButton("Analysis of Algorithms", callback_data='Analysis of Algorithmsgfg2'),
                         InlineKeyboardButton("Searching and Sorting", callback_data='Searching and Sortinggfg2')],
                        [InlineKeyboardButton("Greedy Algorithms", callback_data='Greedy Algorithmsgfg2'),
                         InlineKeyboardButton("Dynamic Programming", callback_data='Dynamic Programminggfg2')],
                        [InlineKeyboardButton("Strings and Pattern Searching",
                                              callback_data='Strings and Pattern Searchinggfg2'),
                         InlineKeyboardButton("Backtracking", callback_data='Backtrackinggfg2')],
                        [InlineKeyboardButton("Geometric Algorithms", callback_data='Geometric Algorithmsgfg2'),
                         InlineKeyboardButton("Mathematical Algorithms", callback_data='Mathematical Algorithmsgfg2')],
                        [InlineKeyboardButton("Bit Algorithms", callback_data='Bit Algorithmsgfg2'),
                         InlineKeyboardButton("Randomized Algorithms", callback_data='Randomized Algorithmsgfg2')],
                        [InlineKeyboardButton("Misc Algorithms", callback_data='Misc Algorithmsgfg2'),
                         InlineKeyboardButton("Recursion", callback_data='Recursiongfg2')],
                        [InlineKeyboardButton("Divide and Conquer", callback_data='Divide and Conquergfg2')]]
        elif val == "DS.json":
            keyboard = [[InlineKeyboardButton("Linked Lists", callback_data='Linked Listsgfg2'),
                         InlineKeyboardButton("Stacks", callback_data='Stacksgfg2')],
                        [InlineKeyboardButton("Queue", callback_data='Queuegfg2'),
                         InlineKeyboardButton("Binary Trees", callback_data='Binary Treesgfg2')],
                        [InlineKeyboardButton("Binary Search Trees",
                                              callback_data='Binary Search Treesgfg2'),
                         InlineKeyboardButton("Heaps", callback_data='Heapsgfg2')],
                        [InlineKeyboardButton("Hashing", callback_data='Hashinggfg2'),
                         InlineKeyboardButton("Graphs", callback_data='Graphsgfg2')],
                        [InlineKeyboardButton("Advanced Data Structures", callback_data='Advanced Data Structuresgfg2'),
                         InlineKeyboardButton("Arrays", callback_data='Arraysgfg2')],
                        [InlineKeyboardButton("Matrix", callback_data='Matrixgfg2')]]
        elif val == "GATE.json":
            keyboard = [[InlineKeyboardButton("Operating Systems", callback_data='Operating Systemsgfg2'),
                         InlineKeyboardButton("Database Management Systems",
                                              callback_data='Database Management Systemsgfg2')],
                        [InlineKeyboardButton("Automata Theory", callback_data='Automata Theorygfg2'),
                         InlineKeyboardButton("Compilers", callback_data='Compilersgfg2')],
                        [InlineKeyboardButton("Computer Networks",
                                              callback_data='Computer Networksgfg2'),
                         InlineKeyboardButton("GATE Data Structures and Algorithms",
                                              callback_data='GATE Data Structures and Algorithmsgfg2')]]
        elif val == "Interview.json":
            keyboard = [[InlineKeyboardButton("Payu", callback_data='Payugfg2'),
                         InlineKeyboardButton("Adobe", callback_data='Adobegfg2')],
                        [InlineKeyboardButton("Amazon", callback_data='Amazongfg2'),
                         InlineKeyboardButton("Flipkart", callback_data='Flipkartgfg2')],
                        [InlineKeyboardButton("Google",
                                              callback_data='Googlegfg2'),
                         InlineKeyboardButton("Microsoft", callback_data='Microsoftgfg2')],
                        [InlineKeyboardButton("Snapdeal", callback_data='Snapdealgfg2'),
                         InlineKeyboardButton("Zopper-Com", callback_data='Zopper-Comgfg2')],
                        [InlineKeyboardButton("Yahoo", callback_data='Yahoogfg2'),
                         InlineKeyboardButton("Cisco", callback_data='Ciscogfg2')],
                        [InlineKeyboardButton("Facebook", callback_data='Facebookgfg2'),
                         InlineKeyboardButton("Yatra.Com", callback_data='Yatra.Comgfg2')],
                        [InlineKeyboardButton("Symantec", callback_data='Symantecgfg2'),
                         InlineKeyboardButton("Myntra", callback_data='Myntragfg2')],
                        [InlineKeyboardButton("Groupon", callback_data='Groupongfg2'),
                         InlineKeyboardButton("Belzabar", callback_data='Belzabargfg2')],
                        [InlineKeyboardButton("Paypal", callback_data='Paypalgfg2'),
                         InlineKeyboardButton("Akosha", callback_data='Akoshagfg2')],
                        [InlineKeyboardButton("Linkedin", callback_data='Linkedingfg2'),
                         InlineKeyboardButton("Browserstack", callback_data='Browserstackgfg2')],
                        [InlineKeyboardButton("Makemytrip", callback_data='Makemytripgfg2'),
                         InlineKeyboardButton("Infoedge", callback_data='Infoedgegfg2')],
                        [InlineKeyboardButton("Practo", callback_data='Practogfg2'),
                         InlineKeyboardButton("Housing-Com", callback_data='Housing-Comgfg2')],
                        [InlineKeyboardButton("Ola-Cabs", callback_data='Ola-Cabsgfg2'),
                         InlineKeyboardButton("Grofers", callback_data='Grofersgfg2')],
                        [InlineKeyboardButton("Thoughtworks", callback_data='Thoughtworksgfg2'),
                         InlineKeyboardButton("Delhivery", callback_data='Delhiverygfg2')],
                        [InlineKeyboardButton("Taxi4Sure", callback_data='Taxi4Suregfg2'),
                         InlineKeyboardButton("Lenskart", callback_data='Lenskartgfg2')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(text="Please select", reply_markup=reply_markup, chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        return GFG2

    # FUNCTION TO SHOW SUBMENU 2
    @staticmethod
    def gfg2(bot, update, user_data):
        query = update.callback_query
        val = query.data
        val = str(val).replace("gfg2", "")
        if val == "Advanced Data Structures":
            keyboard = [[InlineKeyboardButton("Advanced Lists", callback_data='Advanced Listsgfg3'),
                         InlineKeyboardButton("Trie", callback_data='Triegfg3')],
                        [InlineKeyboardButton("Suffix Array and Suffix Tree",
                                              callback_data='Suffix Array and Suffix Treegfg3'),
                         InlineKeyboardButton("AVL Tree", callback_data='AVL Treegfg3')],
                        [InlineKeyboardButton("Splay Tree",
                                              callback_data='Splay Treegfg3'),
                         InlineKeyboardButton("B Tree", callback_data='B Treegfg3')],
                        [InlineKeyboardButton("Segment Tree", callback_data='Segment Treegfg3'),
                         InlineKeyboardButton("Red Black Tree", callback_data='Red Black Treegfg3')],
                        [InlineKeyboardButton("K Dimensional Tree", callback_data='K Dimensional Treegfg3'),
                         InlineKeyboardButton("Others", callback_data='Othersgfg3')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.edit_message_text(text="Please select", reply_markup=reply_markup, chat_id=query.message.chat_id,
                                  message_id=query.message.message_id)
            return GFG3
        else:
            try:
                with open("geeks_for_geeks/"+user_data['gfg'], encoding='utf-8') as data_file:
                    data = json.load(data_file)
                se = data[val]
                s = ""
                s1 = ""
                a = 0
                for i in se:
                    a = a + 1
                    if a <= 50:
                        s = s + '<a href="' + se[i] + '">' + i + '</a>\n\n'
                    else:
                        s1 = s1 + '<a href="' + se[i] + '">' + i + '</a>\n\n'
                bot.edit_message_text(text=val + "\n\n" + s, chat_id=query.message.chat_id,
                                      message_id=query.message.message_id, parse_mode=ParseMode.HTML)
                if len(s1) != 0:
                    bot.send_message(text=val + "\n\n" + s1, chat_id=query.message.chat_id, parse_mode=ParseMode.HTML)
            except:
                return ConversationHandler.END
            user_data.clear()
            return ConversationHandler.END

    # FUNCTION TO SHOW SUBMENU 3
    @staticmethod
    def gfg3(bot, update, user_data):
        query = update.callback_query
        try:
            val = query.data
            val = str(val).replace("gfg3", "")
            with open("geeks_for_geeks/"+user_data['gfg'], encoding='utf-8') as data_file:
                data = json.load(data_file)
            se = data["Advanced Data Structures"][val]
            s = ""
            for i in se:
                s = s + '<a href="' + se[i] + '">' + i + '</a>\n\n'
            bot.edit_message_text(text=val + "\n\n" + s, chat_id=query.message.chat_id,
                                  message_id=query.message.message_id, parse_mode=ParseMode.HTML)
        except:
            return ConversationHandler.END
        user_data.clear()
        return ConversationHandler.END
