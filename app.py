import logging
import helper
import json
from datetime import datetime, timedelta
import os
import sys
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from queue import Queue
from telegram import ReplyKeyboardRemove
from telegram import ReplyKeyboardMarkup
from threading import Thread
from telegram import ParseMode
from telegram import Bot
from telegram.ext import Dispatcher, CommandHandler, ConversationHandler, MessageHandler, RegexHandler, Updater,Filters,CallbackQueryHandler
from configparser import ConfigParser
import bs4 as bs
import html5lib
import time
import urllib.error
import urllib.request
from urllib import parse
import sqlite3
import random
from xlsxwriter.workbook import Workbook

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
config = ConfigParser()
config.read('config.ini')
TOKEN = config.get('telegram','bot_token')
HACKERRANK_API_KEY = config.get('hackerrank','api_key')
CLIST_USER_NAME = config.get('clist','username')
CLIST_API_KEY = config.get('clist','api_key')
mount_point=config.get('openshift','persistent_mount_point')
compiler = helper.HackerRankAPI(api_key=HACKERRANK_API_KEY)
adminlist=str(config.get('telegram','admin_chat_id')).split(',')
# FOR CONVERSATION HANDLERS
NAME,JUDGE,HANDLE,SELECTION,HOLO,SOLO,POLO,XOLO,REMOVER,UPDA,QSELCC,LANG,CODE,DECODE,TESTCASES,RESULT,OTHER,FILE,FILETEST,GFG1,GFG2,GFG3,DB,CF,SCHED,REMNOTI,QSELCF,SUBSEL,SUBCC,SUBCF,UNSUB,MSG=range(32)
# CLASS FOR FLOOD PROTECTION
class Spam_settings:
    def __init__(self):
        self.limits = {1: 3, 5: 7, 10: 10, 15: 13, 30: 20}  # max: 3 updates in 1 second, 7 updates in 5 seconds etc
        self.timeout_start = 10
        self.timeout_factor = 5
        self.factors = {}
        self.timeouts = {}
        self.times = {}

    def new_message(self, chat_id):
        update_time = time.time()
        if chat_id not in self.timeouts:
            self.timeouts.update({chat_id: 0})
            self.times.update({chat_id: [update_time]})
            self.factors.update({chat_id: 1})
        else:
            if self.timeouts[chat_id] > update_time:
                return self.timeouts[chat_id] - update_time
            for limit in self.limits:
                amount = 1
                for n, upd_time in enumerate(self.times[chat_id]):
                    if update_time - upd_time < limit:
                        amount += 1
                    else:
                        if amount > self.limits[limit]:
                            self.timeouts[chat_id] = update_time + self.timeout_start * (self.factors[chat_id])
                            self.factors[chat_id] *= self.timeout_factor
                            text = "You are timeouted by the flood protection system of this bot. Try again in {0} seconds.".format(
                                self.timeouts[chat_id] - update_time)

                            return text
        self.times[chat_id].insert(0, update_time)
        return 0

    def wrapper(self, func):  # only works on functions, not on instancemethods
        def func_wrapper(bot, update, *args2):
            timeout = self.new_message(update.effective_chat.id)
            if not timeout:
               return func(bot, update, *args2)
            elif isinstance(timeout, str):
                print("timeout")
                # Only works for messages (+Commands) and callback_queries (Inline Buttons)
                if update.callback_query:
                    bot.edit_message_text(chat_id=update.effective_chat.id,
                                          message_id=update.effective_message.message_id,
                                          text=timeout)
                elif update.message:
                    bot.send_message(chat_id=update.effective_chat.id, text=timeout)

        return func_wrapper


timeouts = Spam_settings()


# CONNECTING TO SQLITE DATABASE AND CREATING TABLES
conn = sqlite3.connect(mount_point+'coders1.db')
create_table_request_list = [
    'CREATE TABLE handles(id TEXT PRIMARY KEY,name TEXT,HE TEXT,HR TEXT,CF TEXT,SP TEXT,CC TEXT)',
    'CREATE TABLE  datas(id TEXT PRIMARY KEY,name TEXT,HE TEXT,HR TEXT,CF TEXT,SP TEXT,CC TEXT)',
    'CREATE TABLE  priority(id TEXT PRIMARY KEY,HE TEXT,HR TEXT,CF TEXT,CC TEXT)',
    'CREATE TABLE subscribers(id TEXT PRIMARY KEY,CC int DEFAULT 0,CF int DEFAULT 0,CCSEL TEXT,CFSEL TEXT)',
]
for create_table_request in create_table_request_list:
    try:
        conn.execute(create_table_request)
    except:
        pass
conn.commit()
conn.close()

if  os.path.exists(mount_point+'codeforces.json'):
  with open(mount_point+'codeforces.json', 'r') as codeforces:
     qcf = json.load(codeforces)

# GETTING QUESTIONS FROM CODECHEF WEBSITE
# STORING THEM ACCORDING TO THE TAG EASY,MEDIUM,HARD,BEGINNER,CHALLENGE
# STORING TITLE OF QUESTIONS AND THEIR CODE IN SEPERATE LISTS
i = 0
while (True):
    # TRYING 5 TIMES AS SOMETIMES IT GIVES URL ERROR IN ONE GO
    if i == 5:
        break
    try:
        reqcce = urllib.request.Request("https://www.codechef.com/problems/easy/", headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"})
        reqccs = urllib.request.Request("https://www.codechef.com/problems/school/", headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"})
        reqccm = urllib.request.Request("https://www.codechef.com/problems/medium/", headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"})
        reqcch = urllib.request.Request("https://www.codechef.com/problems/hard/", headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"})
        reqccc = urllib.request.Request("https://www.codechef.com/problems/challenge/", headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"})
        concce = urllib.request.urlopen(reqcce)
        soupcce = bs.BeautifulSoup(concce, "html5lib")
        scce = soupcce.find_all('div', {"class": "problemname"})
        s1cce = soupcce.find_all('a', {"title": "Submit a solution to this problem."})
        conccs = urllib.request.urlopen(reqccs)
        soupccs = bs.BeautifulSoup(conccs, "html5lib")
        sccs = soupccs.find_all('div', {"class": "problemname"})
        s1ccs = soupccs.find_all('a', {"title": "Submit a solution to this problem."})
        conccm = urllib.request.urlopen(reqccm)
        soupccm = bs.BeautifulSoup(conccm, "html5lib")
        sccm = soupccm.find_all('div', {"class": "problemname"})
        s1ccm = soupccm.find_all('a', {"title": "Submit a solution to this problem."})
        concch = urllib.request.urlopen(reqcch)
        soupcch = bs.BeautifulSoup(concch, "html5lib")
        scch = soupcch.find_all('div', {"class": "problemname"})
        s1cch = soupcch.find_all('a', {"title": "Submit a solution to this problem."})
        conccc = urllib.request.urlopen(reqccc)
        soupccc = bs.BeautifulSoup(conccc, "html5lib")
        sccc = soupccc.find_all('div', {"class": "problemname"})
        s1ccc = soupccc.find_all('a', {"title": "Submit a solution to this problem."})
        break
    except urllib.error.URLError:
        i = i + 1
        continue


# COMMAND HANDLER FUNCTION FOR /start COMMAND
@timeouts.wrapper
def start(bot, update):
    update.message.reply_text(
        'welcome!\nOnly one person can register through one telegram id\nHere are the commands\nEnter /cancel at any time to cancel operation\nEnter /randomcc to get a random question from codechef\nEnter /randomcf to get a random question from codeforces\nEnter /geeksforgeeks to get topics from geeks for geeks\nEnter /register to go to register menu to register your handle to the bot\nEnter /unregister to go to unregister menu to unregister from the bot\nEnter /ranklist to go to ranklist menu to get ranklist\nEnter /ongoing to get a list of ongoing competitions\nEnter /upcoming to get a list of upcoming competitions\nEnter /compiler to compile and run\nEnter /subscribe to get question of the day everyday\nEnter /unsubscribe to unsubscribe from question of the day\nEnter /update to initialise updating of your info\n Automatic updation of all data will take place every day\n To see all the commands enter /help any time.\n\nORIGINAL CREATOR @gotham13121997\nORIGINAL source code https://github.com/Gotham13121997/superCodingBot')


# COMMAND HANDLER FUNCTION FOR /help COMMAND
@timeouts.wrapper
def help(bot, update):
    update.message.reply_text(
        'Only one person can register through one telegram id\nHere are the commands\nEnter /register to go to register menu to register your handle to the bot\nEnter /cancel at any time to cancel operation\nEnter /randomcc to get a random question from codechef\nEnter /randomcf to get a random question from codeforces\nEnter /geeksforgeeks to get topics from geeks for geeks\nEnter /unregister to go to unregister menu to unregister from the bot\nEnter /ranklist to go to ranklist menu to get ranklist\nEnter /ongoing to get a list of ongoing competitions\nEnter /upcoming to get a list of upcoming competitions\nEnter /compiler to compile and run\nEnter /subscribe to get question of the day everyday\nEnter /unsubscribe to unsubscribe from question of the day\nEnter /update to initialise updating of your info\n Automatic updation of all data will take place every day\n To see all the commands enter /help any time.\n\nORIGINAL CREATOR @gotham13121997\nORIGINAL source code https://github.com/Gotham13121997/superCodingBot')


# FUNCTION FOR LOGGING ALL KINDS OF ERRORS
def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


# START OF CONVERSATION HANDLER FOR GETTING RANDOM QUESTION FROM CODEFORCES
# FUNCTION TO GET INPUT ABOUT THE TYPE OF QUESTION FROM USER
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
def qselcf(bot, update):
    query = update.callback_query
    val = query.data
    if val == 'Acf1':
        n = random.randint(0, len(qcf['A']) - 1)
        strn = qcf['A'][n]
    elif val == 'Bcf1':
        n = random.randint(0, len(qcf['B']) - 1)
        strn = qcf['B'][n]
    elif val == 'Ccf1':
        n = random.randint(0, len(qcf['C']) - 1)
        strn = qcf['C'][n]
    elif val == 'Dcf1':
        n = random.randint(0, len(qcf['D']) - 1)
        strn = qcf['D'][n]
    elif val == 'Ecf1':
        n = random.randint(0, len(qcf['E']) - 1)
        strn = qcf['E'][n]
    elif val == 'Fcf1':
        n = random.randint(0, len(qcf['F']) - 1)
        strn = qcf['F'][n]
    elif val=='OTHERScf1':
        n = random.randint(0, len(qcf['OTHERS']) - 1)
        strn = qcf['OTHERS'][n]
    val=str(val).replace("cf1","")
    bot.edit_message_text(
        text="Random " + val + " question from codeforces\n\n" + strn,
        chat_id=query.message.chat_id,
        message_id=query.message.message_id)
    return ConversationHandler.END
# END OF CONVERSATION HANDLER FOR GETTING RANDOM QUESTION FROM CODEFORCES


# START OF CONVERSATION HANDLER FOR GETTING RANDOM QUESTION FROM CODECHEF
# FUNCTION TO GET INPUT ABOUT THE TYPE OF QUESTION FROM USER
@timeouts.wrapper
def randomcc(bot, update):
    keyboard = [[InlineKeyboardButton("Beginner", callback_data='BEGINNERcc1'),
                 InlineKeyboardButton("Easy", callback_data='EASYcc1')],
                [InlineKeyboardButton("Medium", callback_data='MEDIUMcc1'),
                 InlineKeyboardButton("Hard", callback_data='HARDcc1')],
                [InlineKeyboardButton("Challenge", callback_data='CHALLENGEcc1')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please select the type of question', reply_markup=reply_markup)
    return QSELCC


# FUNCTION FOR SENDING THE RANDOM QUESTION TO USER ACCORDING TO HIS CHOICE
def qselcc(bot, update):
    global scce, s1cce, scch, s1cch, sccm, s1ccm, sccs, s1ccs, sccc, s1ccc
    query = update.callback_query
    val = query.data
    if val == 'BEGINNERcc1':
        n = random.randint(0, len(sccs) - 1)
        strt = sccs[n].text.strip("\n\n ")
        strn = s1ccs[n].text
    if val == 'EASYcc1':
        n = random.randint(0, len(scce) - 1)
        strt = scce[n].text.strip("\n\n ")
        strn = s1cce[n].text
    if val == 'MEDIUMcc1':
        n = random.randint(0, len(sccm) - 1)
        strt = sccm[n].text.strip("\n\n ")
        strn = s1ccm[n].text
    if val == 'HARDcc1':
        n = random.randint(0, len(scch) - 1)
        strt = scch[n].text.strip("\n\n ")
        strn = s1cch[n].text
    if val == 'CHALLENGEcc1':
        n = random.randint(0, len(sccc) - 1)
        strt = sccc[n].text.strip("\n\n ")
        strn = s1ccc[n].text
    val=str(val).replace("cc1","")
    bot.edit_message_text(
        text="Random " + val + " question from codechef\n\n" + strt + "\n" + "https://www.codechef.com/problems/" + strn,
        chat_id=query.message.chat_id,
        message_id=query.message.message_id)
    return ConversationHandler.END


# END OF CONVERSATION HANDLER FOR GETTING RANDOM QUESTION FROM CODECHEF


# START OF CONVERSATION HANDLER FOR REGISTERING THE USERS HANDLES
@timeouts.wrapper
def register(bot, update):
    markup = ReplyKeyboardRemove()
    update.message.reply_text('Hi,please enter your name ', reply_markup=markup)
    return NAME


# FUNCTION FOR GETTING THE NAME AND ASKING ABOUT WHICH JUDGE USER WANTS TO REGISTER THEIR HANDLE FOR
def name(bot, update, user_data):
    user_data['name'] = update.message.text.upper()
    # THIS IS HOW AN INLINE KEYBOARD IS MADE AND USED
    keyboard = [[InlineKeyboardButton("Hackerearth", callback_data='HEreg1'),
                 InlineKeyboardButton("Hackerrank", callback_data='HRreg1')],
                [InlineKeyboardButton("Codechef", callback_data='CCreg1'),
                 InlineKeyboardButton("Spoj", callback_data='SPreg1')],
                [InlineKeyboardButton("Codeforces", callback_data='CFreg1')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('please enter the online judge you want to setup with  the bot',
                              reply_markup=reply_markup)
    return JUDGE


# FUNCTION FOR GETTING THE ONLINE JUDGE AND ASKING FOR HANDLE
def judge(bot, update, user_data):
    # AND THIS IS HOW WE GET THE CALLBACK DATA WHEN INLINE KEYBOARD KEY IS PRESSED
    query = update.callback_query
    choices=['HEreg1','HRreg1','CFreg1','CCreg1','SPreg1']
    if query.data not in choices:
        return ConversationHandler.END
    user_data['code'] = str(query.data).replace("reg1","")
    bot.edit_message_text(text='please enter your handle eg. gotham13121997',
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)
    return HANDLE


# FUNCTION FOR GETTING THE HANDLE AND REGISTERING IT IN DATABASE
# ALL THE MAGIC BEGINS HERE
def handle(bot, update, user_data):
    user = str(update.message.from_user.id)
    handle1 = update.message.text
    name1 = user_data['name']
    code1 = user_data['code']
    if code1 == 'HE':
        # IF HACKEREARTH
        opener = urllib.request.build_opener()
        # SCRAPING DATA FROM WEBPAGE
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        try:
            sauce = opener.open('https://www.hackerearth.com/@' + handle1)
            print('used')
            soup = bs.BeautifulSoup(sauce, 'html5lib')
            stri = "HACKEREARTH\n"
            for i in soup.find_all('a', {"href": "/users/" + handle1 + "/activity/hackerearth/#user-rating-graph"}):
                stri = stri + i.text + "\n"
            for i in soup.find_all('a', {"href": "/@" + handle1 + "/followers/"}):
                stri = stri + i.text + "\n"
            for i in soup.find_all('a', {"href": "/@" + handle1 + "/following/"}):
                stri = stri + i.text + "\n"
            vals = stri
        except urllib.error.URLError as e:
            # IF URL NOT FOUND THE ID IS WRONG
            update.message.reply_text('wrong id')
            user_data.clear()
            return ConversationHandler.END
    elif code1 == 'HR':
        # IF HACKERRANK
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        try:
            sauce = opener.open('https://www.hackerrank.com/' + handle1 + '?hr_r=1')
            soup = bs.BeautifulSoup(sauce, 'html5lib')
            try:
                soup.find('script', {"id": "initialData"}).text
            except AttributeError:
                update.message.reply_text('wrong id')
                user_data.clear()
                return ConversationHandler.END
            # I HAVE NO IDEA WHAT I HAVE DONE HERE
            # BUT IT SEEMS TO WORK
            s = soup.find('script', {"id": "initialData"}).text
            i = s.find("hacker_id", s.find("hacker_id", s.find("hacker_id") + 1) + 1)
            i = parse.unquote(s[i:i + 280]).replace(",", ">").replace(":", " ").replace("{", "").replace("}",
                                                                                                         "").replace(
                '"', "").split(">")
            s1 = "HACKERRANK\n"
            for j in range(1, 10):
                s1 = s1 + i[j] + "\n"
            vals = s1
        except urllib.error.URLError as e:
            update.message.reply_text('wrong id')
            user_data.clear()
            return ConversationHandler.END
    elif code1 == 'CC':
        # IF CODECHEF
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        try:
            sauce = opener.open('https://www.codechef.com/users/' + handle1)
            soup = bs.BeautifulSoup(sauce, 'html5lib')
            try:
                soup.find('a', {"href": "http://www.codechef.com/ratings/all"}).text
            except AttributeError:
                update.message.reply_text('wrong id')
                user_data.clear()
                return ConversationHandler.END
            try:
                s1 = soup.find('span', {"class": "rating"}).text + "\n"
            except AttributeError:
                s1 = ""
            s = "CODECHEF" + "\n" + s1 + "rating: " + soup.find('a', {
                "href": "http://www.codechef.com/ratings/all"}).text + "\n" + soup.find('div', {
                "class": "rating-ranks"}).text.replace(" ", "").replace("\n\n", "").strip('\n')
            vals = s
        except urllib.error.URLError as e:
            update.message.reply_text('wrong id')
            user_data.clear()
            return ConversationHandler.END
    elif code1 == 'SP':
        # IF SPOJ
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        try:
            sauce = opener.open('http://www.spoj.com/users/' + handle1 + '/')
            soup = bs.BeautifulSoup(sauce, 'html5lib')
            try:
                soup.find('div', {"class": "col-md-3"}).text
            except AttributeError:
                update.message.reply_text('wrong id')
                user_data.clear()
                return ConversationHandler.END
            s = soup.find('div', {"class": "col-md-3"}).text.strip('\n\n').replace("\t", "").split('\n')
            s = s[3].strip().split(":")
            s = "SPOJ\n" + s[0] + "\n" + s[1].strip(" ") + "\n" + soup.find('dl', {
                "class": "dl-horizontal profile-info-data profile-info-data-stats"}).text.replace("\t", "").replace(
                "\xa0", "").strip('\n')
            vals = s
        except urllib.error.URLError as e:
            update.message.reply_text('wrong id')
            user_data.clear()
            return ConversationHandler.END
    elif code1 == 'CF':
        # IF CODEFORCES
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        try:
            sauce = opener.open('http://codeforces.com/profile/' + handle1)
            soup = bs.BeautifulSoup(sauce, 'html5lib')
            try:
                soup.find('img', {"alt": "User\'\'s contribution into Codeforces community"}).text
            except AttributeError:
                update.message.reply_text('wrong id')
                user_data.clear()
                return ConversationHandler.END
            s = soup.find_all('span', {"style": "font-weight:bold;"})
            if len(s) == 0:
                s2 = ""
            else:
                s2 = "contest rating: " + s[0].text + "\n" + "max: " + s[1].text + s[2].text + "\n"
            s1 = "CODEFORCES\n" + s2 + "contributions: " + soup.find('img', {"alt": "User\'\'s contribution into Codeforces community"}).nextSibling.nextSibling.text
            vals = s1
        except urllib.error.URLError as e:
            update.message.reply_text('wrong id')
            user_data.clear()
            return ConversationHandler.END
    else:
        return ConversationHandler.END
    # CONNECTING TO DATABASE
    conn = sqlite3.connect(mount_point+'coders1.db')
    c = conn.cursor()
    # STORING THE PROFILE INFO IN datas TABLE
    # STORING HANDLES IN handles TABLE
    c.execute("INSERT OR IGNORE INTO datas (id, name, " + code1 + ") VALUES (?, ?, ?)", (user, name1, vals))
    c.execute("INSERT OR IGNORE INTO handles (id, name, " + code1 + ") VALUES (?, ?, ?)", (user, name1, handle1))
    if c.rowcount == 0:
        c.execute("UPDATE datas SET " + code1 + " = (?) , name= (?) WHERE id = (?) ", (vals, name1, user))
        c.execute("UPDATE handles SET " + code1 + " = (?) , name= (?) WHERE id = (?) ", (handle1, name1, user))
    if code1=='HE':
        try:
            rat=vals.split('\n')
            if(rat[1]=="Rating"):
                rat2=rat[2].strip(" ").strip("\n")
                c.execute("INSERT OR IGNORE INTO priority (id, HE) VALUES(?, ?)", (user, rat2))
                if(c.rowcount==0):
                    c.execute("UPDATE  priority SET HE = (?) WHERE id = (?) ", (rat2, user))
        except:
            pass
    elif code1=='HR':
        try:
            rat=vals.split('\n')
            rat2=rat[1].split(" ")[1].strip(" ").strip("\n")
            c.execute("INSERT OR IGNORE INTO priority (id, HR) VALUES(?, ?)", (user, rat2))
            if (c.rowcount == 0):
                c.execute("UPDATE  priority SET HR = (?) WHERE id = (?) ", (rat2, user))
        except:
            pass
    elif code1=='CF':
        try:
            rat=vals.split("\n")
            if "contest rating:"in rat[1]:
                rat2=rat[1].split(" ")[2].strip(" ").strip("\n")
                c.execute("INSERT OR IGNORE INTO priority (id, CF) VALUES(?, ?)", (user, rat2))
                if (c.rowcount == 0):
                    c.execute("UPDATE  priority SET CF = (?) WHERE id = (?) ", (rat2, user))
        except:
            pass
    elif code1=='CC':
        try:
            rat=vals.split("\n")
            if not "rating" in rat[1]:
                rat2=rat[2].split(" ")[1].strip(" ").strip("\n")
                c.execute("INSERT OR IGNORE INTO priority (id, CC) VALUES(?, ?)", (user, rat2))
                if (c.rowcount == 0):
                    c.execute("UPDATE  priority SET CC = (?) WHERE id = (?) ", (rat2, user))
        except:
            pass
    elif code1=='SP':
        c.execute("INSERT OR IGNORE INTO priority (id) VALUES(?)", (user,))

    conn.commit()
    # BELOW LINES ARE USED TO CREATE XLMX FILES OF ALL SORTS OF RANKLIST
    # SO WHEN USER ASKS FOR RANKLIST THERE IS NO DELAY
    workbook = Workbook(mount_point+'all.xlsx')
    worksheet = workbook.add_worksheet()
    format = workbook.add_format()
    format.set_align('top')
    format.set_text_wrap()
    mysel = c.execute("SELECT datas.name, datas.HE, datas.HR, datas.SP, datas.CF, datas.CC FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority.CF AS FLOAT) DESC, CAST(priority.CC AS FLOAT) DESC, CAST(priority.HR AS FLOAT) DESC, CAST(priority.HE AS FLOAT) DESC")
    for i, row in enumerate(mysel):
        for j, value in enumerate(row):
            worksheet.write(i, j, row[j], format)
            worksheet.set_row(i, 170)
    worksheet.set_column(0, 5, 40)
    workbook.close()
    workbook = Workbook(mount_point + code1 + ".xlsx")
    worksheet = workbook.add_worksheet()
    format = workbook.add_format()
    format.set_align('top')
    format.set_text_wrap()
    if(code1=='SP'):
        mysel = c.execute("SELECT name, " + code1 + " FROM datas")
        for i, row in enumerate(mysel):
            for j, value in enumerate(row):
                worksheet.write(i, j, row[j], format)
                worksheet.set_row(i, 170)
        worksheet.set_column(0, 5, 40)
        workbook.close()
    else:
        mysel = c.execute("SELECT datas.name, datas." + code1 + " FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority."+code1+" AS FLOAT) DESC")
        for i, row in enumerate(mysel):
            for j, value in enumerate(row):
                worksheet.write(i, j, row[j], format)
                worksheet.set_row(i, 170)
        worksheet.set_column(0, 5, 40)
        workbook.close()
    conn.close()
    update.message.reply_text("Succesfully Registered")
    update.message.reply_text(name1 + "    \n" + vals)
    user_data.clear()
    return ConversationHandler.END


# END OF CONVERSATION HANDLER FOR REGISTERING THE USERS HANDLES


# START OF CONVERSATION HANDLER FOR COMPILING AND RUNNING
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
def lang(bot, update, user_data):
    query = update.callback_query
    val = query.data
    val=str(val).replace("comp1","")
    if val == "other":
        # IF USER CHOOSES OTHER
        s1 = ""
        for i in compiler.supportedlanguages():
            s1 = s1 + i + ","
        bot.edit_message_text(text="enter the name of language\n" + s1, chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
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
def code(bot, update, user_data):
    query = update.callback_query
    val = query.data
    val=str(val).replace("so1","")
    if val == "code":
        bot.edit_message_text(text="please enter your code\nPlease make sure that the first line is not a comment line",
                              chat_id=query.message.chat_id, message_id=query.message.message_id)
        return DECODE
    elif val=="file":
        bot.edit_message_text(text="please send your .txt file\nMaximum size 2mb", chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        return FILE
    else:
        return ConversationHandler.END


# FUNCTION TO GET TESTCASE FILE
def filetest(bot, update, user_data):
    file_id = update.message.document.file_id
    file_id = update.message.document.file_id
    file_size = update.message.document.file_size
    if file_size > 2097152:
        update.message.reply_text("FILE SIZE GREATER THAN 2 MB")
        return ConversationHandler.END
    newFile = bot.get_file(file_id)
    newFile.download('test.txt')
    with open('test.txt', 'rt') as f:
        source = f.read()
    s1 = (str(user_data['code'])).replace("«", "<<").replace("»", ">>")
    result = compiler.run({'source': s1,
                           'lang': user_data['lang'],
                           'testcases': [source]
                           })
    output = result.output
    time1 = result.time
    memory1 = result.memory
    message1 = result.message
    if time1 is not None:
        time1 = time1[0]
    if memory1 is not None:
        memory1 = memory1[0]
    if output is not None:
        output = output[0]
    else:
        output = ""
    markup = ReplyKeyboardRemove()
    if (len(output) <= 2897):
        update.message.reply_text("Output:\n" + str(output) + "\n" + "Time: " + str(time1) + "\nMemory: " + str(
            memory1) + "\nMessage: " + str(message1), reply_markup=markup)
    else:
        with open("out.txt", "w") as text_file:
            text_file.write("Output:\n" + str(output) + "\n" + "Time: " + str(time1) + "\nMemory: " + str(
                memory1) + "\nMessage: " + str(message1))
        bot.send_document(chat_id=update.message.chat_id, document=open('out.txt', 'rb'), reply_markup=markup)
        os.remove('out.txt')
    user_data.clear()
    os.remove('test.txt')
    return ConversationHandler.END


# FUNCTION TO DOWNLOAD THE FILE SENT AND EXTRACT ITS CONTENTS
def filer(bot, update, user_data):
    file_id = update.message.document.file_id
    file_size=update.message.document.file_size
    if file_size > 2097152:
        update.message.reply_text("FILE SIZE GREATER THAN 2 MB")
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
def decode(bot, update, user_data):
    user_data['code'] = update.message.text
    custom_keyboard = [['#no test case', '#send a .txt file']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True, resize_keybord=True)
    update.message.reply_text(
        'Please send test cases together as you would do in online ide\nIf you dont want to provide test cases select #no test case\n I you want to send test cases as .txt file select #send a .txt file',
        reply_markup=reply_markup)
    return TESTCASES


# FUNCTION TO GET THE TEST CASES FROM THE USER
def testcases(bot, update, user_data):
    s = update.message.text
    markup = ReplyKeyboardRemove()
    if s == "#send a .txt file":
        update.message.reply_text("Please send your testcases as a .txt file\nMaximum size 2mb", reply_markup=markup)
        return FILETEST
    if s == "#no test case":
        # CONVERTING UNICODE CHARACTER TO DOUBLE GREATER THAN OR LESS THAN
        # WEIRD
        s1 = (str(user_data['code'])).replace("«", "<<").replace("»", ">>")
        # USING COMPILER FUNCTION FROM helper.py script
        result = compiler.run({'source': s1,
                               'lang': user_data['lang']
                               })
        # GETTING OUTPUT FROM result CLASS in helper.py script
        output = result.output
        time1 = result.time
        memory1 = result.memory
        message1 = result.message
        if time1 is not None:
            time1 = time1[0]
        if memory1 is not None:
            memory1 = memory1[0]
        if output is not None:
            output = output[0]
        else:
            output = ""
        if (len(output) <= 2897):
            update.message.reply_text("Output:\n" + str(output) + "\n" + "Time: " + str(time1) + "\nMemory: " + str(
                memory1) + "\nMessage: " + str(message1), reply_markup=markup)
        else:
            with open("out.txt", "w") as text_file:
                text_file.write("Output:\n" + str(output) + "\n" + "Time: " + str(time1) + "\nMemory: " + str(
                    memory1) + "\nMessage: " + str(message1))
            bot.send_document(chat_id=update.message.chat_id, document=open('out.txt', 'rb'), reply_markup=markup)
            os.remove('out.txt')
    else:
        # AGAIN THE SAME DRILL
        s1 = (str(user_data['code'])).replace("«", "<<").replace("»", ">>")
        result = compiler.run({'source': s1,
                               'lang': user_data['lang'],
                               'testcases': [s]
                               })
        output = result.output
        time1 = result.time
        memory1 = result.memory
        message1 = result.message
        if time1 is not None:
            time1 = time1[0]
        if memory1 is not None:
            memory1 = memory1[0]
        if output is not None:
            output = output[0]
        else:
            output = ""
        if (len(output) <= 2897):
            update.message.reply_text("Output:\n" + str(output) + "\n" + "Time: " + str(time1) + "\nMemory: " + str(
                memory1) + "\nMessage: " + str(message1), reply_markup=markup)
        else:
            with open("out.txt", "w") as text_file:
                text_file.write("Output:\n" + str(output) + "\n" + "Time: " + str(time1) + "\nMemory: " + str(
                    memory1) + "\nMessage: " + str(message1))
            bot.send_document(chat_id=update.message.chat_id, document=open('out.txt', 'rb'), reply_markup=markup)
            os.remove('out.txt')
    user_data.clear()
    return ConversationHandler.END


# FUNCTION FOR THE CASE WHERE USER HAD SELECTED OTHER
def other(bot, update, user_data):
    s = update.message.text
    user_data['lang'] = s
    keyboard = [[InlineKeyboardButton("Enter Source Code", callback_data='code'),
                 InlineKeyboardButton("Send a file", callback_data='file')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("please select", reply_markup=reply_markup)
    return CODE


# END OF CONVERSATION HANDLER FOR COMPILING AND RUNNING

# START OF CONVERSATION HANDLER FOR GEEKS FOR GEEKS
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
def gfg1(bot, update, user_data):
    query = update.callback_query
    val = query.data
    val=str(val).replace("gfg1","")
    val=val+".json"
    user_data['gfg'] = val
    if (val == "Algorithms.json"):
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
    elif (val == "DS.json"):
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
    elif (val == "GATE.json"):
        keyboard = [[InlineKeyboardButton("Operating Systems", callback_data='Operating Systemsgfg2'),
                     InlineKeyboardButton("Database Management Systems", callback_data='Database Management Systemsgfg2')],
                    [InlineKeyboardButton("Automata Theory", callback_data='Automata Theorygfg2'),
                     InlineKeyboardButton("Compilers", callback_data='Compilersgfg2')],
                    [InlineKeyboardButton("Computer Networks",
                                          callback_data='Computer Networksgfg2'),
                     InlineKeyboardButton("GATE Data Structures and Algorithms",
                                          callback_data='GATE Data Structures and Algorithmsgfg2')]]
    elif (val == "Interview.json"):
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
def gfg2(bot, update, user_data):
    query = update.callback_query
    val = query.data
    val=str(val).replace("gfg2","")
    if (val == "Advanced Data Structures"):
        keyboard = [[InlineKeyboardButton("Advanced Lists", callback_data='Advanced Listsgfg3'),
                     InlineKeyboardButton("Trie", callback_data='Triegfg3')],
                    [InlineKeyboardButton("Suffix Array and Suffix Tree", callback_data='Suffix Array and Suffix Treegfg3'),
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
            with open(user_data['gfg'], encoding='utf-8') as data_file:
                data = json.load(data_file)
            se = data[val]
            s = ""
            s1 = ""
            a = 0
            for i in se:
                a = a + 1
                if (a <= 50):
                    s = s + '<a href="' + se[i] + '">' + i + '</a>\n\n'
                else:
                    s1 = s1 + '<a href="' + se[i] + '">' + i + '</a>\n\n'
            bot.edit_message_text(text=val + "\n\n" + s, chat_id=query.message.chat_id,
                                  message_id=query.message.message_id, parse_mode=ParseMode.HTML)
            if (len(s1) != 0):
                bot.send_message(text=val + "\n\n" + s1, chat_id=query.message.chat_id, parse_mode=ParseMode.HTML)
        except:
            return ConversationHandler.END
        user_data.clear()
        return ConversationHandler.END


# FUNCTION TO SHOW SUBMENU 3
def gfg3(bot, update, user_data):
    query = update.callback_query
    try:
        val = query.data
        val=str(val).replace("gfg3","")
        with open(user_data['gfg'], encoding='utf-8') as data_file:
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


# END OF CONVERSATION HANDLER FOR GEEKS FOR GEEKS

# GLOBAL VARIABLES STORE THE PREVIOUS DATA TEMPORARILY IN CASE THE WEBPAGE IS BEING MAINTAINED
ong = ""
upc = ""


# COMMAND HANDLER FUNCTION TO SHOW LIST OF ONGOING COMPETITIONS
@timeouts.wrapper
def ongoing(bot, update):
    global ong
    # PARSING JSON
    date1 = update.message.date
    payload = {'limit': '15', 'start__lt': str(date1), 'end__gt': str(date1),
               'username': CLIST_USER_NAME, 'api_key': CLIST_API_KEY, 'format': 'json', 'order_by': 'end'}
    url = "https://clist.by/api/v1/contest/?"
    url = url + urllib.parse.urlencode(payload)
    opener = urllib.request.build_opener()
    opener.addheaders = [('Content-Type', 'application/json')]
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    rawData = opener.open(url).read().decode('utf-8')
    try:
        jsonData = json.loads(rawData)
        searchResults = jsonData['objects']
        s = ""
        i=0
        for er in searchResults:
            i=i+1
            if(i==16):
                break
            title = er['event']
            start = er['start']
            sec = timedelta(seconds=int(er['duration']))
            d = datetime(1, 1, 1) + sec
            duration = ("%d days %d hours %d min" % (d.day - 1, d.hour, d.minute))
            host = er['resource']['name']
            contest = er['href']
            start1 = time_converter(start, '+0530')
            s = s + title + "\n" + "Start:\n" + start.replace("T", " ") + " GMT\n" + str(
                start1).replace("T",
                                " ") + " IST\n" + "Duration:" + duration + "\n" + host + "\n" + contest + "\n\n"
        ong = s
        update.message.reply_text(s)
    except:
        update.message.reply_text(ong)


# FUNCTION TO CONVERT TIME FROM UTC TO OTHER TIME ZONE
def time_converter(old_time, time_zone):
    time_zone = float(time_zone[:3] + ('.5' if time_zone[3] == '3' else '.0'))
    str_time = datetime.strptime(old_time, "%Y-%m-%dT%H:%M:%S")
    return (str_time + timedelta(hours=time_zone)).strftime("%Y-%m-%dT%H:%M:%S")


# START OF CONVERSTION HANDLER  TO SHOW A LIST OF UPCOMING COMPETITIONS AND GET REMINDERS
@timeouts.wrapper
def upcoming(bot, update):
    global upc
    # PARSING JSON
    date1=update.message.date
    payload={'limit':'15','start__gt':str(date1),'order_by':'start','username':CLIST_USER_NAME,'api_key':CLIST_API_KEY,'format':'json'}
    url="https://clist.by/api/v1/contest/?"
    url=url+urllib.parse.urlencode(payload)
    opener = urllib.request.build_opener()
    opener.addheaders = [('Content-Type', 'application/json')]
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    rawData = opener.open(url).read().decode('utf-8')
    try:
        jsonData = json.loads(rawData)
        searchResults = jsonData['objects']
        i = 0
        s = ""
        keyboard=[]
        keyboard1=[]
        for er in searchResults:
            i = i + 1
            # LIMITING NO OF EVENTS TO 20
            if i == 16:
                break
            title = er['event']
            start = er['start']
            sec = timedelta(seconds=int(er['duration']))
            d = datetime(1, 1, 1) + sec
            duration = ("%d days %d hours %d min" % (d.day - 1, d.hour, d.minute))
            host = er['resource']['name']
            contest = er['href']
            start1 = time_converter(start, '+0530')
            keyboard1.append(InlineKeyboardButton(str(i), callback_data=str(i)))
            s = s + str(i) + ". " + title + "\n" + "Start:\n" + start.replace("T", " ") + " GMT\n" + str(
                start1).replace("T",
                                " ") + " IST\n" + "Duration: " + str(duration) + "\n" + host + "\n" + contest + "\n\n"
            if i%5==0:
                keyboard.append(keyboard1)
                keyboard1 = []
        keyboard.append(keyboard1)
        upc = searchResults
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(s + "Select competition number to get notification" + "\n\n",
                                  reply_markup=reply_markup)
    except:
        i = 0
        s = ""
        keyboard = []
        keyboard1 = []
        for er in upc:
            i = i + 1
            # LIMITING NO OF EVENTS TO 20
            if i == 16:
                break
            title = er['event']
            start = er['start']
            sec = timedelta(seconds=int(er['duration']))
            d = datetime(1, 1, 1) + sec
            duration = ("%d days %d hours %d min %d sec" % (d.day - 1, d.hour, d.minute, d.second))
            host = er['resource']['name']
            contest = er['href']
            start1 = time_converter(start, '+0530')
            keyboard1.append(InlineKeyboardButton(str(i), callback_data=str(i)))
            s = s + str(i) + ". " + title + "\n" + "Start:\n" + start.replace("T", " ") + " GMT\n" + str(
                start1).replace("T",
                                " ") + " IST\n" + "Duration: " + str(duration) + "\n" + host + "\n" + contest + "\n\n"
            if i%5==0:
                keyboard.append(keyboard1)
                keyboard1 = []
        keyboard.append(keyboard1)
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(s + "\n\n" + "Select competition number to get notification",
                                  reply_markup=reply_markup)
    return SCHED


jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///'+mount_point+'coders1.db')
}
schedule = BackgroundScheduler(jobstores=jobstores)
schedule.start()


# FUNCTION TO SET REMINDER
def remind(bot, update):
    query = update.callback_query
    msg = query.data
    if str(msg).isdigit():
        msg = int(msg) - 1
        start1 = time_converter(upc[msg]['start'], '-0030')
        dateT = str(upc[msg]['start']).replace("T", " ").split(" ")
        start1 = start1.replace("T", " ").split(" ")
        date = dateT[0].split("-")
        date1 = start1[0].split("-")
        time1 = start1[1].split(":")
        schedule.add_job(remindmsgDay, 'cron', year=date[0], month=date[1], day=date[2], replace_existing=True,
                         id=str(query.message.chat_id) + str(upc[msg]['id']) + "0",
                         args=[str(query.message.chat_id),
                               str(upc[msg]['event']) + "\n" + str(upc[msg]['href'])])
        schedule.add_job(remindmsg, 'cron', year=date1[0], month=date1[1], day=date1[2], hour=time1[0], minute=time1[0],
                         replace_existing=True,
                         id=str(query.message.chat_id) + str(upc[msg]['id']) + "1",
                         args=[str(query.message.chat_id),
                               str(upc[msg]['event'] + "\n" + str(upc[msg]['href']))])
        bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,
                              text="I will remind you about " + upc[msg]['event']+"\nYou can use command /dontremindme to cancel reminder")
        if query.message.chat_id<0:
            bot.send_message(chat_id=query.message.chat_id,text="I detected this is a group. The reminder will be sent to the group. If you want to get reminder personally then use this command in private message")
    return ConversationHandler.END


# WHAT HAPPENSWHEN REMINDER IS DEPLOYED
def remindmsgDay(chatId, message):
    bot = Bot(TOKEN)
    bot.send_message(chat_id=chatId, text="You have a contest today\n " + message)


def remindmsg(chatId, message):
    bot = Bot(TOKEN)
    bot.send_message(chat_id=chatId, text="Your contest starts in half an hour\n " + message)


# END OF CONVERSTION HANDLER  TO SHOW A LIST OF UPCOMING COMPETITIONS AND GET REMINDERS

# START OF CONVERSATION HANDLER TO REMOVE REMINDERS
@timeouts.wrapper
def removeRemind(bot, update ):
    cid = update.message.chat_id
    conn = sqlite3.connect(mount_point+'coders1.db')
    c = conn.cursor()
    c.execute("SELECT id FROM apscheduler_jobs WHERE id LIKE  " + "'" + str(
        update.message.chat_id) + "%' AND id LIKE " + "'%0'")
    if (c.fetchone()):
        c.execute("SELECT id FROM apscheduler_jobs WHERE id LIKE  " + "'" + str(
            update.message.chat_id) + "%' AND id LIKE " + "'%0'")
        a = c.fetchall()
        keyboard=[]
        for i in range(0, len(a)):
            s =str(a[i]).replace("('", "").replace("',)", "").replace(
                '("', "").replace('",)', "")
            print(s)
            keyboard.append([InlineKeyboardButton(str(schedule.get_job(job_id=s).args[1].split("\n")[0]), callback_data=s[:-1]+"notiplz")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Here are your pending reminders\nSelect the reminder you want to remove",reply_markup=reply_markup)
        c.close()
        return REMNOTI
    else:
        c.close()
        update.message.reply_text("You have no pending reminders")
        return ConversationHandler.END


def remnoti(bot, update):
    query=update.callback_query
    val =str(query.data).replace("notiplz", "")
    schedule.remove_job(val + "0")
    schedule.remove_job(val + "1")
    bot.edit_message_text(text="Reminder removed", message_id=query.message.message_id,
                          chat_id=query.message.chat_id)
    return ConversationHandler.END


# END OF CONVERSATION HANDLER TO REMOVE REMINDERS

# START OF CONVERSATION HANDLER FOR UNREGISTERING
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
def remover(bot, update):
    query = update.callback_query
    val = query.data
    val=str(val).replace("rem2","")
    conn = sqlite3.connect(mount_point+'coders1.db')
    c = conn.cursor()
    a = str(query.from_user.id)
    c.execute("SELECT id FROM handles WHERE id=(?)", (a,))
    if not c.fetchone():
        bot.edit_message_text(text='You are not registered to the bot. Please register using /register command',
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
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
        workbook = Workbook(mount_point+"HE.xlsx")
        worksheet = workbook.add_worksheet()
        format = workbook.add_format()
        format.set_align('top')
        format.set_text_wrap()
        mysel = c.execute("SELECT datas.name, datas.HE FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority.HE AS FLOAT) DESC")
        for i, row in enumerate(mysel):
            for j, value in enumerate(row):
                worksheet.write(i, j, row[j], format)
                worksheet.set_row(i, 170)
        worksheet.set_column(0, 5, 40)
        workbook.close()
        workbook = Workbook(mount_point+"HR.xlsx")
        worksheet = workbook.add_worksheet()
        format = workbook.add_format()
        format.set_align('top')
        format.set_text_wrap()
        mysel = c.execute(
            "SELECT datas.name, datas.HR FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority.HR AS FLOAT) DESC")
        for i, row in enumerate(mysel):
            for j, value in enumerate(row):
                worksheet.write(i, j, row[j], format)
                worksheet.set_row(i, 170)
        worksheet.set_column(0, 5, 40)
        workbook.close()
        workbook = Workbook(mount_point+"SP.xlsx")
        worksheet = workbook.add_worksheet()
        format = workbook.add_format()
        format.set_align('top')
        format.set_text_wrap()
        mysel = c.execute("SELECT name, SP FROM datas")
        for i, row in enumerate(mysel):
            for j, value in enumerate(row):
                worksheet.write(i, j, row[j], format)
                worksheet.set_row(i, 170)
        worksheet.set_column(0, 5, 40)
        workbook.close()
        workbook = Workbook(mount_point+"CF.xlsx")
        worksheet = workbook.add_worksheet()
        format = workbook.add_format()
        format.set_align('top')
        format.set_text_wrap()
        mysel = c.execute(
            "SELECT datas.name, datas.CF FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority.CF AS FLOAT) DESC")
        for i, row in enumerate(mysel):
            for j, value in enumerate(row):
                worksheet.write(i, j, row[j], format)
                worksheet.set_row(i, 170)
        worksheet.set_column(0, 5, 40)
        workbook.close()
        workbook = Workbook(mount_point+"CC.xlsx")
        worksheet = workbook.add_worksheet()
        format = workbook.add_format()
        format.set_align('top')
        format.set_text_wrap()
        mysel = c.execute(
            "SELECT datas.name, datas.CC FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority.CC AS FLOAT) DESC")
        for i, row in enumerate(mysel):
            for j, value in enumerate(row):
                worksheet.write(i, j, row[j], format)
                worksheet.set_row(i, 170)
        worksheet.set_column(0, 5, 40)
        workbook.close()
    else:
        c.execute("SELECT "+val+" FROM handles WHERE id=(?)", (a,))
        for row in c:
            if row[0] is None or row[0]=="":
                bot.edit_message_text(text='You are not registered to the bot. Please register using /register command',
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id)
                conn.close()
                return ConversationHandler.END
        # OTHER WISE REMOVING THE PARTICULAR ENTRY
        c.execute("UPDATE datas SET " + val + " = (?)  WHERE id = (?) ", ("", a))
        c.execute("UPDATE handles SET " + val + " = (?)  WHERE id = (?) ", ("", a))
        if not val=='SP':
            c.execute("UPDATE priority SET " + val + " = (?)  WHERE id = (?) ", ("", a))
        conn.commit()
        bot.edit_message_text(text='Unregistering please wait',
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        c.execute("SELECT name, " + val + " FROM datas")
        # RECREATING XLSX FILE
        workbook = Workbook(mount_point + val + ".xlsx")
        worksheet = workbook.add_worksheet()
        format = workbook.add_format()
        format.set_align('top')
        format.set_text_wrap()
        mysel = c.execute(
            "SELECT datas.name, datas." +val + " FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority." + val + " AS FLOAT) DESC")
        for i, row in enumerate(mysel):
            for j, value in enumerate(row):
                worksheet.write(i, j, row[j], format)
                worksheet.set_row(i, 170)
        worksheet.set_column(0, 5, 40)
        workbook.close()
    c.execute("SELECT HE, HR, SP, CF, CC FROM handles WHERE id =(?)",(a,))
    count=0
    for row in c:
        for i in row:
            if i is None or i == "":
                count=count+1
    if count==5:
        c.execute("DELETE FROM datas WHERE id = (?)", (a,))
        c.execute("DELETE FROM handles WHERE id = (?)", (a,))
        c.execute("DELETE FROM priority WHERE id = (?)", (a,))
        conn.commit()
    workbook = Workbook(mount_point+'all.xlsx')
    worksheet = workbook.add_worksheet()
    format = workbook.add_format()
    format.set_align('top')
    format.set_text_wrap()
    mysel = c.execute("SELECT datas.name, datas.HE, datas.HR, datas.SP, datas.CF, datas.CC FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority.CF AS FLOAT) DESC, CAST(priority.CC AS FLOAT) DESC, CAST(priority.HR AS FLOAT) DESC, CAST(priority.HE AS FLOAT) DESC")
    for i, row in enumerate(mysel):
        for j, value in enumerate(row):
            worksheet.write(i, j, row[j], format)
            worksheet.set_row(i, 170)
    worksheet.set_column(0, 5, 40)
    workbook.close()
    bot.send_message(chat_id=query.message.chat_id, text="Successfully unregistered")
    conn.commit()
    conn.close()
    return ConversationHandler.END


# END OF CONVERSATION HANDLER FOR UNREGISTERING


sched = BackgroundScheduler()


# FUNCTION FOR UPDATING ALL THE QUESTIONS FROM CODECHEF
# SCHEDULED TO AUTOMATICALLY HAPPEN AT 18:30 GMT WHICH IS 0:0 IST
@sched.scheduled_job('cron', day_of_week='sat-sun', hour=18, minute=30)
def qupd():
    global reqccc, reqcce, reqcch, reqccm, reqccs, conccc, concce, concch, conccm, conccs, scce, s1cce, scch, s1cch, sccm, s1ccm, sccs, s1ccs, sccc, s1ccc, soupccc, soupcce, soupcch, soupccm, soupccs
    try:
        reqcce = urllib.request.Request("https://www.codechef.com/problems/easy/", headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"})
        reqccs = urllib.request.Request("https://www.codechef.com/problems/school/", headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"})
        reqccm = urllib.request.Request("https://www.codechef.com/problems/medium/", headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"})
        reqcch = urllib.request.Request("https://www.codechef.com/problems/hard/", headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"})
        reqccc = urllib.request.Request("https://www.codechef.com/problems/challenge/", headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"})
        concce = urllib.request.urlopen(reqcce)
        soupcce = bs.BeautifulSoup(concce, "html5lib")
        scce = soupcce.find_all('div', {"class": "problemname"})
        s1cce = soupcce.find_all('a', {"title": "Submit a solution to this problem."})
        conccs = urllib.request.urlopen(reqccs)
        soupccs = bs.BeautifulSoup(conccs, "html5lib")
        sccs = soupccs.find_all('div', {"class": "problemname"})
        s1ccs = soupccs.find_all('a', {"title": "Submit a solution to this problem."})
        conccm = urllib.request.urlopen(reqccm)
        soupccm = bs.BeautifulSoup(conccm, "html5lib")
        sccm = soupccm.find_all('div', {"class": "problemname"})
        s1ccm = soupccm.find_all('a', {"title": "Submit a solution to this problem."})
        concch = urllib.request.urlopen(reqcch)
        soupcch = bs.BeautifulSoup(concch, "html5lib")
        scch = soupcch.find_all('div', {"class": "problemname"})
        s1cch = soupcch.find_all('a', {"title": "Submit a solution to this problem."})
        conccc = urllib.request.urlopen(reqccc)
        soupccc = bs.BeautifulSoup(conccc, "html5lib")
        sccc = soupccc.find_all('div', {"class": "problemname"})
        s1ccc = soupccc.find_all('a', {"title": "Submit a solution to this problem."})
        bot = Bot(TOKEN)
        for chatids in adminlist:
            bot.send_message(chat_id=chatids, text="Questions updated codechef")
    except urllib.error.URLError:
        pass


# FUNCTION FOR UPDATING ALL THE QUESTIONS FROM CODEFORCES
# SCHEDULED TO AUTOMATICALLY HAPPEN AT 18:30 GMT WHICH IS 0:0 IST
@sched.scheduled_job('cron', day_of_week='sat-sun', hour=18, minute=30)
def updateCf():
    global qcf
    bot = Bot(TOKEN)
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    source1 = opener.open("http://www.codeforces.com/problemset")
    soup1 = bs.BeautifulSoup(source1, 'html5lib')
    endpage = int(soup1.findAll('span', {"class": "page-index"})[-1].getText())
    latest = soup1.find('td', {"class": "id"}).text
    with open(mount_point+'codeforces.json', 'r') as codeforces:
        data = json.load(codeforces)
        latest1 = data['latest']
        if latest1 == latest:
            return
        else:
            data['latest'] = latest
            signal = True
            for i in range(1, endpage + 1):
                if signal == False:
                    for chatids in adminlist:
                        bot.send_message(chat_id=chatids, text="Codeforces questions up to date")
                    break
                source = opener.open("http://www.codeforces.com/problemset/page/" + str(i))
                soup = bs.BeautifulSoup(source, 'html5lib')
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
    os.remove(mount_point+'codeforces.json')
    with open(mount_point+'codeforces.json', 'w') as codeforces:
        json.dump(data, codeforces)
    with open(mount_point+'codeforces.json', 'r') as codeforces:
        qcf = json.load(codeforces)
    for chatids in adminlist:
        bot.send_message(chat_id=chatids, text="Questions updated codeforces")


# FUNCTION FOR UPDATING ALL THE DETAILS IN DATAS TABLE
# SCHEDULED TO AUTOMATICALLY HAPPEN AT 18:30 GMT WHICH IS 0:0 IST
@sched.scheduled_job('cron', hour=18, minute=30)
def updaters():
    global timeouts
    timeouts = Spam_settings()
    conn = sqlite3.connect(mount_point+'coders1.db')
    c = conn.cursor()
    c.execute('SELECT id, HE, HR, CC, SP, CF FROM handles')
    for row in c.fetchall():
        a = ""
        he = ""
        hr = ""
        sp = ""
        cc = ""
        cf = ""
        for wo in range(0, 6):
            if wo == 0:
                a = row[wo]
            elif wo == 1 and (row[wo] != '' and row[wo] is not None):
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                try:
                    sauce = opener.open('https://www.hackerearth.com/@' + str(row[wo]))
                    soup = bs.BeautifulSoup(sauce, 'html5lib')
                    stri = "HACKEREARTH\n"
                    for i in soup.find_all('a', {
                        "href": "/users/" + str(row[wo]) + "/activity/hackerearth/#user-rating-graph"}):
                        stri = stri + i.text + "\n"
                    for i in soup.find_all('a', {"href": "/@" + str(row[wo]) + "/followers/"}):
                        stri = stri + i.text + "\n"
                    for i in soup.find_all('a', {"href": "/@" + str(row[wo]) + "/following/"}):
                        stri = stri + i.text + "\n"
                    he = stri
                except urllib.error.URLError as e:
                    pass
            elif wo == 2 and (row[wo] != '' and row[wo] is not None):
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                try:
                    sauce = opener.open('https://www.hackerrank.com/' + str(row[wo]) + '?hr_r=1')
                    soup = bs.BeautifulSoup(sauce, 'html5lib')
                    try:
                        soup.find('script', {"id": "initialData"}).text
                        s = soup.find('script', {"id": "initialData"}).text
                        i = s.find("hacker_id", s.find("hacker_id", s.find("hacker_id") + 1) + 1)
                        i = parse.unquote(s[i:i + 280]).replace(",", ">").replace(":", " ").replace("{", "").replace(
                            "}",
                            "").replace(
                            '"', "").split(">")
                        s1 = "HACKERRANK\n"
                        for j in range(1, 10):
                            s1 = s1 + i[j] + "\n"
                        hr = s1
                    except AttributeError:
                        pass
                except urllib.error.URLError as e:
                    pass
            elif wo == 3 and (row[wo] != '' and row[wo] is not None):
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                count=0
                while(count<5):
                    try:
                        sauce = opener.open('https://www.codechef.com/users/' + str(row[wo]))
                        soup = bs.BeautifulSoup(sauce, 'html5lib')
                        try:
                            soup.find('a', {"href": "http://www.codechef.com/ratings/all"}).text
                            try:
                                s1 = soup.find('span', {"class": "rating"}).text + "\n"
                            except AttributeError:
                                s1 = ""
                            s = "CODECHEF" + "\n" + s1 + "rating: " + soup.find('a', {
                                "href": "http://www.codechef.com/ratings/all"}).text + "\n" + soup.find('div', {
                                "class": "rating-ranks"}).text.replace(" ", "").replace("\n\n", "").strip('\n')
                            cc = s
                            break
                        except AttributeError:
                            break
                    except urllib.error.URLError as e:
                        count=count+1
                        continue
            elif wo == 4 and (row[wo] != '' and row[wo] is not None):
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                try:
                    sauce = opener.open('http://www.spoj.com/users/' + str(row[wo]) + '/')
                    soup = bs.BeautifulSoup(sauce, 'html5lib')
                    try:
                        soup.find('div', {"class": "col-md-3"}).text
                        s = soup.find('div', {"class": "col-md-3"}).text.strip('\n\n').replace("\t", "").split('\n')
                        s = s[3].strip().split(":")
                        s = "SPOJ\n" + s[0] + "\n" + s[1].strip(" ") + "\n" + soup.find('dl', {
                            "class": "dl-horizontal profile-info-data profile-info-data-stats"}).text.replace("\t",
                                                                                                              "").replace(
                            "\xa0", "").strip('\n')
                        sp = s
                    except AttributeError:
                        pass
                except urllib.error.URLError as e:
                    pass
            elif wo == 5 and (row[wo] != '' and row[wo] is not None):
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                try:
                    sauce = opener.open('http://codeforces.com/profile/' + str(row[wo]))
                    soup = bs.BeautifulSoup(sauce, 'html5lib')
                    try:
                        soup.find('img', {"alt": "User\'\'s contribution into Codeforces community"}).text
                        s = soup.find_all('span', {"style": "font-weight:bold;"})
                        if len(s) == 0:
                            s2 = ""
                        else:
                            s2 = "contest rating: " + s[0].text + "\n" + "max: " + s[1].text + s[2].text + "\n"
                        s1 = "CODEFORCES\n" + s2 + "contributions: " + soup.find('img', {"alt": "User\'\'s contribution into Codeforces community"}).nextSibling.nextSibling.text
                        cf = s1
                    except AttributeError:
                        pass
                except urllib.error.URLError as e:
                    pass
        if not he == '' or (he == '' and (row[1] == '' or row[1] is None)):
            c.execute("UPDATE datas SET HE=(?) WHERE id=(?)", (he,str(a)))
            try:
                rat = he.split('\n')
                if (rat[1] == "Rating"):
                    rat2 = rat[2].strip(" ").strip("\n")
                    c.execute("UPDATE  priority SET HE = (?) WHERE id = (?) ", (rat2, str(a)))
            except:
                pass
        if not hr == '' or (hr == '' and (row[2] == '' or row[2] is None)):
            c.execute("UPDATE datas SET HR=(?) WHERE id=(?)", (hr,str(a)))
            try:
                rat = hr.split('\n')
                rat2 = rat[1].split(" ")[1].strip(" ").strip("\n")
                c.execute("UPDATE  priority SET HR = (?) WHERE id = (?) ", (rat2, str(a)))
            except:
                pass
        if not cf == '' or (cf == '' and (row[5] == '' or row[5] is None)):
            c.execute("UPDATE datas SET CF=(?) WHERE id=(?)", (cf,str(a)))
            try:
                rat = cf.split("\n")
                if "contest rating:" in rat[1]:
                    rat2 = rat[1].split(" ")[2].strip(" ").strip("\n")
                    c.execute("UPDATE  priority SET CF = (?) WHERE id = (?) ", (rat2, str(a)))
            except:
                pass
        if not cc == '' or (cc == '' and (row[3] == '' or row[3] is None)):
            c.execute("UPDATE datas SET CC=(?) WHERE id=(?)", (cc,str(a)))
            try:
                rat = cc.split("\n")
                if not "rating" in rat[1]:
                    rat2 = rat[2].split(" ")[1].strip(" ").strip("\n")
                    c.execute("UPDATE  priority SET CC = (?) WHERE id = (?) ", (rat2, str(a)))
            except:
                pass
        if not sp == '' or (sp == '' and (row[4] == '' or row[4] is None)):
            c.execute("UPDATE datas SET SP=(?) WHERE id=(?)", (sp,str(a)))
    # RECREATING ALL THE XLSX FILES
    workbook = Workbook(mount_point + "HE.xlsx")
    worksheet = workbook.add_worksheet()
    format = workbook.add_format()
    format.set_align('top')
    format.set_text_wrap()
    mysel = c.execute(
        "SELECT datas.name, datas.HE FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority.HE AS FLOAT) DESC")
    for i, row in enumerate(mysel):
        for j, value in enumerate(row):
            worksheet.write(i, j, row[j], format)
            worksheet.set_row(i, 170)
    worksheet.set_column(0, 5, 40)
    workbook.close()
    workbook = Workbook(mount_point + "HR.xlsx")
    worksheet = workbook.add_worksheet()
    format = workbook.add_format()
    format.set_align('top')
    format.set_text_wrap()
    mysel = c.execute(
        "SELECT datas.name, datas.HR FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority.HR AS FLOAT) DESC")
    for i, row in enumerate(mysel):
        for j, value in enumerate(row):
            worksheet.write(i, j, row[j], format)
            worksheet.set_row(i, 170)
    worksheet.set_column(0, 5, 40)
    workbook.close()
    workbook = Workbook(mount_point + "SP.xlsx")
    worksheet = workbook.add_worksheet()
    format = workbook.add_format()
    format.set_align('top')
    format.set_text_wrap()
    mysel = c.execute("SELECT name, SP FROM datas")
    for i, row in enumerate(mysel):
        for j, value in enumerate(row):
            worksheet.write(i, j, row[j], format)
            worksheet.set_row(i, 170)
    worksheet.set_column(0, 5, 40)
    workbook.close()
    workbook = Workbook(mount_point + "CF.xlsx")
    worksheet = workbook.add_worksheet()
    format = workbook.add_format()
    format.set_align('top')
    format.set_text_wrap()
    mysel = c.execute(
        "SELECT datas.name, datas.CF FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority.CF AS FLOAT) DESC")
    for i, row in enumerate(mysel):
        for j, value in enumerate(row):
            worksheet.write(i, j, row[j], format)
            worksheet.set_row(i, 170)
    worksheet.set_column(0, 5, 40)
    workbook.close()
    workbook = Workbook(mount_point + "CC.xlsx")
    worksheet = workbook.add_worksheet()
    format = workbook.add_format()
    format.set_align('top')
    format.set_text_wrap()
    mysel = c.execute(
        "SELECT datas.name, datas.CC FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority.CC AS FLOAT) DESC")
    for i, row in enumerate(mysel):
        for j, value in enumerate(row):
            worksheet.write(i, j, row[j], format)
            worksheet.set_row(i, 170)
    worksheet.set_column(0, 5, 40)
    workbook.close()
    workbook = Workbook(mount_point+'all.xlsx')
    worksheet = workbook.add_worksheet()
    format = workbook.add_format()
    format.set_align('top')
    format.set_text_wrap()
    mysel = c.execute(
        "SELECT datas.name, datas.HE, datas.HR, datas.SP, datas.CF, datas.CC FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority.CF AS FLOAT) DESC, CAST(priority.CC AS FLOAT) DESC, CAST(priority.HR AS FLOAT) DESC, CAST(priority.HE AS FLOAT) DESC")
    for i, row in enumerate(mysel):
        for j, value in enumerate(row):
            worksheet.write(i, j, row[j], format)
            worksheet.set_row(i, 170)
    worksheet.set_column(0, 5, 40)
    workbook.close()
    conn.commit()
    conn.close()
    bot = Bot(TOKEN)
    for chatids in adminlist:
        bot.send_message(chat_id=chatids, text="Data updated")


# START OF CONVERSATION HANDLER TO SUBSCRIBE TO QUESTION OF THE DAY
@timeouts.wrapper
def subscribe(bot,update):
    if update.message.chat_id<0:
        update.message.reply_text("I detected this is a group\nIf you subscribe here I will send questions to the group\nTo get questions to yourself subscribe to me in personal message")
    keyboard = [[InlineKeyboardButton("CODEFORCES", callback_data='CFsub3'),
                 InlineKeyboardButton("CODECHEF", callback_data='CCsub3')]]
    reply_markup=InlineKeyboardMarkup(keyboard)
    bot.send_message(text="Please select the website to which you wish to subscribe for getting question of the day",chat_id=update.message.chat_id,reply_markup=reply_markup)
    return SUBSEL

def subsel(bot,update):
    query=update.callback_query
    val=query.data
    if val=='CCsub3':
        keyboard = [[InlineKeyboardButton("Beginner", callback_data='BEGINNERcc2'),
                     InlineKeyboardButton("Easy", callback_data='EASYcc2')],
                    [InlineKeyboardButton("Medium", callback_data='MEDIUMcc2'),
                     InlineKeyboardButton("Hard", callback_data='HARDcc2')],
                    [InlineKeyboardButton("Challenge", callback_data='CHALLENGEcc2')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(chat_id=query.message.chat_id,message_id=query.message.message_id,text="Please select",reply_markup=reply_markup)
        return SUBCC
    elif val=='CFsub3':
        keyboard = [[InlineKeyboardButton("A", callback_data='Acf2'),
                     InlineKeyboardButton("B", callback_data='Bcf2'), InlineKeyboardButton("C", callback_data='Ccf2')],
                    [InlineKeyboardButton("D", callback_data='Dcf2'),
                     InlineKeyboardButton("E", callback_data='Ecf2'), InlineKeyboardButton("F", callback_data='Fcf2')],
                    [InlineKeyboardButton("OTHERS", callback_data='OTHERScf2')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text="Please select",reply_markup=reply_markup)
        return SUBCF


def subcc(bot,update):
    conn = sqlite3.connect(mount_point+'coders1.db')
    query = update.callback_query
    val = query.data
    val=str(val).replace("cc2","")
    a=str(query.message.chat_id)
    c=conn.cursor()
    c.execute("INSERT OR IGNORE INTO subscribers (id,CC,CCSEL) VALUES (?, ?, ?)", (a,1,val))
    if c.rowcount == 0:
        c.execute("UPDATE subscribers SET CC = (?) , CCSEL= (?) WHERE id = (?) ", (1, val, a))
    conn.commit()
    conn.close()
    bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text="I will send you a question of type "+val+" everyday from codechef \nyou can use command /unsubscribe to unsubscribe ")
    return ConversationHandler.END


def subcf(bot,update):
    conn = sqlite3.connect(mount_point+'coders1.db')
    query = update.callback_query
    val = query.data
    val=str(val).replace("cf2","")
    a=str(query.message.chat_id)
    c=conn.cursor()
    c.execute("INSERT OR IGNORE INTO subscribers (id,CF,CFSEL) VALUES (?, ?, ?)", (a,1,val))
    if c.rowcount == 0:
        c.execute("UPDATE subscribers SET CF = (?) , CFSEL= (?) WHERE id = (?) ", (1, val, a))
    conn.commit()
    conn.close()
    bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text="I will send you a question of type "+val+" everyday from codeforces \nyou can use command /unsubscribe to unsubscribe ")
    return ConversationHandler.END
# END OF CONVERSATION HANDLER TO SUBSCRIBE TO QUESTION OF THE DAY


# START OF CONVERSATION HANDLER TO UNSUBSCRIBE FROM QUESTION OF THE DAY
@timeouts.wrapper
def unsubsel(bot,update):
    conn = sqlite3.connect(mount_point+'coders1.db')
    c = conn.cursor()
    c.execute("SELECT id FROM subscribers WHERE id=(?)", (str(update.message.chat_id),))
    if not c.fetchone():
        update.message.reply_text("You have not subscribed for question of the day")
        c.close()
        return ConversationHandler.END
    else:
        c.execute("SELECT CC,CF FROM subscribers WHERE id=(?)",(str(update.message.chat_id),))
        keyboard=[]
        for row in c.fetchall():
            if(row[0]==1):
                keyboard.append([InlineKeyboardButton("CODECHEF", callback_data='CCunsub4')])
            if(row[1]==1):
                keyboard.append([InlineKeyboardButton("CODEFORCES", callback_data='CFunsub4')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Select the one you want to unsubscribe from",reply_markup=reply_markup)
        c.close()
        conn.close()
        return UNSUB


def unsub(bot,update):
    query=update.callback_query
    val=query.data
    val=str(val).replace("unsub4","")

    a = str(query.message.chat_id)
    conn = sqlite3.connect(mount_point+'coders1.db')
    c=conn.cursor()
    c.execute("UPDATE subscribers SET " + val + " = 0 WHERE id = (?) ", (a,))
    conn.commit()
    c.execute("SELECT CC,CF FROM subscribers WHERE id=(?)", (a,))
    i=0
    for row in c.fetchall():
        if (row[0] == 0):
            i=i+1
        if (row[1] == 0):
            i=i+1
    if i==2:
        c.execute("DELETE FROM subscribers WHERE id=(?)",(a,))
        conn.commit()
    bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text="unsubscribed")
    c.close()
    conn.close()
    return ConversationHandler.END
# END OF CONVERSATION HANDLER TO UNSUBSCRIBE FROM QUESTION OF THE DAY


# FUNCTION TO SEND QUESTION TO COMPETITIVE CODERS EVERY DAY
@sched.scheduled_job('cron', hour=0, minute=0)
def sender():
    bot = Bot(TOKEN)
    global scce, s1cce, scch, s1cch, sccm, s1ccm, sccs, s1ccs, sccc, s1ccc,qcf
    conn = sqlite3.connect(mount_point+'coders1.db')
    c=conn.cursor()
    c.execute("SELECT  * FROM subscribers")
    for row in c.fetchall():
        if(row[1]==1):
            val=row[3]
            if val == 'BEGINNER':
                n = random.randint(0, len(sccs) - 1)
                strt = sccs[n].text.strip("\n\n ")
                strn = s1ccs[n].text
            if val == 'EASY':
                n = random.randint(0, len(scce) - 1)
                strt = scce[n].text.strip("\n\n ")
                strn = s1cce[n].text
            if val == 'MEDIUM':
                n = random.randint(0, len(sccm) - 1)
                strt = sccm[n].text.strip("\n\n ")
                strn = s1ccm[n].text
            if val == 'HARD':
                n = random.randint(0, len(scch) - 1)
                strt = scch[n].text.strip("\n\n ")
                strn = s1cch[n].text
            if val == 'CHALLENGE':
                n = random.randint(0, len(sccc) - 1)
                strt = sccc[n].text.strip("\n\n ")
                strn = s1ccc[n].text
            bot.send_message(
                text="Random " + val + " question from codechef\n\n" + strt + "\n" + "https://www.codechef.com/problems/" + strn,
                chat_id=row[0])
        if(row[2]==1):
            val=row[4]
            if val == 'A':
                n = random.randint(0, len(qcf['A']) - 1)
                strn = qcf['A'][n]
            elif val == 'B':
                n = random.randint(0, len(qcf['B']) - 1)
                strn = qcf['B'][n]
            elif val == 'C':
                n = random.randint(0, len(qcf['C']) - 1)
                strn = qcf['C'][n]
            elif val == 'D':
                n = random.randint(0, len(qcf['D']) - 1)
                strn = qcf['D'][n]
            elif val == 'E':
                n = random.randint(0, len(qcf['E']) - 1)
                strn = qcf['E'][n]
            elif val == 'F':
                n = random.randint(0, len(qcf['F']) - 1)
                strn = qcf['F'][n]
            else:
                n = random.randint(0, len(qcf['OTHERS']) - 1)
                strn = qcf['OTHERS'][n]
            bot.send_message(
                text="Random " + val + " question from codeforces\n\n" + strn,
                chat_id=row[0])
    c.close()
    conn.close()
sched.start()


# START OF CONVERSATION HANDLER FOR UPDATING USERS DATA ON HIS WISH
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
def updasel(bot, update):
    query = update.callback_query
    val = query.data
    val=str(val).replace("upd5","")
    a = str(query.from_user.id)
    conn = sqlite3.connect(mount_point+'coders1.db')
    c = conn.cursor()
    c.execute("SELECT id FROM handles WHERE id=(?)", (a,))
    if not c.fetchone():
        bot.edit_message_text(text='You are not registered to the bot. Please register using /register command',
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        conn.close()
        return ConversationHandler.END
    if val == "ALL":
        # IF USER SELECTED ALL UPDATING ALL HIS VALUES
        c.execute('SELECT id, HE, HR, CC, SP, CF FROM handles WHERE id=(?)', (a,))
        for row in c.fetchall():
            a = ""
            he = ""
            hr = ""
            sp = ""
            cc = ""
            cf = ""
            for wo in range(0, 6):
                if wo == 0:
                    if row[wo] is None:
                        bot.edit_message_text(text='You are not registered to the bot',
                                              chat_id=query.message.chat_id,
                                              message_id=query.message.message_id)
                        conn.close()
                        return ConversationHandler.END
                    a = row[wo]
                elif wo == 1 and (row[wo] != '' and row[wo] is not None):
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                    try:
                        sauce = opener.open('https://www.hackerearth.com/@' + str(row[wo]))
                        soup = bs.BeautifulSoup(sauce, 'html5lib')
                        stri = "HACKEREARTH\n"
                        for i in soup.find_all('a', {
                            "href": "/users/" + str(row[wo]) + "/activity/hackerearth/#user-rating-graph"}):
                            stri = stri + i.text + "\n"
                        for i in soup.find_all('a', {"href": "/@" + str(row[wo]) + "/followers/"}):
                            stri = stri + i.text + "\n"
                        for i in soup.find_all('a', {"href": "/@" + str(row[wo]) + "/following/"}):
                            stri = stri + i.text + "\n"
                        he = stri
                    except urllib.error.URLError as e:
                        pass
                elif wo == 2 and (row[wo] != '' and row[wo] is not None):
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                    try:
                        sauce = opener.open('https://www.hackerrank.com/' + str(row[wo]) + '?hr_r=1')
                        soup = bs.BeautifulSoup(sauce, 'html5lib')
                        try:
                            soup.find('script', {"id": "initialData"}).text
                            s = soup.find('script', {"id": "initialData"}).text
                            i = s.find("hacker_id", s.find("hacker_id", s.find("hacker_id") + 1) + 1)
                            i = parse.unquote(s[i:i + 280]).replace(",", ">").replace(":", " ").replace("{",
                                                                                                        "").replace(
                                "}",
                                "").replace(
                                '"', "").split(">")
                            s1 = "HACKERRANK\n"
                            for j in range(1, 10):
                                s1 = s1 + i[j] + "\n"
                            hr = s1
                        except AttributeError:
                            pass
                    except urllib.error.URLError as e:
                        pass
                elif wo == 3 and (row[wo] != '' and row[wo] is not None):
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                    count=0
                    while(count<5):
                        try:
                            sauce = opener.open('https://www.codechef.com/users/' + str(row[wo]))
                            soup = bs.BeautifulSoup(sauce, 'html5lib')
                            try:
                                soup.find('a', {"href": "http://www.codechef.com/ratings/all"}).text
                                try:
                                    s1 = soup.find('span', {"class": "rating"}).text + "\n"
                                except AttributeError:
                                    s1 = ""
                                s = "CODECHEF" + "\n" + s1 + "rating: " + soup.find('a', {
                                    "href": "http://www.codechef.com/ratings/all"}).text + "\n" + soup.find('div', {
                                    "class": "rating-ranks"}).text.replace(" ", "").replace("\n\n", "").strip('\n')
                                cc = s
                                break
                            except AttributeError:
                                break
                        except urllib.error.URLError as e:
                            count=count+1
                            continue
                elif wo == 4 and (row[wo] != '' and row[wo] is not None):
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                    try:
                        sauce = opener.open('http://www.spoj.com/users/' + str(row[wo]) + '/')
                        soup = bs.BeautifulSoup(sauce, 'html5lib')
                        try:
                            soup.find('div', {"class": "col-md-3"}).text
                            s = soup.find('div', {"class": "col-md-3"}).text.strip('\n\n').replace("\t", "").split('\n')
                            s = s[3].strip().split(":")
                            s = "SPOJ\n" + s[0] + "\n" + s[1].strip(" ") + "\n" + soup.find('dl', {
                                "class": "dl-horizontal profile-info-data profile-info-data-stats"}).text.replace("\t",
                                                                                                                  "").replace(
                                "\xa0", "").strip('\n')
                            sp = s
                        except AttributeError:
                            pass
                    except urllib.error.URLError as e:
                        pass
                elif wo == 5 and (row[wo] != '' and row[wo] is not None):
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                    try:
                        sauce = opener.open('http://codeforces.com/profile/' + str(row[wo]))
                        soup = bs.BeautifulSoup(sauce, 'html5lib')
                        try:
                            soup.find('img', {"alt": "User\'\'s contribution into Codeforces community"}).text
                            s = soup.find_all('span', {"style": "font-weight:bold;"})
                            if len(s) == 0:
                                s2 = ""
                            else:
                                s2 = "contest rating: " + s[0].text + "\n" + "max: " + s[1].text + s[2].text + "\n"
                            s1 = "CODEFORCES\n" + s2 + "contributions: " + soup.find('img', {"alt": "User\'\'s contribution into Codeforces community"}).nextSibling.nextSibling.text
                            cf = s1
                        except AttributeError:
                            pass
                    except urllib.error.URLError as e:
                        pass
            if not he=='' or (he=='' and (row[1] == '' or row[1] is None)):
                c.execute("UPDATE datas SET HE=(?) WHERE id=(?)",(he,str(a)))
                try:
                    rat = he.split('\n')
                    if (rat[1] == "Rating"):
                        rat2 = rat[2].strip(" ").strip("\n")
                        c.execute("UPDATE  priority SET HE = (?) WHERE id = (?) ", (rat2, str(a)))
                except:
                    pass
            if not hr == '' or (hr=='' and (row[2] == '' or row[2] is None)):
                c.execute("UPDATE datas SET HR=(?) WHERE id=(?)", (hr,str(a)))
                try:
                    rat = hr.split('\n')
                    rat2 = rat[1].split(" ")[1].strip(" ").strip("\n")
                    c.execute("UPDATE  priority SET HR = (?) WHERE id = (?) ", (rat2, str(a)))
                except:
                    pass
            if not cf == '' or (cf=='' and (row[5] == '' or row[5] is None)):
                c.execute("UPDATE datas SET CF=(?) WHERE id=(?)", (cf,str(a)))
                try:
                    rat = cf.split("\n")
                    if "contest rating:" in rat[1]:
                        rat2 = rat[1].split(" ")[2].strip(" ").strip("\n")
                        c.execute("UPDATE  priority SET CF = (?) WHERE id = (?) ", (rat2, str(a)))
                except:
                    pass
            if not cc == '' or (cc=='' and (row[3] == '' or row[3] is None)):
                c.execute("UPDATE datas SET CC=(?) WHERE id=(?)", (cc,str(a)))
                try:
                    rat = cc.split("\n")
                    if not "rating" in rat[1]:
                        rat2 = rat[2].split(" ")[1].strip(" ").strip("\n")
                        c.execute("UPDATE  priority SET CC = (?) WHERE id = (?) ", (rat2, str(a)))
                except:
                    pass
            if not sp=='' or (sp=='' and (row[4] == '' or row[4] is None)):
                c.execute("UPDATE datas SET SP=(?) WHERE id=(?)", (sp,str(a)))
        # RECREATING ALL XLSX FILES
        workbook = Workbook(mount_point + "HE.xlsx")
        worksheet = workbook.add_worksheet()
        format = workbook.add_format()
        format.set_align('top')
        format.set_text_wrap()
        mysel = c.execute(
            "SELECT datas.name, datas.HE FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority.HE AS FLOAT) DESC")
        for i, row in enumerate(mysel):
            for j, value in enumerate(row):
                worksheet.write(i, j, row[j], format)
                worksheet.set_row(i, 170)
        worksheet.set_column(0, 5, 40)
        workbook.close()
        workbook = Workbook(mount_point + "HR.xlsx")
        worksheet = workbook.add_worksheet()
        format = workbook.add_format()
        format.set_align('top')
        format.set_text_wrap()
        mysel = c.execute(
            "SELECT datas.name, datas.HR FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority.HR AS FLOAT) DESC")
        for i, row in enumerate(mysel):
            for j, value in enumerate(row):
                worksheet.write(i, j, row[j], format)
                worksheet.set_row(i, 170)
        worksheet.set_column(0, 5, 40)
        workbook.close()
        workbook = Workbook(mount_point + "SP.xlsx")
        worksheet = workbook.add_worksheet()
        format = workbook.add_format()
        format.set_align('top')
        format.set_text_wrap()
        mysel = c.execute("SELECT name, SP FROM datas")
        for i, row in enumerate(mysel):
            for j, value in enumerate(row):
                worksheet.write(i, j, row[j], format)
                worksheet.set_row(i, 170)
        worksheet.set_column(0, 5, 40)
        workbook.close()
        workbook = Workbook(mount_point + "CF.xlsx")
        worksheet = workbook.add_worksheet()
        format = workbook.add_format()
        format.set_align('top')
        format.set_text_wrap()
        mysel = c.execute(
            "SELECT datas.name, datas.CF FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority.CF AS FLOAT) DESC")
        for i, row in enumerate(mysel):
            for j, value in enumerate(row):
                worksheet.write(i, j, row[j], format)
                worksheet.set_row(i, 170)
        worksheet.set_column(0, 5, 40)
        workbook.close()
        workbook = Workbook(mount_point + "CC.xlsx")
        worksheet = workbook.add_worksheet()
        format = workbook.add_format()
        format.set_align('top')
        format.set_text_wrap()
        mysel = c.execute(
            "SELECT datas.name, datas.CC FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority.CC AS FLOAT) DESC")
        for i, row in enumerate(mysel):
            for j, value in enumerate(row):
                worksheet.write(i, j, row[j], format)
                worksheet.set_row(i, 170)
        worksheet.set_column(0, 5, 40)
        workbook.close()
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
                if val == "HE":
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                    try:
                        sauce = opener.open('https://www.hackerearth.com/@' + str(row[0]))
                        soup = bs.BeautifulSoup(sauce, 'html5lib')
                        stri = "HACKEREARTH\n"
                        for i in soup.find_all('a', {
                            "href": "/users/" + str(row[0]) + "/activity/hackerearth/#user-rating-graph"}):
                            stri = stri + i.text + "\n"
                        for i in soup.find_all('a', {"href": "/@" + str(row[0]) + "/followers/"}):
                            stri = stri + i.text + "\n"
                        for i in soup.find_all('a', {"href": "/@" + str(row[0]) + "/following/"}):
                            stri = stri + i.text + "\n"
                        ans = stri
                    except urllib.error.URLError as e:
                        pass
                elif val == 'HR':
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                    try:
                        sauce = opener.open('https://www.hackerrank.com/' + str(row[0]) + '?hr_r=1')
                        soup = bs.BeautifulSoup(sauce, 'html5lib')
                        try:
                            soup.find('script', {"id": "initialData"}).text
                            s = soup.find('script', {"id": "initialData"}).text
                            i = s.find("hacker_id", s.find("hacker_id", s.find("hacker_id") + 1) + 1)
                            i = parse.unquote(s[i:i + 280]).replace(",", ">").replace(":", " ").replace("{",
                                                                                                        "").replace(
                                "}",
                                "").replace(
                                '"', "").split(">")
                            s1 = "HACKERRANK\n"
                            for j in range(1, 10):
                                s1 = s1 + i[j] + "\n"
                            ans = s1
                        except AttributeError:
                            pass
                    except urllib.error.URLError as e:
                        pass
                elif val == "CC":
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                    count=0
                    while(count<5):
                        try:
                            sauce = opener.open('https://www.codechef.com/users/' + str(row[0]))
                            soup = bs.BeautifulSoup(sauce, 'html5lib')
                            try:
                                soup.find('a', {"href": "http://www.codechef.com/ratings/all"}).text
                                try:
                                    s1 = soup.find('span', {"class": "rating"}).text + "\n"
                                except AttributeError:
                                    s1 = ""
                                s = "CODECHEF" + "\n" + s1 + "rating: " + soup.find('a', {
                                    "href": "http://www.codechef.com/ratings/all"}).text + "\n" + soup.find('div', {
                                    "class": "rating-ranks"}).text.replace(" ", "").replace("\n\n", "").strip('\n')
                                ans = s
                                break
                            except AttributeError:
                                break
                        except urllib.error.URLError as e:
                            count=count+1
                            continue
                elif val == "SP":
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                    try:
                        sauce = opener.open('http://www.spoj.com/users/' + str(row[0]) + '/')
                        soup = bs.BeautifulSoup(sauce, 'html5lib')
                        try:
                            soup.find('div', {"class": "col-md-3"}).text
                            s = soup.find('div', {"class": "col-md-3"}).text.strip('\n\n').replace("\t", "").split('\n')
                            s = s[3].strip().split(":")
                            s = "SPOJ\n" + s[0] + "\n" + s[1].strip(" ") + "\n" + soup.find('dl', {
                                "class": "dl-horizontal profile-info-data profile-info-data-stats"}).text.replace("\t",
                                                                                                                  "").replace(
                                "\xa0", "").strip('\n')
                            ans = s
                        except AttributeError:
                            pass
                    except urllib.error.URLError as e:
                        pass
                elif val == "CF":
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                    try:
                        sauce = opener.open('http://codeforces.com/profile/' + str(row[0]))
                        soup = bs.BeautifulSoup(sauce, 'html5lib')
                        try:
                            soup.find('img', {"alt": "User\'\'s contribution into Codeforces community"}).text
                            s = soup.find_all('span', {"style": "font-weight:bold;"})
                            if len(s) == 0:
                                s2 = ""
                            else:
                                s2 = "contest rating: " + s[0].text + "\n" + "max: " + s[1].text + s[2].text + "\n"
                            s1 = "CODEFORCES\n" + s2 + "contributions: " + soup.find('img', {"alt": "User\'\'s contribution into Codeforces community"}).nextSibling.nextSibling.text
                            ans = s1
                        except AttributeError:
                            pass
                    except urllib.error.URLError as e:
                        pass
                c.execute("UPDATE datas SET " + val + " = (?)  WHERE id = (?) ", (ans, a))
                if val == 'HE':
                    try:
                        rat = ans.split('\n')
                        if (rat[1] == "Rating"):
                            rat2 = rat[2].strip(" ").strip("\n")
                            c.execute("UPDATE  priority SET HE = (?) WHERE id = (?) ", (rat2, a))
                    except:
                        pass
                elif val == 'HR':
                    try:
                        rat = ans.split('\n')
                        rat2 = rat[1].split(" ")[1].strip(" ").strip("\n")
                        c.execute("UPDATE  priority SET HR = (?) WHERE id = (?) ", (rat2, a))
                    except:
                        pass
                elif val == 'CF':
                    try:
                        rat = ans.split("\n")
                        if "contest rating:" in rat[1]:
                            rat2 = rat[1].split(" ")[2].strip(" ").strip("\n")
                            c.execute("UPDATE  priority SET CF = (?) WHERE id = (?) ", (rat2, a))
                    except:
                        pass
                elif val == 'CC':
                    try:
                        rat = ans.split("\n")
                        if not "rating" in rat[1]:
                            rat2 = rat[2].split(" ")[1].strip(" ").strip("\n")
                            c.execute("UPDATE  priority SET CC = (?) WHERE id = (?) ", (rat2, a))
                    except:
                        pass
            bot.edit_message_text(text=""+ans, chat_id=query.message.chat_id, message_id=query.message.message_id)
        # RECREATING ALL THE XLMX FILES
        workbook = Workbook(mount_point + val + ".xlsx")
        worksheet = workbook.add_worksheet()
        format = workbook.add_format()
        format.set_align('top')
        format.set_text_wrap()
        if not val=="SP":
            mysel = c.execute(
                "SELECT datas.name, datas." + val + " FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority." + val + " AS FLOAT) DESC")
            for i, row in enumerate(mysel):
                for j, value in enumerate(row):
                    worksheet.write(i, j, row[j], format)
                    worksheet.set_row(i, 170)
            worksheet.set_column(0, 5, 40)
            workbook.close()
        else:
            mysel = c.execute(
                "SELECT name, " + val + " FROM datas")
            for i, row in enumerate(mysel):
                for j, value in enumerate(row):
                    worksheet.write(i, j, row[j], format)
                    worksheet.set_row(i, 170)
            worksheet.set_column(0, 5, 40)
            workbook.close()
    workbook = Workbook(mount_point+'all.xlsx')
    worksheet = workbook.add_worksheet()
    format = workbook.add_format()
    format.set_align('top')
    format.set_text_wrap()
    mysel = c.execute(
        "SELECT datas.name, datas.HE, datas.HR, datas.SP, datas.CF, datas.CC FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority.CF AS FLOAT) DESC, CAST(priority.CC AS FLOAT) DESC, CAST(priority.HR AS FLOAT) DESC, CAST(priority.HE AS FLOAT) DESC")
    for i, row in enumerate(mysel):
        for j, value in enumerate(row):
            worksheet.write(i, j, row[j], format)
            worksheet.set_row(i, 170)
    worksheet.set_column(0, 5, 40)
    workbook.close()
    bot.send_message(text='Successfully updated',
                          chat_id=query.message.chat_id)
    conn.commit()
    conn.close()
    return ConversationHandler.END
# END OF CONVERSATION HANDLER FOR UPDATING USERS DATA ON HIS WISH


# START OF CONVERSATION HANDLER TO GET THE RANKLIST
@timeouts.wrapper
def ranklist(bot, update):
    keyboard = [[InlineKeyboardButton("EVERY ONE", callback_data='allsel1'),
                 InlineKeyboardButton("MINE", callback_data='minesel1')],
                [InlineKeyboardButton("GET BY NAME", callback_data='getNamesel1')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Please select the ranklist you want", reply_markup=reply_markup)
    return SELECTION


# FUNCTION TO GET THE USER REQUEST AND SHOW MENU OF RANKLISTS
def selection(bot, update):
    query = update.callback_query
    val = query.data
    val=str(val).replace("sel1","")
    if val == "all":
        keyboard = [[InlineKeyboardButton("Hackerearth", callback_data='HElist6'),
                     InlineKeyboardButton("Hackerrank", callback_data='HRlist6')],
                    [InlineKeyboardButton("Codechef", callback_data='CClist6'),
                     InlineKeyboardButton("Spoj", callback_data='SPlist6')],
                    [InlineKeyboardButton("Codeforces", callback_data='CFlist6'),
                     InlineKeyboardButton("ALL", callback_data='ALLlist6')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(text='please select the judge or select all for showing all', reply_markup=reply_markup,
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        return HOLO
    elif val == "mine":
        conn = sqlite3.connect(mount_point+'coders1.db')
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
        bot.edit_message_text(text='please enter the name',
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        return POLO
    else:
        return ConversationHandler.END


# FUNCTION TO GET THE USERS RANKLIST
def solo(bot, update):
    query = update.callback_query
    val = query.data
    choices = ['HElist7', 'HRlist7', 'CClist7', 'SPlist7', 'CFlist7', 'ALLlist7']
    if val not in choices:
        return ConversationHandler.END
    val=str(val).replace("list7","")
    conn = sqlite3.connect(mount_point+'coders1.db')
    c = conn.cursor()
    if val == "ALL":
        a = str(query.from_user.id)
        c.execute("SELECT name, HE, HR, SP, CC, CF FROM datas WHERE id=" + a)
        bot.edit_message_text(text='Sending please wait',
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        workbook = Workbook('me.xlsx')
        worksheet = workbook.add_worksheet()
        format = workbook.add_format()
        format.set_align('top')
        format.set_text_wrap()
        mysel = c.execute("SELECT name, HE, HR, SP, CC, CF FROM datas WHERE id=" + a)
        for i, row in enumerate(mysel):
            for j, value in enumerate(row):
                worksheet.write(i, j, row[j], format)
                worksheet.set_row(i, 170)
        worksheet.set_column(0, 5, 40)
        workbook.close()
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


# FUNCTION TO GET THE RANKLIST MENU OF THE USER BY SEARCHING IS NAME
def polo(bot, update, user_data):
    msg = update.message.text.upper()
    conn = sqlite3.connect(mount_point+'coders1.db')
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
        update.message.reply_text('please select the judge or select all for showing all', reply_markup=reply_markup)
        user_data['name1'] = msg
        conn.close()
        return XOLO
    else:
        conn.close()
        update.message.reply_text("Sorry this name not found")
        return ConversationHandler.END


# FUNCTION TO SHOW THE KIND OF RANKLIST USER WANTS
def xolo(bot, update, user_data):
    query = update.callback_query
    val = query.data
    choices = ['HElist8', 'HRlist8', 'CClist8', 'SPlist8', 'CFlist8', 'ALLlist8']
    if val not in choices:
        return ConversationHandler.END
    val=str(val).replace("list8","")
    name1 = user_data['name1']
    conn = sqlite3.connect(mount_point+'coders1.db')
    c = conn.cursor()
    if val == "ALL":
        c.execute("SELECT name, HE, HR, SP, CC, CF FROM datas WHERE name=(?)", (name1,))
        bot.edit_message_text(text='Sending please wait',
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        workbook = Workbook('det.xlsx')
        worksheet = workbook.add_worksheet()
        format = workbook.add_format()
        format.set_align('top')
        format.set_text_wrap()
        mysel = c.execute("SELECT name, HE, HR, SP, CC, CF FROM datas WHERE name=(?)", (name1,))
        for i, row in enumerate(mysel):
            for j, value in enumerate(row):
                worksheet.write(i, j, row[j], format)
                worksheet.set_row(i, 170)
        worksheet.set_column(0, 5, 40)
        workbook.close()
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
def holo(bot, update):
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
            bot.send_document(chat_id=query.message.chat_id, document=open(mount_point+'all.xlsx', 'rb'))
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
            bot.send_document(chat_id=query.message.chat_id, document=open(mount_point + val + ".xlsx", 'rb'))
        except FileNotFoundError:
            bot.edit_message_text(text='Sorry no entry found',
                                  chat_id=query.message.chat_id,
                                  message_id=query.message.message_id)
            return ConversationHandler.END
    return ConversationHandler.END


# END OF CONVERSATION HANDLER TO GET THE RANKLIST


# COMMAND HANDLER FUNCTION FOR CANCELLING
def cancel(bot, update, user_data):
    update.message.reply_text('Cancelled')
    user_data.clear()
    return ConversationHandler.END


# START OF ADMIN COMMANDS
# ADMIN COMMAND HANDLER FUNCTION TO RUN UPDATE WHEN HE WANTS
@timeouts.wrapper
def adminupdate(bot, update):
    if not str(update.message.chat_id) in adminlist:
        update.message.reply_text("sorry you are not an admin")
        return
    updaters()

@timeouts.wrapper
def restart(bot, update):
    if not str(update.message.chat_id) in adminlist:
        update.message.reply_text("sorry you are not an admin")
        return
    bot.send_message(update.message.chat_id, "Bot is restarting...")
    time.sleep(0.2)
    os.execl(sys.executable, sys.executable, *sys.argv)

# ADMIN COMMAND HANDLER FUNCTION TO UPDATE ALL THE QUESTIONS WHEN HE WANTS
@timeouts.wrapper
def admqupd(bot, update):
    if not str(update.message.chat_id) in adminlist:
        update.message.reply_text("sorry you are not an admin")
        return
    qupd()
    updateCf()


# START OF ADMIN CONVERSATION HANDLER TO REPLACE THE DATABASE
@timeouts.wrapper
def getDb(bot, update):
    if not str(update.message.chat_id) in adminlist:
        update.message.reply_text("sorry you are not an admin")
        return ConversationHandler.END
    update.message.reply_text("send your sqlite database")
    return DB


def db(bot, update):
    file_id = update.message.document.file_id
    newFile = bot.get_file(file_id)
    newFile.download(mount_point+'coders1.db')
    update.message.reply_text("saved")
    return ConversationHandler.END
# END OF ADMIN CONVERSATION HANDLER TO REPLACE THE DATABASE


# START OF ADMIN CONVERSATION HANDLER TO REPLACE THE CODEFORCES JSON
@timeouts.wrapper
def getCf(bot, update):
    if not str(update.message.chat_id) in adminlist:
        update.message.reply_text("sorry you are not an admin")
        return ConversationHandler.END
    update.message.reply_text("send your json file")
    return CF


def cf(bot, update):
    global qcf
    file_id = update.message.document.file_id
    newFile = bot.get_file(file_id)
    newFile.download(mount_point+'codeforces.json')
    update.message.reply_text("saved")
    with open(mount_point+'codeforces.json','r') as codeforces:
        qcf=json.load(codeforces)
    return ConversationHandler.END
# END OF ADMIN CONVERSATION HANDLER TO REPLACE THE CODEFORCES JSON


# ADMIN COMMAND HANDLER FOR GETTING THE DATABASE
@timeouts.wrapper
def givememydb(bot, update):
    if not str(update.message.chat_id) in adminlist:
        update.message.reply_text("sorry you are not an admin")
        return
    bot.send_document(chat_id=update.message.chat_id, document=open(mount_point+'coders1.db', 'rb'))


# ADMIN COMMAND HANDLER FOR GETTING THE CODEFORCES JSON
@timeouts.wrapper
def getcfjson(bot,update):
    if not str(update.message.chat_id) in adminlist:
        update.message.reply_text("sorry you are not an admin")
        return
    bot.send_document(chat_id=update.message.chat_id, document=open(mount_point+'codeforces.json', 'rb'))


# ADMIN COMMAND HANDLER FUNCTION TO GET THE DETAILS OF HANDLES OF ALL THE USERS IN DATABASE
@timeouts.wrapper
def adminhandle(bot, update):
    if not str(update.message.chat_id) in adminlist:
        update.message.reply_text("sorry you are not an admin")
        return
    conn = sqlite3.connect(mount_point+'coders1.db')
    c = conn.cursor()
    c.execute('SELECT * FROM handles')
    workbook = Workbook("admin.xlsx")
    worksheet = workbook.add_worksheet()
    format = workbook.add_format()
    format.set_align('top')
    format.set_text_wrap()
    mysel = c.execute("SELECT * FROM handles")
    for i, row in enumerate(mysel):
        for j, value in enumerate(row):
            worksheet.write(i, j, row[j], format)
    workbook.close()
    bot.send_document(chat_id=update.message.chat_id, document=open('admin.xlsx', 'rb'))
    os.remove('admin.xlsx')
    conn.close()
# END OF ADMIN COMMANDS


# MAIN SETUP FUNCTION
def setup(webhook_url=None):
    """If webhook_url is not passed, run with long-polling."""
    logging.basicConfig(level=logging.WARNING)
    if webhook_url:
        bot = Bot(TOKEN)
        update_queue = Queue()
        dp = Dispatcher(bot, update_queue)
    else:
        updater = Updater(TOKEN)
        bot = updater.bot
        dp = updater.dispatcher
        # CONVERSATION HANDLER FOR REGISTERING
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('register', register)],
            allow_reentry=True,
            states={

                NAME: [MessageHandler(Filters.text, name, pass_user_data=True)],

                JUDGE: [CallbackQueryHandler(judge, pass_user_data=True,pattern=r'\w*reg1\b')],

                HANDLE: [MessageHandler(Filters.text, handle, pass_user_data=True)]
            },

            fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
        )
        # CONVERSATION HANDLER FOR GETTING RANKLIST
        conv_handler1 = ConversationHandler(
            entry_points=[CommandHandler('ranklist', ranklist)],
            allow_reentry=True,
            states={

                SELECTION: [CallbackQueryHandler(selection,pattern=r'\w*sel1\b')],

                HOLO: [CallbackQueryHandler(holo,pattern=r'\w*list6\b')],

                SOLO: [CallbackQueryHandler(solo,pattern=r'\w*list7\b')],

                POLO: [MessageHandler(Filters.text, polo, pass_user_data=True)],

                XOLO: [CallbackQueryHandler(xolo, pass_user_data=True,pattern=r'\w*list8\b')]
            },

            fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
        )
        # CONVERSATION HANDLER FOR UNREGISTERING
        conv_handler2 = ConversationHandler(
            entry_points=[CommandHandler('unregister', unregister)],
            allow_reentry=True,
            states={

                REMOVER: [CallbackQueryHandler(remover,pattern=r'\w*rem2\b')]

            },

            fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
        )
        # CONVERSATION HANDLER FOR UPDATING
        conv_handler3 = ConversationHandler(
            entry_points=[CommandHandler('update', updatesel)],
            allow_reentry=True,
            states={

                UPDA: [CallbackQueryHandler(updasel,pattern=r'\w*upd5\b')]

            },

            fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
        )
        # CONVERSATION HANDLER FOR COMPILING AND RUNNING
        conv_handler4 = ConversationHandler(
            entry_points=[CommandHandler('compiler', compilers)],
            allow_reentry=True,
            states={

                LANG: [CallbackQueryHandler(lang, pass_user_data=True,pattern=r'\w*comp1\b')],
                CODE: [CallbackQueryHandler(code, pass_user_data=True,pattern=r'\w*so1\b')],
                DECODE: [MessageHandler(Filters.text, decode, pass_user_data=True)],
                TESTCASES: [MessageHandler(Filters.text, testcases, pass_user_data=True)],
                OTHER: [MessageHandler(Filters.text, other, pass_user_data=True)],
                FILE: [MessageHandler(Filters.document, filer, pass_user_data=True)],
                FILETEST: [MessageHandler(Filters.document, filetest, pass_user_data=True)]
            },

            fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
        )
        # CONVERSATION HANDLER FOR GETTING A RANDOM QUESTION FROM CODECHEF
        conv_handler5 = ConversationHandler(
            entry_points=[CommandHandler('randomcc', randomcc)],
            allow_reentry=True,
            states={

                QSELCC: [CallbackQueryHandler(qselcc,pattern=r'\w*cc1\b')]

            },

            fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
        )
        # CONVERSATION HANDLER FOR GEEKS FOR GEEKS
        conv_handler6 = ConversationHandler(
            entry_points=[CommandHandler('geeksforgeeks', gfg)],
            allow_reentry=True,
            states={

                GFG1: [CallbackQueryHandler(gfg1, pass_user_data=True,pattern=r'\w*gfg1\b')],

                GFG2: [CallbackQueryHandler(gfg2, pass_user_data=True,pattern='^.*gfg2.*$')],

                GFG3: [CallbackQueryHandler(gfg3, pass_user_data=True,pattern='^.*gfg3.*$')]
            },

            fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
        )
        # CONVERSATION HANDLER FOR REPLACING SQLITE DATABASE
        conv_handler7 = ConversationHandler(
            entry_points=[CommandHandler('senddb', getDb)],
            allow_reentry=True,
            states={
                DB: [MessageHandler(Filters.document, db)]
            },

            fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
        )
        # CONVERSATION HANDLER FOR GETTING UPCOMING COMPETITIONS
        conv_handler8 = ConversationHandler(
            entry_points=[CommandHandler('upcoming', upcoming)],
            allow_reentry=True,
            states={

                SCHED: [CallbackQueryHandler(remind,pattern=r"^[0-9]*$")]

            },

            fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
        )
        # CONVERSATION HANDLER FOR REMOVING CONTEST REMINDERS
        conv_handler9 = ConversationHandler(
            entry_points=[CommandHandler('dontRemindMe', removeRemind)],
            allow_reentry=True,
            states={
                REMNOTI: [CallbackQueryHandler(remnoti,pattern=r'^.*notiplz.*$')]
            },

            fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
        )
        # CONVERSATION HANDLER FOR GETTING RANDOM QUESTION FROM CODEFORCES
        conv_handler10 = ConversationHandler(
            entry_points=[CommandHandler('randomcf', randomcf)],
            allow_reentry=True,
            states={

                QSELCF: [CallbackQueryHandler(qselcf,pattern=r'\w*cf1\b')]

            },

            fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
        )
        # ADMIN CONVERSATION HANDLER TO REPLACE CODEFORCES JSON FILE
        conv_handler11 = ConversationHandler(
            entry_points=[CommandHandler('sendcf', getCf)],
            allow_reentry=True,
            states={
                CF: [MessageHandler(Filters.document,cf)]
            },

            fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
        )
        # CONVERSATION HANDLER TO SUBSCRIBE TO QUESTION OF THE DAY
        conv_handler12 = ConversationHandler(
            entry_points=[CommandHandler('subscribe', subscribe)],
            allow_reentry=True,
            states={
                SUBSEL:[CallbackQueryHandler(subsel,pattern=r'\w*sub3\b')],
                SUBCC:[CallbackQueryHandler(subcc,pattern=r'\w*cc2\b')],
                SUBCF: [CallbackQueryHandler(subcf,pattern=r'\w*cf2\b')]
            },

            fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
        )
        # CONVERSATION HANDLER TO UNSUBSCRIBE FROM QUESTION OF THE DAY
        conv_handler13 = ConversationHandler(
            entry_points=[CommandHandler('unsubscribe', unsubsel)],
            allow_reentry=True,
            states={
                UNSUB: [CallbackQueryHandler(unsub,pattern=r'\w*unsub4\b')]
            },

            fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
        )
        dp.add_handler(conv_handler)
        dp.add_handler(conv_handler1)
        dp.add_handler(conv_handler2)
        dp.add_handler(conv_handler3)
        dp.add_handler(conv_handler4)
        dp.add_handler(conv_handler5)
        dp.add_handler(conv_handler6)
        dp.add_handler(conv_handler7)
        dp.add_handler(conv_handler8)
        dp.add_handler(conv_handler9)
        dp.add_handler(conv_handler10)
        dp.add_handler(conv_handler11)
        dp.add_handler(conv_handler12)
        dp.add_handler(conv_handler13)
        dp.add_handler(CommandHandler('help', help))
        dp.add_handler(CommandHandler('givememydb', givememydb))
        dp.add_handler(CommandHandler('getcfjson', getcfjson))
        dp.add_handler(CommandHandler('start', start))
        dp.add_handler(CommandHandler('ongoing', ongoing))
        dp.add_handler(CommandHandler('adminhandle', adminhandle))
        dp.add_handler(CommandHandler('adminud', adminupdate))
        dp.add_handler(CommandHandler('adminuq', admqupd))
        dp.add_handler(CommandHandler('adminrestart', restart))
        # log all errors
        dp.add_error_handler(error)
    if webhook_url:
        bot.set_webhook(webhook_url=webhook_url)
        thread = Thread(target=dp.start, name='dispatcher')
        thread.start()
        return update_queue, bot
    else:
        bot.set_webhook()  # Delete webhook
        updater.start_polling()
        updater.idle()


if __name__ == '__main__':
    setup()