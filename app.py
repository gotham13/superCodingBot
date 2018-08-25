"""
Created by Gotham on 31-07-2018.
"""
import logging
import helper
import json
import requests
import os
from apscheduler.schedulers.background import BackgroundScheduler
from telegram.error import Unauthorized
from queue import Queue
from threading import Thread
from telegram import Bot
from telegram.ext import Dispatcher, CommandHandler, ConversationHandler, Updater, MessageHandler, Filters
from configparser import ConfigParser
import bs4 as bs
import time
import sqlite3
from handlers import codeforces, codechef, register, compiler, \
    competitions, unregister, ques_of_the_day, ranklist, \
    update_rank_list, geeks_for_geeks, admin
import random
import flood_protection
from utility import Utility

sched = BackgroundScheduler()
timeouts = flood_protection.Spam_settings()


# CONNECTING TO SQLITE DATABASE AND CREATING TABLES
class SuperCodingBot:
    def __init__(self):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        self.CF = 20000
        self.db = "coders1.db"
        self.logger = logging.getLogger(__name__)
        self.config = ConfigParser()
        self.config.read("config.ini")
        self.bot_token = self.config.get('telegram', 'bot_token')
        self.hr_api_key = self.config.get('hackerrank', 'api_key')
        self.clist_user_name = self.config.get('clist', 'username')
        self.clist_api_key = self.config.get('clist', 'api_key')
        self.mount_point = self.config.get('openshift', 'persistent_mount_point')
        self.utility = Utility(self.mount_point)
        self.compiler = helper.HackerRankAPI(api_key=self.hr_api_key)
        self.admin_list = str(self.config.get('telegram', 'admin_chat_id')).split(',')
        self.fallback = CommandHandler('cancel', self.cancel, pass_user_data=True)
        self.cf = codeforces.CfHandler(mount_point=self.mount_point, fallback=self.fallback)
        self.bot = Bot(self.bot_token)
        self.cc_questions = {"easy": None,
                             "hard": None,
                             "medium": None,
                             "school": None,
                             "challenge": None,
                             "peer": None}
        self.init_db()
        self.cc = codechef.CcHandler(cc_dict=self.cc_questions, fallback=self.fallback)
        self.register = register.RegHandler(mount_point=self.mount_point, fallback=self.fallback)
        self.compiler = compiler.ComHandler(api_key=self.hr_api_key, fallback=self.fallback)
        self.competitions = competitions.Competitions(clist_api_key=self.clist_api_key,
                                                      clist_user_name=self.clist_user_name,
                                                      mount_point=self.mount_point, bot=self.bot,
                                                      fallback=self.fallback)
        self.unregister = unregister.UnregHandler(mount_point=self.mount_point, fallback=self.fallback)
        self.ques_of_the_day = ques_of_the_day.QuesHandler(mount_point=self.mount_point, fallback=self.fallback)
        self.ranklist = ranklist.RankListHandler(mount_point=self.mount_point, fallback=self.fallback)
        self.update = update_rank_list.UpdateHandler(mount_point=self.mount_point, fallback=self.fallback)
        self.geeks_for_geeks = geeks_for_geeks.GeeksForGeeksHandler(fallback=self.fallback)
        self.admin = admin.AdminHandle(mount_point=self.mount_point, admin_list=self.admin_list, fallback=self.fallback)
        self.update_fun()
        self.update_fun("codechef")
        self.conv_handler = ConversationHandler(
            entry_points=[CommandHandler('sendcf', self.getCf)],
            allow_reentry=True,
            states={
                self.CF: [MessageHandler(Filters.document, self.receive_cf)]
            },
            fallbacks=[self.fallback]
        )

    def init_db(self):
        conn = sqlite3.connect(self.mount_point + self.db)
        create_table_request_list = [
            'CREATE TABLE handles(id TEXT PRIMARY KEY,name TEXT,HE TEXT,HR TEXT,CF TEXT,SP TEXT,CC TEXT)',
            'CREATE TABLE  datas(id TEXT PRIMARY KEY,name TEXT,HE TEXT,HR TEXT,CF TEXT,SP TEXT,CC TEXT)',
            'CREATE TABLE  priority(id TEXT PRIMARY KEY,HE TEXT,HR TEXT,CF TEXT,CC TEXT)',
            'CREATE TABLE subscribers(id TEXT PRIMARY KEY,BEGINNER int DEFAULT 0,'
            'EASY int DEFAULT 0,MEDIUM int DEFAULT 0,'
            'HARD int DEFAULT 0,CHALLENGE int DEFAULT 0,PEER int DEFAULT 0,A int DEFAULT 0,B int DEFAULT 0,'
            'C int DEFAULT 0,D int DEFAULT 0,E int DEFAULT 0,F int DEFAULT 0,OTHERS int DEFAULT 0)',
        ]
        for create_table_request in create_table_request_list:
            try:
                conn.execute(create_table_request)
            except:
                pass
        conn.commit()
        conn.close()

    def get_ques_cc(self, type_of_ques):
        """
        :param type_of_ques: Type of question
        """
        i = 0
        while True:
            # TRYING 5 TIMES AS SOMETIMES IT GIVES URL ERROR IN ONE GO
            if i == 5:
                break
            try:
                response = requests.get("https://www.codechef.com/problems/easy/", headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)"
                                  " Chrome/47.0.2526.106 Safari/537.36"})
                soup = bs.BeautifulSoup(response.text, "html5lib")
                self.cc_questions[type_of_ques] = soup.find_all('a', {"title": "Submit a solution to this problem."})
                break
            except requests.exceptions.RequestException:
                i = i + 1
                continue

    # COMMAND HANDLER FUNCTION FOR /start COMMAND
    @staticmethod
    @timeouts.wrapper
    def start(bot, update):
        update.message.reply_text(
            'welcome!\nOnly one person can register through one telegram id\nHere are the commands\nEnter /cancel at any time to cancel operation\nEnter /randomcc to get a random question from codechef\nEnter /randomcf to get a random question from codeforces\nEnter /geeksforgeeks to get topics from geeks for geeks\nEnter /register to go to register menu to register your handle to the bot\nEnter /unregister to go to unregister menu to unregister from the bot\nEnter /ranklist to go to ranklist menu to get ranklist\nEnter /ongoing to get a list of ongoing competitions\nEnter /upcoming to get a list of upcoming competitions\nEnter /compiler to compile and run\nEnter /subscribe to get question of the day everyday\nEnter /unsubscribe to unsubscribe from question of the day\nEnter /update to initialise updating of your info\n Automatic updation of all data will take place every day\n To see all the commands enter /help any time.\n\nORIGINAL CREATOR @gotham13121997\nORIGINAL source code https://github.com/Gotham13121997/superCodingBot')

    # COMMAND HANDLER FUNCTION FOR /help COMMAND
    @staticmethod
    @timeouts.wrapper
    def help(bot, update):
        update.message.reply_text(
            'Only one person can register through one telegram id\nHere are the commands\nEnter /register to go to register menu to register your handle to the bot\nEnter /cancel at any time to cancel operation\nEnter /randomcc to get a random question from codechef\nEnter /randomcf to get a random question from codeforces\nEnter /geeksforgeeks to get topics from geeks for geeks\nEnter /unregister to go to unregister menu to unregister from the bot\nEnter /ranklist to go to ranklist menu to get ranklist\nEnter /ongoing to get a list of ongoing competitions\nEnter /upcoming to get a list of upcoming competitions\nEnter /compiler to compile and run\nEnter /subscribe to get question of the day everyday\nEnter /unsubscribe to unsubscribe from question of the day\nEnter /update to initialise updating of your info\n Automatic updation of all data will take place every day\n To see all the commands enter /help any time.\n\nORIGINAL CREATOR @gotham13121997\nORIGINAL source code https://github.com/Gotham13121997/superCodingBot')

    # COMMAND HANDLER FUNCTION FOR CANCELLING
    @staticmethod
    def cancel(bot, update, user_data):
        update.message.reply_text('Cancelled')
        user_data.clear()
        return ConversationHandler.END

    # FUNCTION FOR LOGGING ALL KINDS OF ERRORS
    @timeouts.wrapper
    def error_handler(self, bot, update, error):
        self.logger.warning('Update "%s" caused error "%s"' % (update, error))

    def update_fun(self, args=None):
        def updaters():
            global timeouts
            timeouts = flood_protection.Spam_settings()
            conn = sqlite3.connect(self.mount_point + 'coders1.db')
            c = conn.cursor()
            c.execute('SELECT id, HE, HR, CC, SP, CF FROM handles')
            self.utility.update_function(c)
            conn.commit()
            conn.close()
            for chat_id in self.admin_list:
                self.bot.send_message(chat_id=chat_id, text="Data updated")
                time.sleep(1)

        def update_cc():
            for key in self.cc_questions.keys():
                self.get_ques_cc(type_of_ques=key)
            self.cc.change_cc(self.cc_questions)

        def update_cf():
            response = requests.get("http://www.codeforces.com/problemset", headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)"
                              " Chrome/47.0.2526.106 Safari/537.36"})
            soup1 = bs.BeautifulSoup(response.text, 'html5lib')
            endpage = int(soup1.findAll('span', {"class": "page-index"})[-1].getText())
            latest = soup1.find('td', {"class": "id"}).text
            with open(self.mount_point + 'codeforces.json', 'r') as code_json:
                data = json.load(code_json)
                latest1 = data['latest']
                if latest1 == latest:
                    for chat_id in self.admin_list:
                        self.bot.send_message(chat_id=chat_id, text="Codeforces questions up to date")
                        time.sleep(1)
                    return
                else:
                    data['latest'] = latest
                    signal = True
                    for i in range(1, endpage + 1):
                        if not signal:
                            break
                        response = requests.get("http://www.codeforces.com/problemset/page/" + str(i), headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)"
                                          " Chrome/47.0.2526.106 Safari/537.36"})
                        soup = bs.BeautifulSoup(response.text, 'html5lib')
                        for s1 in soup.findAll('td', {"class": "id"}):
                            idcur = s1.text
                            s2 = s1.find('a')
                            if idcur == latest1:
                                signal = False
                                break
                            else:
                                save = "http://www.codeforces.com" + s2.get('href')
                                if 'A' in save:
                                    data['A'].append(save)
                                elif 'B' in save:
                                    data['B'].append(save)
                                elif 'C' in save:
                                    data['C'].append(save)
                                elif 'D' in save:
                                    data['D'].append(save)
                                elif 'E' in save:
                                    data['E'].append(save)
                                elif 'F' in save:
                                    data['F'].append(save)
                                else:
                                    data['OTHERS'].append(save)
            os.remove(self.mount_point + 'codeforces.json')
            with open(self.mount_point + 'codeforces.json', 'w') as code_json:
                json.dump(data, code_json)
            with open(self.mount_point + 'codeforces.json', 'r') as code_json:
                self.cf.change_cf(json.load(code_json))
            for chat_id in self.admin_list:
                self.bot.send_message(chat_id=chat_id, text="Questions updated codeforces")
                time.sleep(1)

        def sender():
            names = ['', 'BEGINNER', 'EASY', 'MEDIUM', 'HARD', 'CHALLENGE', 'PEER', 'A', 'B', 'C', 'D', 'E', 'F',
                     'OTHERS']
            nscc = "https://www.codechef.com/problems/" + random.choice(self.cc_questions['school']).text
            necc = "https://www.codechef.com/problems/" + random.choice(self.cc_questions['easy']).text
            nmcc = "https://www.codechef.com/problems/" + random.choice(self.cc_questions['medium']).text
            nhcc = "https://www.codechef.com/problems/" + random.choice(self.cc_questions['hard']).text
            nccc = "https://www.codechef.com/problems/" + random.choice(self.cc_questions['challenge']).text
            npcc = "https://www.codechef.com/problems/" + random.choice(self.cc_questions['peer']).text
            nAcf = self.cf.get_random_ques('A')
            nBcf = self.cf.get_random_ques('B')
            nCcf = self.cf.get_random_ques('C')
            nDcf = self.cf.get_random_ques('D')
            nEcf = self.cf.get_random_ques('E')
            nFcf = self.cf.get_random_ques('F')
            nOTHERScf = self.cf.get_random_ques('OTHERS')
            questions = ['', nscc, necc, nmcc, nhcc, nccc, npcc, nAcf, nBcf, nCcf, nDcf, nEcf, nFcf, nOTHERScf]
            conn = sqlite3.connect(self.mount_point + 'coders1.db')
            c = conn.cursor()
            c.execute("SELECT  * FROM subscribers")
            for row in c.fetchall():
                chat_id = row[0]
                try:
                    for k in range(1, len(row)):
                        if k <= 6:
                            site = 'codechef'
                        else:
                            site = 'codeforces'
                        if row[k] == 1:
                            if not questions[k] is None:
                                self.bot.send_message(
                                    text="Random " + names[k] + " question from " + site + "\n\n" + questions[k],
                                    chat_id=chat_id)
                        time.sleep(1)
                except Unauthorized:
                    c.execute("DELETE FROM subscribers WHERE id = (?)", (chat_id,))
                except:
                    pass
            c.close()
            conn.commit()
            conn.close()

        if args is None:
            sched.add_job(func=update_cf, trigger='cron', day_of_week='sat-sun', hour=18, minute=30)
            sched.add_job(func=update_cc, trigger='cron', day_of_week='sat-sun', hour=18, minute=30)
            sched.add_job(func=sender, trigger='cron', hour=0, minute=0)
            sched.add_job(func=updaters, trigger='cron', hour=18, minute=30)
            sched.start()
        elif args == "codechef":
            update_cc()
        elif args == "codeforces":
            update_cf()
        elif args == "rating":
            updaters()

    @timeouts.wrapper_for_class_methods
    def adminupdate(self, bot, update):
        if not str(update.message.chat_id) in self.admin_list:
            update.message.reply_text("sorry you are not an admin")
            return
        self.update_fun("rating")

    # ADMIN COMMAND HANDLER FUNCTION TO UPDATE ALL THE QUESTIONS WHEN HE WANTS
    @timeouts.wrapper_for_class_methods
    def admqupd(self, bot, update):
        if not str(update.message.chat_id) in self.admin_list:
            update.message.reply_text("sorry you are not an admin")
            return
        self.update_fun("codechef")
        for chat_id in self.admin_list:
            bot.send_message(chat_id=chat_id, text="Questions updated codechef")
            time.sleep(1)
        self.update_fun("codeforces")

    # START OF ADMIN CONVERSATION HANDLER TO REPLACE THE CODEFORCES JSON
    @timeouts.wrapper_for_class_methods
    def getCf(self, bot, update):
        if not str(update.message.chat_id) in self.admin_list:
            update.message.reply_text("sorry you are not an admin")
            return ConversationHandler.END
        update.message.reply_text("send your json file")
        return self.CF

    def receive_cf(self, bot, update):
        file_id = update.message.document.file_id
        newFile = bot.get_file(file_id)
        newFile.download(self.mount_point + 'codeforces.json')
        update.message.reply_text("saved")
        with open(self.mount_point + 'codeforces.json', 'r') as code_json:
            self.cf.change_cf(json.load(code_json))
        return ConversationHandler.END

    # END OF ADMIN CONVERSATION HANDLER TO REPLACE THE CODEFORCES JSON

    def setup(self, webhook_url=None):
        """If webhook_url is not passed, run with long-polling."""
        logging.basicConfig(level=logging.WARNING)
        if webhook_url:
            self.bot = Bot(self.bot_token)
            update_queue = Queue()
            dp = Dispatcher(self.bot, update_queue)
        else:
            updater = Updater(self.bot_token)
            self.bot = updater.bot
            dp = updater.dispatcher
            dp.add_handler(CommandHandler('help', self.help))
            dp.add_handler(CommandHandler('start', self.start))
            dp.add_handler(CommandHandler('ongoing', self.competitions.ongoing))
            dp.add_handler(CommandHandler('givememydb', self.admin.givememydb))
            dp.add_handler(CommandHandler('getcfjson', self.admin.getcfjson))
            dp.add_handler(CommandHandler('adminhandle', self.admin.adminhandle))
            dp.add_handler(CommandHandler('adminud', self.adminupdate))
            dp.add_handler(CommandHandler('adminuq', self.admqupd))
            dp.add_handler(self.cf.conv_handler10)
            dp.add_handler(self.cc.conv_handler)
            dp.add_handler(self.competitions.conv_handler)
            dp.add_handler(self.competitions.conv_handler1)
            dp.add_handler(self.register.conv_handler)
            dp.add_handler(self.compiler.conv_handler)
            dp.add_handler(self.unregister.conv_handler)
            dp.add_handler(self.ques_of_the_day.conv_handler)
            dp.add_handler(self.ques_of_the_day.conv_handler1)
            dp.add_handler(self.ranklist.conv_handler)
            dp.add_handler(self.update.conv_handler)
            dp.add_handler(self.geeks_for_geeks.conv_handler)
            dp.add_handler(self.admin.conv_handler1)
            dp.add_handler(self.admin.conv_handler2)
            dp.add_handler(self.conv_handler)
            # log all errors
            dp.add_error_handler(self.error_handler)
        if webhook_url:
            self.bot.set_webhook(webhook_url=webhook_url)
            thread = Thread(target=dp.start, name='dispatcher')
            thread.start()
            return update_queue, self.bot
        else:
            self.bot.set_webhook()  # Delete webhook
            updater.start_polling()
            updater.idle()


if __name__ == "__main__":
    sb = SuperCodingBot()
    sb.setup()
