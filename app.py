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
API_KEY = config.get('hackerrank','api_key')
compiler = helper.HackerRankAPI(api_key=API_KEY)
adminlist=str(config.get('telegram','admin_chat_id')).split(',')
# FOR CONVERSATION HANDLERS
NAME, JUDGE, HANDLE = range(3)
SELECTION, HOLO, SOLO, POLO, XOLO = range(5)
REMOVER = range(1)
UPDA = range(1)
QSELCC = range(1)
LANG, CODE, DECODE, TESTCASES, RESULT, OTHER, FILE, FILETEST = range(8)
GFG1, GFG2, GFG3 = range(3)
DB = range(1)
CF =range(1)
SCHED = range(1)
REMNOTI = (1)
QSELCF = range(1)
SUBSEL, SUBCC, SUBCF = range(3)
UNSUB=range(1)
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
            timeout = self.new_message(update.message.chat_id)
            if not timeout:
               return func(bot, update, *args2)
            elif isinstance(timeout, str):
                print("timeout")
                # Only works for messages (+Commands) and callback_queries (Inline Buttons)
                if update.callback_query:
                    bot.edit_message_text(chat_id=update.message.chat_id,
                                          message_id=update.message.message_id,
                                          text=timeout)
                elif update.message:
                    bot.send_message(chat_id=update.message.chat_id, text=timeout)

        return func_wrapper


timeouts = Spam_settings()


# CONNECTING TO SQLITE DATABASE AND CREATING TABLES
conn = sqlite3.connect('coders1.db')
create_table_request_list = [
    'CREATE TABLE handles(id TEXT PRIMARY KEY,name TEXT,HE TEXT,HR TEXT,CF TEXT,SP TEXT,CC TEXT)',
    'CREATE TABLE  datas(id TEXT PRIMARY KEY,name TEXT,HE TEXT,HR TEXT,CF TEXT,SP TEXT,CC TEXT)',
    'CREATE TABLE subscribers(id TEXT PRIMARY KEY,CC int DEFAULT 0,CF int DEFAULT 0,CCSEL TEXT,CFSEL TEXT)',
]
for create_table_request in create_table_request_list:
    try:
        conn.execute(create_table_request)
    except:
        pass
conn.commit()
conn.close()

if  os.path.exists('codeforces.json'):
  with open('codeforces.json', 'r') as codeforces:
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
    keyboard = [[InlineKeyboardButton("A", callback_data='A'),
                 InlineKeyboardButton("B", callback_data='B'), InlineKeyboardButton("C", callback_data='C')],
                [InlineKeyboardButton("D", callback_data='D'),
                 InlineKeyboardButton("E", callback_data='E'), InlineKeyboardButton("F", callback_data='F')],
                [InlineKeyboardButton("OTHERS", callback_data='OTHERS')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please select the type of question', reply_markup=reply_markup)
    return QSELCF


# FUNCTION FOR SENDING THE RANDOM QUESTION TO USER ACCORDING TO HIS CHOICE
def qselcf(bot, update):
    global qcf
    query = update.callback_query
    val = query.data
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
    keyboard = [[InlineKeyboardButton("Beginner", callback_data='BEGINNER'),
                 InlineKeyboardButton("Easy", callback_data='EASY')],
                [InlineKeyboardButton("Medium", callback_data='MEDIUM'),
                 InlineKeyboardButton("Hard", callback_data='HARD')],
                [InlineKeyboardButton("Challenge", callback_data='CHALLENGE')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please select the type of question', reply_markup=reply_markup)
    return QSELCC


# FUNCTION FOR SENDING THE RANDOM QUESTION TO USER ACCORDING TO HIS CHOICE
def qselcc(bot, update):
    global scce, s1cce, scch, s1cch, sccm, s1ccm, sccs, s1ccs, sccc, s1ccc
    query = update.callback_query
    val = query.data
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
    keyboard = [[InlineKeyboardButton("Hackerearth", callback_data='HE'),
                 InlineKeyboardButton("Hackerrank", callback_data='HR')],
                [InlineKeyboardButton("Codechef", callback_data='CC'),
                 InlineKeyboardButton("Spoj", callback_data='SP')],
                [InlineKeyboardButton("Codeforces", callback_data='CF')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('please enter the online judge you want to setup with  the bot',
                              reply_markup=reply_markup)
    return JUDGE


# FUNCTION FOR GETTING THE ONLINE JUDGE AND ASKING FOR HANDLE
def judge(bot, update, user_data):
    # AND THIS IS HOW WE GET THE CALLBACK DATA WHEN INLINE KEYBOARD KEY IS PRESSED
    query = update.callback_query
    user_data['code'] = query.data
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
                soup.find('span', {"style": "color:gray;font-weight:bold;"}).text
            except AttributeError:
                update.message.reply_text('wrong id')
                user_data.clear()
                return ConversationHandler.END
            s = soup.find_all('span', {"style": "font-weight:bold;"})
            if len(s) == 0:
                s2 = ""
            else:
                s2 = "contest rating: " + s[0].text + "\n" + "max: " + s[1].text + s[2].text + "\n"
            s1 = "CODEFORCES\n" + s2 + "contributions: " + soup.find('span',
                                                                     {"style": "color:gray;font-weight:bold;"}).text
            vals = s1
        except urllib.error.URLError as e:
            update.message.reply_text('wrong id')
            user_data.clear()
            return ConversationHandler.END
    # CONNECTING TO DATABASE
    conn = sqlite3.connect('coders1.db')
    c = conn.cursor()
    # STORING THE PROFILE INFO IN datas TABLE
    # STORING HANDLES IN handles TABLE
    c.execute("INSERT OR IGNORE INTO datas (id, name, " + code1 + ") VALUES (?, ?, ?)", (user, name1, vals))
    c.execute("INSERT OR IGNORE INTO handles (id, name, " + code1 + ") VALUES (?, ?, ?)", (user, name1, handle1))
    if c.rowcount == 0:
        c.execute("UPDATE datas SET " + code1 + " = (?) , name= (?) WHERE id = (?) ", (vals, name1, user))
        c.execute("UPDATE handles SET " + code1 + " = (?) , name= (?) WHERE id = (?) ", (handle1, name1, user))
    conn.commit()
    # BELOW LINES ARE USED TO CREATE XLMX FILES OF ALL SORTS OF RANKLIST
    # SO WHEN USER ASKS FOR RANKLIST THERE IS NO DELAY
    c.execute("SELECT name, HE, HR, SP, CF, CC FROM datas")
    workbook = Workbook('all.xlsx')
    worksheet = workbook.add_worksheet()
    format = workbook.add_format()
    format.set_align('top')
    format.set_text_wrap()
    mysel = c.execute("SELECT name, HE, HR, SP, CF, CC FROM datas")
    for i, row in enumerate(mysel):
        for j, value in enumerate(row):
            worksheet.write(i, j, row[j], format)
            worksheet.set_row(i, 170)
    worksheet.set_column(0, 5, 40)
    workbook.close()
    c.execute("SELECT name, " + code1 + " FROM datas")
    workbook = Workbook('' + code1 + ".xlsx")
    worksheet = workbook.add_worksheet()
    format = workbook.add_format()
    format.set_align('top')
    format.set_text_wrap()
    mysel = c.execute("SELECT name, " + code1 + " FROM datas")
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
    keyboard = [[InlineKeyboardButton("C++", callback_data='cpp'),
                 InlineKeyboardButton("Python", callback_data='python')],
                [InlineKeyboardButton("C", callback_data='c'),
                 InlineKeyboardButton("Java", callback_data='java')],
                [InlineKeyboardButton("Python3", callback_data='python3'),
                 InlineKeyboardButton("Java8", callback_data='java8')],
                [InlineKeyboardButton("Other", callback_data='other')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please select the language', reply_markup=reply_markup)
    return LANG


# FUNCTION TO GET THE PROGRAMMING LANGUAGE
def lang(bot, update, user_data):
    query = update.callback_query
    val = query.data
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
        keyboard = [[InlineKeyboardButton("Enter Source Code", callback_data='code'),
                     InlineKeyboardButton("Send a .txt file", callback_data='file')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(text="please select", reply_markup=reply_markup, chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        return CODE


# FUNCTION TO GET THE SOURCE CODE OR .TXT FILE AS INPUT
def code(bot, update, user_data):
    query = update.callback_query
    val = query.data
    if val == "code":
        bot.edit_message_text(text="please enter your code\nPlease make sure that the first line is not a comment line",
                              chat_id=query.message.chat_id, message_id=query.message.message_id)
        return DECODE
    else:
        bot.edit_message_text(text="please send your .txt file\nMaximum size 2mb", chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        return FILE


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
    keyboard = [[InlineKeyboardButton("ALGORITHMS", callback_data='Algorithms.json'),
                 InlineKeyboardButton("DATA STRUCTURES", callback_data='DS.json')],
                [InlineKeyboardButton("GATE", callback_data='GATE.json'),
                 InlineKeyboardButton("INTERVIEW", callback_data='Interview.json')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("please select", reply_markup=reply_markup)
    return GFG1


# FUNCTION TO SHOW SUBMENU 1
def gfg1(bot, update, user_data):
    query = update.callback_query
    val = query.data
    user_data['gfg'] = val
    if (val == "Algorithms.json"):
        keyboard = [[InlineKeyboardButton("Analysis of Algorithms", callback_data='Analysis of Algorithms'),
                     InlineKeyboardButton("Searching and Sorting", callback_data='Searching and Sorting')],
                    [InlineKeyboardButton("Greedy Algorithms", callback_data='Greedy Algorithms'),
                     InlineKeyboardButton("Dynamic Programming", callback_data='Dynamic Programming')],
                    [InlineKeyboardButton("Strings and Pattern Searching",
                                          callback_data='Strings and Pattern Searching'),
                     InlineKeyboardButton("Backtracking", callback_data='Backtracking')],
                    [InlineKeyboardButton("Geometric Algorithms", callback_data='Geometric Algorithms'),
                     InlineKeyboardButton("Mathematical Algorithms", callback_data='Mathematical Algorithms')],
                    [InlineKeyboardButton("Bit Algorithms", callback_data='Bit Algorithms'),
                     InlineKeyboardButton("Randomized Algorithms", callback_data='Randomized Algorithms')],
                    [InlineKeyboardButton("Misc Algorithms", callback_data='Misc Algorithms'),
                     InlineKeyboardButton("Recursion", callback_data='Recursion')],
                    [InlineKeyboardButton("Divide and Conquer", callback_data='Divide and Conquer')]]
    elif (val == "DS.json"):
        keyboard = [[InlineKeyboardButton("Linked Lists", callback_data='Linked Lists'),
                     InlineKeyboardButton("Stacks", callback_data='Stacks')],
                    [InlineKeyboardButton("Queue", callback_data='Queue'),
                     InlineKeyboardButton("Binary Trees", callback_data='Binary Trees')],
                    [InlineKeyboardButton("Binary Search Trees",
                                          callback_data='Binary Search Trees'),
                     InlineKeyboardButton("Heaps", callback_data='Heaps')],
                    [InlineKeyboardButton("Hashing", callback_data='Hashing'),
                     InlineKeyboardButton("Graphs", callback_data='Graphs')],
                    [InlineKeyboardButton("Advanced Data Structures", callback_data='Advanced Data Structures'),
                     InlineKeyboardButton("Arrays", callback_data='Arrays')],
                    [InlineKeyboardButton("Matrix", callback_data='Matrix')]]
    elif (val == "GATE.json"):
        keyboard = [[InlineKeyboardButton("Operating Systems", callback_data='Operating Systems'),
                     InlineKeyboardButton("Database Management Systems", callback_data='Database Management Systems')],
                    [InlineKeyboardButton("Automata Theory", callback_data='Automata Theory'),
                     InlineKeyboardButton("Compilers", callback_data='Compilers')],
                    [InlineKeyboardButton("Computer Networks",
                                          callback_data='Computer Networks'),
                     InlineKeyboardButton("GATE Data Structures and Algorithms",
                                          callback_data='GATE Data Structures and Algorithms')]]
    elif (val == "Interview.json"):
        keyboard = [[InlineKeyboardButton("Payu", callback_data='Payu'),
                     InlineKeyboardButton("Adobe", callback_data='Adobe')],
                    [InlineKeyboardButton("Amazon", callback_data='Amazon'),
                     InlineKeyboardButton("Flipkart", callback_data='Flipkart')],
                    [InlineKeyboardButton("Google",
                                          callback_data='Google'),
                     InlineKeyboardButton("Microsoft", callback_data='Microsoft')],
                    [InlineKeyboardButton("Snapdeal", callback_data='Snapdeal'),
                     InlineKeyboardButton("Zopper-Com", callback_data='Zopper-Com')],
                    [InlineKeyboardButton("Yahoo", callback_data='Yahoo'),
                     InlineKeyboardButton("Cisco", callback_data='Cisco')],
                    [InlineKeyboardButton("Facebook", callback_data='Facebook'),
                     InlineKeyboardButton("Yatra.Com", callback_data='Yatra.Com')],
                    [InlineKeyboardButton("Symantec", callback_data='Symantec'),
                     InlineKeyboardButton("Myntra", callback_data='Myntra')],
                    [InlineKeyboardButton("Groupon", callback_data='Groupon'),
                     InlineKeyboardButton("Belzabar", callback_data='Belzabar')],
                    [InlineKeyboardButton("Paypal", callback_data='Paypal'),
                     InlineKeyboardButton("Akosha", callback_data='Akosha')],
                    [InlineKeyboardButton("Linkedin", callback_data='Linkedin'),
                     InlineKeyboardButton("Browserstack", callback_data='Browserstack')],
                    [InlineKeyboardButton("Makemytrip", callback_data='Makemytrip'),
                     InlineKeyboardButton("Infoedge", callback_data='Infoedge')],
                    [InlineKeyboardButton("Practo", callback_data='Practo'),
                     InlineKeyboardButton("Housing-Com", callback_data='Housing-Com')],
                    [InlineKeyboardButton("Ola-Cabs", callback_data='Ola-Cabs'),
                     InlineKeyboardButton("Grofers", callback_data='Grofers')],
                    [InlineKeyboardButton("Thoughtworks", callback_data='Thoughtworks'),
                     InlineKeyboardButton("Delhivery", callback_data='Delhivery')],
                    [InlineKeyboardButton("Taxi4Sure", callback_data='Taxi4Sure'),
                     InlineKeyboardButton("Lenskart", callback_data='Lenskart')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(text="Please select", reply_markup=reply_markup, chat_id=query.message.chat_id,
                          message_id=query.message.message_id)
    return GFG2


# FUNCTION TO SHOW SUBMENU 2
def gfg2(bot, update, user_data):
    query = update.callback_query
    val = query.data
    if (val == "Advanced Data Structures"):
        keyboard = [[InlineKeyboardButton("Advanced Lists", callback_data='Advanced Lists'),
                     InlineKeyboardButton("Trie", callback_data='Trie')],
                    [InlineKeyboardButton("Suffix Array and Suffix Tree", callback_data='Suffix Array and Suffix Tree'),
                     InlineKeyboardButton("AVL Tree", callback_data='AVL Tree')],
                    [InlineKeyboardButton("Splay Tree",
                                          callback_data='Splay Tree'),
                     InlineKeyboardButton("B Tree", callback_data='B Tree')],
                    [InlineKeyboardButton("Segment Tree", callback_data='Segment Tree'),
                     InlineKeyboardButton("Red Black Tree", callback_data='Red Black Tree')],
                    [InlineKeyboardButton("K Dimensional Tree", callback_data='K Dimensional Tree'),
                     InlineKeyboardButton("Others", callback_data='Others')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(text="Please select", reply_markup=reply_markup, chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        return GFG3
    else:
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
        user_data.clear()
        return ConversationHandler.END


# FUNCTION TO SHOW SUBMENU 3
def gfg3(bot, update, user_data):
    query = update.callback_query
    val = query.data
    with open(user_data['gfg'], encoding='utf-8') as data_file:
        data = json.load(data_file)
    se = data["Advanced Data Structures"][val]
    s = ""
    for i in se:
        s = s + '<a href="' + se[i] + '">' + i + '</a>\n\n'
    bot.edit_message_text(text=val + "\n\n" + s, chat_id=query.message.chat_id,
                          message_id=query.message.message_id, parse_mode=ParseMode.HTML)
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
    rawData = urllib.request.urlopen('http://challengehuntapp.appspot.com/v2').read().decode('utf-8')
    try:
        jsonData = json.loads(rawData)
        searchResults = jsonData['active']
        s = ""
        for er in searchResults:
            title = er['contest_name']
            duration = er['duration']
            host = er['host_name']
            contest = er['contest_url']
            s = s + title + "\nDuration:" + duration + "\n" + host + "\n" + contest + "\n\n"
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
    rawData = urllib.request.urlopen('http://challengehuntapp.appspot.com/v2').read().decode('utf-8')
    try:
        jsonData = json.loads(rawData)
        searchResults = jsonData['pending']
        i = 0
        s = ""
        for er in searchResults:
            i = i + 1
            # LIMITING NO OF EVENTS TO 20
            if i == 21:
                break
            title = er['contest_name']
            start = er['start']
            duration = er['duration']
            host = er['host_name']
            contest = er['contest_url']
            start1 = time_converter(start, '+0530')
            s = s + str(i) + ". " + title + "\n" + "Start:\n" + start.replace("T", " ") + " GMT\n" + str(
                start1).replace("T",
                                " ") + " IST\n" + "Duration: " + duration + "\n" + host + "\n" + contest + "\n\n"
        upc = searchResults
        print(upc[0])
        print(upc[0]['contest_name'])
        keyboard = [[InlineKeyboardButton("1", callback_data='1'), InlineKeyboardButton("2", callback_data='2'),
                     InlineKeyboardButton("3", callback_data='3'), InlineKeyboardButton("4", callback_data='4')]
            , [InlineKeyboardButton("5", callback_data='5'), InlineKeyboardButton("6", callback_data='6'),
               InlineKeyboardButton(
                   "7", callback_data='7'), InlineKeyboardButton("8", callback_data='8')]
            , [InlineKeyboardButton("9", callback_data='9'), InlineKeyboardButton("10",
                                                                                  callback_data='10'),
               InlineKeyboardButton(
                   "11", callback_data='11'), InlineKeyboardButton("12", callback_data='12')]
            , [InlineKeyboardButton("13", callback_data='13'), InlineKeyboardButton("14",
                                                                                    callback_data='14'),
               InlineKeyboardButton(
                   "15", callback_data='15'), InlineKeyboardButton("16", callback_data='16')],
                    [InlineKeyboardButton("17", callback_data='17'), InlineKeyboardButton("18", callback_data='18'),
                     InlineKeyboardButton("19", callback_data='19'), InlineKeyboardButton("20", callback_data='20')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(s + "Select competition number to get notification" + "\n\n",
                                  reply_markup=reply_markup)

    except:
        i = 0
        s = ""
        for er in upc:
            i = i + 1
            # LIMITING NO OF EVENTS TO 20
            if i == 21:
                break
            title = er['contest_name']
            start = er['start']
            duration = er['duration']
            host = er['host_name']
            contest = er['contest_url']
            start1 = time_converter(start, '+0530')
            s = s + title + "\n" + "Start:\n" + start.replace("T", " ") + " GMT\n" + str(start1).replace("T",
                                                                                                         " ") + " IST\n" + "Duration: " + duration + "\n" + host + "\n" + contest + "\n\n"
        keyboard = [[InlineKeyboardButton("1", callback_data='1'), InlineKeyboardButton("2", callback_data='2'),
                     InlineKeyboardButton("3", callback_data='3'), InlineKeyboardButton("4", callback_data='4')]
            , [InlineKeyboardButton("5", callback_data='5'), InlineKeyboardButton("6", callback_data='6'),
               InlineKeyboardButton(
                   "7", callback_data='7'), InlineKeyboardButton("8", callback_data='8')]
            , [InlineKeyboardButton("9", callback_data='9'), InlineKeyboardButton("10",
                                                                                  callback_data='10'),
               InlineKeyboardButton(
                   "11", callback_data='11'), InlineKeyboardButton("12", callback_data='12')]
            , [InlineKeyboardButton("13", callback_data='13'), InlineKeyboardButton("14",
                                                                                    callback_data='14'),
               InlineKeyboardButton(
                   "15", callback_data='15'), InlineKeyboardButton("16", callback_data='16')],
                    [InlineKeyboardButton("17", callback_data='17'), InlineKeyboardButton("18", callback_data='18'),
                     InlineKeyboardButton("19", callback_data='19'), InlineKeyboardButton("20", callback_data='20')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(s + "\n\n" + "Select competition number to get notification",
                                  reply_markup=reply_markup)
    return SCHED


jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///coders1.db')
}
schedule = BackgroundScheduler(jobstores=jobstores)
schedule.start()


# FUNCTION TO SET REMINDER
def remind(bot, update):
    global upc
    query = update.callback_query
    msg = query.data
    msg = int(msg) - 1
    start1 = time_converter(upc[msg]['start'], '-0030')
    dateT = str(upc[msg]['start']).replace("T", " ").split(" ")
    start1 = start1.replace("T", " ").split(" ")
    date = dateT[0].split("-")
    date1 = start1[0].split("-")
    time1 = start1[1].split(":")
    schedule.add_job(remindmsgDay, 'cron', year=date[0], month=date[1], day=date[2], replace_existing=True,
                     id=str(query.message.chat_id) + str(upc[msg]['contest_name']) + "0",
                     args=[str(query.message.chat_id),
                           str(upc[msg]['contest_name']) + "\n" + str(upc[msg]['contest_url'])])
    schedule.add_job(remindmsg, 'cron', year=date1[0], month=date1[1], day=date1[2], hour=time1[0], minute=time1[0],
                     replace_existing=True,
                     id=str(query.message.chat_id) + str(upc[msg]['contest_name']) + "1",
                     args=[str(query.message.chat_id),
                           str(upc[msg]['contest_name'] + "\n" + str(upc[msg]['contest_url']))])
    bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,
                          text="I will remind you about this competition")
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
    conn = sqlite3.connect('coders1.db')
    c = conn.cursor()
    c.execute("SELECT id FROM apscheduler_jobs WHERE id LIKE  " + "'" + str(
        update.message.chat_id) + "%' AND id LIKE " + "'%0'")
    if (c.fetchone()):
        c.execute("SELECT id FROM apscheduler_jobs WHERE id LIKE  " + "'" + str(
            update.message.chat_id) + "%' AND id LIKE " + "'%0'")
        a = c.fetchall()
        keyboard=[]
        for i in range(0, len(a)):
            s =str(a[i]).replace(str(cid), "").replace("('", "").replace("',)", "").replace(
                '("', "").replace('",)', "").rstrip("0")
            keyboard.append([InlineKeyboardButton(s, callback_data=s)])
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
    val=str(query.message.chat_id)+query.data
    schedule.remove_job(val + "0")
    schedule.remove_job(val + "1")
    bot.edit_message_text(text="Reminder removed",message_id=query.message.message_id,chat_id=query.message.chat_id)
    return ConversationHandler.END


# END OF CONVERSATION HANDLER TO REMOVE REMINDERS

# START OF CONVERSATION HANDLER FOR UNREGISTERING
@timeouts.wrapper
def unregister(bot, update):
    keyboard = [[InlineKeyboardButton("Hackerearth", callback_data='HE'),
                 InlineKeyboardButton("Hackerrank", callback_data='HR')],
                [InlineKeyboardButton("Codechef", callback_data='CC'),
                 InlineKeyboardButton("Spoj", callback_data='SP')],
                [InlineKeyboardButton("Codeforces", callback_data='CF'),
                 InlineKeyboardButton("ALL", callback_data='ALL')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Select the judge you want to unregister from", reply_markup=reply_markup)
    return REMOVER


# FUNCTION FOR REMOVING DATA FROM DATABASE ACCORDING TO USERS CHOICE
def remover(bot, update):
    query = update.callback_query
    val = query.data
    conn = sqlite3.connect('coders1.db')
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
        conn.commit()
        bot.edit_message_text(text='Unregistering please wait',
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        c.execute("SELECT name, HE FROM datas")
        # RECREATING ALL XLSX FILES
        workbook = Workbook("HE.xlsx")
        worksheet = workbook.add_worksheet()
        format = workbook.add_format()
        format.set_align('top')
        format.set_text_wrap()
        mysel = c.execute("SELECT name, HE FROM datas")
        for i, row in enumerate(mysel):
            for j, value in enumerate(row):
                worksheet.write(i, j, row[j], format)
                worksheet.set_row(i, 170)
        worksheet.set_column(0, 5, 40)
        workbook.close()
        c.execute("SELECT name, HR FROM datas")
        workbook = Workbook("HR.xlsx")
        worksheet = workbook.add_worksheet()
        format = workbook.add_format()
        format.set_align('top')
        format.set_text_wrap()
        mysel = c.execute("SELECT name, HR FROM datas")
        for i, row in enumerate(mysel):
            for j, value in enumerate(row):
                worksheet.write(i, j, row[j], format)
                worksheet.set_row(i, 170)
        worksheet.set_column(0, 5, 40)
        workbook.close()
        c.execute("SELECT name, SP FROM datas")
        workbook = Workbook("SP.xlsx")
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
        c.execute("SELECT name, CF FROM datas")
        workbook = Workbook("CF.xlsx")
        worksheet = workbook.add_worksheet()
        format = workbook.add_format()
        format.set_align('top')
        format.set_text_wrap()
        mysel = c.execute("SELECT name, CF FROM datas")
        for i, row in enumerate(mysel):
            for j, value in enumerate(row):
                worksheet.write(i, j, row[j], format)
                worksheet.set_row(i, 170)
        worksheet.set_column(0, 5, 40)
        workbook.close()
        c.execute("SELECT name, CC FROM datas")
        workbook = Workbook("CC.xlsx")
        worksheet = workbook.add_worksheet()
        format = workbook.add_format()
        format.set_align('top')
        format.set_text_wrap()
        mysel = c.execute("SELECT name, CC FROM datas")
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
        conn.commit()
        bot.edit_message_text(text='Unregistering please wait',
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        c.execute("SELECT name, " + val + " FROM datas")
        # RECREATING XLSX FILE
        workbook = Workbook("" + val + ".xlsx")
        worksheet = workbook.add_worksheet()
        format = workbook.add_format()
        format.set_align('top')
        format.set_text_wrap()
        mysel = c.execute("SELECT name, " + val + " FROM datas")
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
        conn.commit()
    workbook = Workbook('all.xlsx')
    worksheet = workbook.add_worksheet()
    format = workbook.add_format()
    format.set_align('top')
    format.set_text_wrap()
    mysel = c.execute("SELECT name, HE, HR, SP, CF, CC FROM datas")
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
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    source1 = opener.open("http://www.codeforces.com/problemset")
    soup1 = bs.BeautifulSoup(source1, 'html5lib')
    endpage = int(soup1.findAll('span', {"class": "page-index"})[-1].getText())
    latest = soup1.find('td', {"class": "id"}).text
    with open('codeforces.json', 'r') as codeforces:
        data = json.load(codeforces)
        latest1 = data['latest']
        if latest1 == latest:
            return
        else:
            data['latest'] = latest
            signal = True
            for i in range(1, endpage + 1):
                if signal == False:
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
    os.remove('codeforces.json')
    with open('codeforces.json', 'w') as codeforces:
        json.dump(data, codeforces)
    with open('codeforces.json', 'r') as codeforces:
        qcf = json.load(codeforces)
    bot = Bot(TOKEN)
    for chatids in adminlist:
        bot.send_message(chat_id=chatids, text="Questions updated codeforces")


# FUNCTION FOR UPDATING ALL THE DETAILS IN DATAS TABLE
# SCHEDULED TO AUTOMATICALLY HAPPEN AT 18:30 GMT WHICH IS 0:0 IST
@sched.scheduled_job('cron', hour=18, minute=30)
def updaters():
    global timeouts
    timeouts = Spam_settings()
    conn = sqlite3.connect('coders1.db')
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
                    except AttributeError:
                        pass
                except urllib.error.URLError as e:
                    pass
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
                        soup.find('span', {"style": "color:gray;font-weight:bold;"}).text
                        s = soup.find_all('span', {"style": "font-weight:bold;"})
                        if len(s) == 0:
                            s2 = ""
                        else:
                            s2 = "contest rating: " + s[0].text + "\n" + "max: " + s[1].text + s[2].text + "\n"
                        s1 = "CODEFORCES\n" + s2 + "contributions: " + soup.find('span',
                                                                                 {
                                                                                     "style": "color:gray;font-weight:bold;"}).text
                        cf = s1
                    except AttributeError:
                        pass
                except urllib.error.URLError as e:
                    pass
        c.execute("UPDATE datas SET HE=(?), HR=(?), CC=(?), SP=(?), CF=(?) WHERE id=(?)", (he, hr, cc, sp, cf, a))
    # RECREATING ALL THE XLSX FILES
    c.execute("SELECT name, HE FROM datas")
    workbook = Workbook("HE.xlsx")
    worksheet = workbook.add_worksheet()
    format = workbook.add_format()
    format.set_align('top')
    format.set_text_wrap()
    mysel = c.execute("SELECT name, HE FROM datas")
    for i, row in enumerate(mysel):
        for j, value in enumerate(row):
            worksheet.write(i, j, row[j], format)
            worksheet.set_row(i, 170)
    worksheet.set_column(0, 5, 40)
    workbook.close()
    c.execute("SELECT name, HR FROM datas")
    workbook = Workbook("HR.xlsx")
    worksheet = workbook.add_worksheet()
    format = workbook.add_format()
    format.set_align('top')
    format.set_text_wrap()
    mysel = c.execute("SELECT name, HR FROM datas")
    for i, row in enumerate(mysel):
        for j, value in enumerate(row):
            worksheet.write(i, j, row[j], format)
            worksheet.set_row(i, 170)
    worksheet.set_column(0, 5, 40)
    workbook.close()
    c.execute("SELECT name, SP FROM datas")
    workbook = Workbook("SP.xlsx")
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
    c.execute("SELECT name, CF FROM datas")
    workbook = Workbook("CF.xlsx")
    worksheet = workbook.add_worksheet()
    format = workbook.add_format()
    format.set_align('top')
    format.set_text_wrap()
    mysel = c.execute("SELECT name, CF FROM datas")
    for i, row in enumerate(mysel):
        for j, value in enumerate(row):
            worksheet.write(i, j, row[j], format)
            worksheet.set_row(i, 170)
    worksheet.set_column(0, 5, 40)
    workbook.close()
    c.execute("SELECT name, CC FROM datas")
    workbook = Workbook("CC.xlsx")
    worksheet = workbook.add_worksheet()
    format = workbook.add_format()
    format.set_align('top')
    format.set_text_wrap()
    mysel = c.execute("SELECT name, CC FROM datas")
    for i, row in enumerate(mysel):
        for j, value in enumerate(row):
            worksheet.write(i, j, row[j], format)
            worksheet.set_row(i, 170)
    worksheet.set_column(0, 5, 40)
    workbook.close()
    c.execute("SELECT name, HE, HR, SP, CF, CC FROM datas")
    workbook = Workbook('all.xlsx')
    worksheet = workbook.add_worksheet()
    format = workbook.add_format()
    format.set_align('top')
    format.set_text_wrap()
    mysel = c.execute("SELECT name, HE, HR, SP, CF, CC FROM datas")
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
    keyboard = [[InlineKeyboardButton("CODEFORCES", callback_data='CF'),
                 InlineKeyboardButton("CODECHEF", callback_data='CC')]]
    reply_markup=InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Please select the website to which you wish to subscribe for getting question of the day",reply_markup=reply_markup)
    return SUBSEL

def subsel(bot,update):
    query=update.callback_query
    val=query.data
    if val=='CC':
        keyboard = [[InlineKeyboardButton("Beginner", callback_data='BEGINNER'),
                     InlineKeyboardButton("Easy", callback_data='EASY')],
                    [InlineKeyboardButton("Medium", callback_data='MEDIUM'),
                     InlineKeyboardButton("Hard", callback_data='HARD')],
                    [InlineKeyboardButton("Challenge", callback_data='CHALLENGE')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(chat_id=query.message.chat_id,message_id=query.message.message_id,text="PLEASE SELECT",reply_markup=reply_markup)
        return SUBCC
    else:
        keyboard = [[InlineKeyboardButton("A", callback_data='A'),
                     InlineKeyboardButton("B", callback_data='B'), InlineKeyboardButton("C", callback_data='C')],
                    [InlineKeyboardButton("D", callback_data='D'),
                     InlineKeyboardButton("E", callback_data='E'), InlineKeyboardButton("F", callback_data='F')],
                    [InlineKeyboardButton("OTHERS", callback_data='OTHERS')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text="PLEASE SELECT",reply_markup=reply_markup)
        return SUBCF


def subcc(bot,update):
    conn = sqlite3.connect('coders1.db')
    query = update.callback_query
    val = query.data
    a=str(query.message.chat_id)
    c=conn.cursor()
    c.execute("INSERT OR IGNORE INTO subscribers (id,CC,CCSEL) VALUES (?, ?, ?)", (a,1,val))
    if c.rowcount == 0:
        c.execute("UPDATE subscribers SET CC = (?) , CCSEL= (?) WHERE id = (?) ", (1, val, a))
    conn.commit()
    conn.close()
    bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text="I WILL SEND YOU A QUESTION OF TYPE "+val+" EVERYDAY FROM CODECHEF \nYOU CAN USE COMMAND /unsubscribe to unsubscribe ")
    return ConversationHandler.END


def subcf(bot,update):
    conn = sqlite3.connect('coders1.db')
    query = update.callback_query
    val = query.data
    a=str(query.message.chat_id)
    c=conn.cursor()
    c.execute("INSERT OR IGNORE INTO subscribers (id,CF,CFSEL) VALUES (?, ?, ?)", (a,1,val))
    if c.rowcount == 0:
        c.execute("UPDATE subscribers SET CF = (?) , CFSEL= (?) WHERE id = (?) ", (1, val, a))
    conn.commit()
    conn.close()
    bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id, text="I WILL SEND YOU A QUESTION OF TYPE "+val+" EVERYDAY FROM CODEFORCES \nYOU CAN USE COMMAND /unsubscribe to unsubscribe ")
    return ConversationHandler.END
# END OF CONVERSATION HANDLER TO SUBSCRIBE TO QUESTION OF THE DAY


# START OF CONVERSATION HANDLER TO UNSUBSCRIBE FROM QUESTION OF THE DAY
@timeouts.wrapper
def unsubsel(bot,update):
    conn = sqlite3.connect('coders1.db')
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
                keyboard.append([InlineKeyboardButton("CODECHEF", callback_data='CC')])
            if(row[1]==1):
                keyboard.append([InlineKeyboardButton("CODEFORCES", callback_data='CF')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Select the one you want to unsubscribe from",reply_markup=reply_markup)
        c.close()
        conn.close()
        return UNSUB


def unsub(bot,update):
    query=update.callback_query
    val=query.data
    a = str(query.message.chat_id)
    conn = sqlite3.connect('coders1.db')
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
    conn = sqlite3.connect('coders1.db')
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
    keyboard = [[InlineKeyboardButton("Hackerearth", callback_data='HE'),
                 InlineKeyboardButton("Hackerrank", callback_data='HR')],
                [InlineKeyboardButton("Codechef", callback_data='CC'),
                 InlineKeyboardButton("Spoj", callback_data='SP')],
                [InlineKeyboardButton("Codeforces", callback_data='CF'),
                 InlineKeyboardButton("ALL", callback_data='ALL')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("PLEASE SELECT THE JUDGE FROM WHICH YOU WANT TO UPDATE YOUR PROFILE",
                              reply_markup=reply_markup)
    return UPDA


# FUNCTION TO UPDATE PARTICULR ENTRY USER SELECTED
def updasel(bot, update):
    query = update.callback_query
    val = query.data
    a = str(query.from_user.id)
    conn = sqlite3.connect('coders1.db')
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
                        except AttributeError:
                            pass
                    except urllib.error.URLError as e:
                        pass
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
                            soup.find('span', {"style": "color:gray;font-weight:bold;"}).text
                            s = soup.find_all('span', {"style": "font-weight:bold;"})
                            if len(s) == 0:
                                s2 = ""
                            else:
                                s2 = "contest rating: " + s[0].text + "\n" + "max: " + s[1].text + s[2].text + "\n"
                            s1 = "CODEFORCES\n" + s2 + "contributions: " + soup.find('span',
                                                                                     {
                                                                                         "style": "color:gray;font-weight:bold;"}).text
                            cf = s1
                        except AttributeError:
                            pass
                    except urllib.error.URLError as e:
                        pass
            c.execute("UPDATE datas SET HE=(?), HR=(?), CC=(?), SP=(?), CF=(?) WHERE id=(?)",
                      (he, hr, cc, sp, cf, str(a)))
        # RECREATING ALL XLSX FILES
        c.execute("SELECT name, HE FROM datas")
        workbook = Workbook("HE.xlsx")
        worksheet = workbook.add_worksheet()
        format = workbook.add_format()
        format.set_align('top')
        format.set_text_wrap()
        mysel = c.execute("SELECT name, HE FROM datas")
        for i, row in enumerate(mysel):
            for j, value in enumerate(row):
                worksheet.write(i, j, row[j], format)
                worksheet.set_row(i, 170)
        worksheet.set_column(0, 5, 40)
        workbook.close()
        c.execute("SELECT name, HR FROM datas")
        workbook = Workbook("HR.xlsx")
        worksheet = workbook.add_worksheet()
        format = workbook.add_format()
        format.set_align('top')
        format.set_text_wrap()
        mysel = c.execute("SELECT name, HR FROM datas")
        for i, row in enumerate(mysel):
            for j, value in enumerate(row):
                worksheet.write(i, j, row[j], format)
                worksheet.set_row(i, 170)
        worksheet.set_column(0, 5, 40)
        workbook.close()
        c.execute("SELECT name, SP FROM datas")
        workbook = Workbook("SP.xlsx")
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
        c.execute("SELECT name, CF FROM datas")
        workbook = Workbook("CF.xlsx")
        worksheet = workbook.add_worksheet()
        format = workbook.add_format()
        format.set_align('top')
        format.set_text_wrap()
        mysel = c.execute("SELECT name, CF FROM datas")
        for i, row in enumerate(mysel):
            for j, value in enumerate(row):
                worksheet.write(i, j, row[j], format)
                worksheet.set_row(i, 170)
        worksheet.set_column(0, 5, 40)
        workbook.close()
        c.execute("SELECT name, CC FROM datas")
        workbook = Workbook("CC.xlsx")
        worksheet = workbook.add_worksheet()
        format = workbook.add_format()
        format.set_align('top')
        format.set_text_wrap()
        mysel = c.execute("SELECT name, CC FROM datas")
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
                        except AttributeError:
                            pass
                    except urllib.error.URLError as e:
                        pass
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
                            soup.find('span', {"style": "color:gray;font-weight:bold;"}).text
                            s = soup.find_all('span', {"style": "font-weight:bold;"})
                            if len(s) == 0:
                                s2 = ""
                            else:
                                s2 = "contest rating: " + s[0].text + "\n" + "max: " + s[1].text + s[2].text + "\n"
                            s1 = "CODEFORCES\n" + s2 + "contributions: " + soup.find('span',
                                                                                     {
                                                                                         "style": "color:gray;font-weight:bold;"}).text
                            ans = s1
                        except AttributeError:
                            pass
                    except urllib.error.URLError as e:
                        pass
                c.execute("UPDATE datas SET " + val + " = (?)  WHERE id = (?) ", (ans, a))
            bot.edit_message_text(text=""+ans, chat_id=query.message.chat_id, message_id=query.message.message_id)
        # RECREATING ALL THE XLMX FILES
        c.execute("SELECT name, " + val + " FROM datas")
        workbook = Workbook("" + val + ".xlsx")
        worksheet = workbook.add_worksheet()
        format = workbook.add_format()
        format.set_align('top')
        format.set_text_wrap()
        mysel = c.execute("SELECT name, " + val + " FROM datas")
        for i, row in enumerate(mysel):
            for j, value in enumerate(row):
                worksheet.write(i, j, row[j], format)
                worksheet.set_row(i, 170)
        worksheet.set_column(0, 5, 40)
        workbook.close()
    c.execute("SELECT name, HE, HR, SP, CF, CC FROM datas")
    workbook = Workbook('all.xlsx')
    worksheet = workbook.add_worksheet()
    format = workbook.add_format()
    format.set_align('top')
    format.set_text_wrap()
    mysel = c.execute("SELECT name, HE, HR, SP, CF, CC FROM datas")
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
    keyboard = [[InlineKeyboardButton("EVERY ONE", callback_data='all'),
                 InlineKeyboardButton("MINE", callback_data='mine')],
                [InlineKeyboardButton("GET BY NAME", callback_data='getName')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Please select the ranklist you want", reply_markup=reply_markup)
    return SELECTION


# FUNCTION TO GET THE USER REQUEST AND SHOW MENU OF RANKLISTS
def selection(bot, update):
    query = update.callback_query
    val = query.data
    if val == "all":
        keyboard = [[InlineKeyboardButton("Hackerearth", callback_data='HE'),
                     InlineKeyboardButton("Hackerrank", callback_data='HR')],
                    [InlineKeyboardButton("Codechef", callback_data='CC'),
                     InlineKeyboardButton("Spoj", callback_data='SP')],
                    [InlineKeyboardButton("Codeforces", callback_data='CF'),
                     InlineKeyboardButton("ALL", callback_data='ALL')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(text='please select the judge or select all for showing all', reply_markup=reply_markup,
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        return HOLO
    elif val == "mine":
        conn = sqlite3.connect('coders1.db')
        c = conn.cursor()
        print(str(query.from_user.id))
        c.execute("SELECT id FROM datas WHERE id=" + str(query.from_user.id))
        if c.fetchone():
            keyboard = [[InlineKeyboardButton("Hackerearth", callback_data='HE'),
                         InlineKeyboardButton("Hackerrank", callback_data='HR')],
                        [InlineKeyboardButton("Codechef", callback_data='CC'),
                         InlineKeyboardButton("Spoj", callback_data='SP')],
                        [InlineKeyboardButton("Codeforces", callback_data='CF'),
                         InlineKeyboardButton("ALL", callback_data='ALL')]]
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


# FUNCTION TO GET THE USERS RANKLIST
def solo(bot, update):
    query = update.callback_query
    val = query.data
    conn = sqlite3.connect('coders1.db')
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
    conn = sqlite3.connect('coders1.db')
    c = conn.cursor()
    c.execute("SELECT name FROM handles WHERE name=(?)", (msg,))
    if c.fetchone():
        keyboard = [[InlineKeyboardButton("Hackerearth", callback_data='HE'),
                     InlineKeyboardButton("Hackerrank", callback_data='HR')],
                    [InlineKeyboardButton("Codechef", callback_data='CC'),
                     InlineKeyboardButton("Spoj", callback_data='SP')],
                    [InlineKeyboardButton("Codeforces", callback_data='CF'),
                     InlineKeyboardButton("ALL", callback_data='ALL')]]
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
    name1 = user_data['name1']
    conn = sqlite3.connect('coders1.db')
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
    if val == "ALL":
        try:
            bot.edit_message_text(text='I am sending you the details',
                                  chat_id=query.message.chat_id,
                                  message_id=query.message.message_id)
            bot.send_document(chat_id=query.message.chat_id, document=open('all.xlsx', 'rb'))
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
            bot.send_document(chat_id=query.message.chat_id, document=open("" + val + ".xlsx", 'rb'))
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
    newFile.download('coders1.db')
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
    newFile.download('codeforces.json')
    update.message.reply_text("saved")
    qcf=json.load('codeforces.json')
    return ConversationHandler.END
# END OF ADMIN CONVERSATION HANDLER TO REPLACE THE CODEFORCES JSON


# ADMIN COMMAND HANDLER FOR GETTING THE DATABASE
@timeouts.wrapper
def givememydb(bot, update):
    if not str(update.message.chat_id) in adminlist:
        update.message.reply_text("sorry you are not an admin")
        return
    bot.send_document(chat_id=update.message.chat_id, document=open('coders1.db', 'rb'))


# ADMIN COMMAND HANDLER FOR GETTING THE CODEFORCES JSON
@timeouts.wrapper
def getcfjson(bot,update):
    if not str(update.message.chat_id) in adminlist:
        update.message.reply_text("sorry you are not an admin")
        return
    bot.send_document(chat_id=update.message.chat_id, document=open('codeforces.json', 'rb'))


# ADMIN COMMAND HANDLER FUNCTION TO GET THE DETAILS OF HANDLES OF ALL THE USERS IN DATABASE
@timeouts.wrapper
def adminhandle(bot, update):
    if not str(update.message.chat_id) in adminlist:
        update.message.reply_text("sorry you are not an admin")
        return
    conn = sqlite3.connect('coders1.db')
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

                JUDGE: [CallbackQueryHandler(judge, pass_user_data=True)],

                HANDLE: [MessageHandler(Filters.text, handle, pass_user_data=True)]
            },

            fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
        )
        # CONVERSATION HANDLER FOR GETTING RANKLIST
        conv_handler1 = ConversationHandler(
            entry_points=[CommandHandler('ranklist', ranklist)],
            allow_reentry=True,
            states={

                SELECTION: [CallbackQueryHandler(selection)],

                HOLO: [CallbackQueryHandler(holo)],

                SOLO: [CallbackQueryHandler(solo)],

                POLO: [MessageHandler(Filters.text, polo, pass_user_data=True)],

                XOLO: [CallbackQueryHandler(xolo, pass_user_data=True)]
            },

            fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
        )
        # CONVERSATION HANDLER FOR UNREGISTERING
        conv_handler2 = ConversationHandler(
            entry_points=[CommandHandler('unregister', unregister)],
            allow_reentry=True,
            states={

                REMOVER: [CallbackQueryHandler(remover)]

            },

            fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
        )
        # CONVERSATION HANDLER FOR UPDATING
        conv_handler3 = ConversationHandler(
            entry_points=[CommandHandler('update', updatesel)],
            allow_reentry=True,
            states={

                UPDA: [CallbackQueryHandler(updasel)]

            },

            fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
        )
        # CONVERSATION HANDLER FOR COMPILING AND RUNNING
        conv_handler4 = ConversationHandler(
            entry_points=[CommandHandler('compiler', compilers)],
            allow_reentry=True,
            states={

                LANG: [CallbackQueryHandler(lang, pass_user_data=True)],
                CODE: [CallbackQueryHandler(code, pass_user_data=True)],
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

                QSELCC: [CallbackQueryHandler(qselcc)]

            },

            fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
        )
        # CONVERSATION HANDLER FOR GEEKS FOR GEEKS
        conv_handler6 = ConversationHandler(
            entry_points=[CommandHandler('geeksforgeeks', gfg)],
            allow_reentry=True,
            states={

                GFG1: [CallbackQueryHandler(gfg1, pass_user_data=True)],

                GFG2: [CallbackQueryHandler(gfg2, pass_user_data=True)],

                GFG3: [CallbackQueryHandler(gfg3, pass_user_data=True)]
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

                SCHED: [CallbackQueryHandler(remind)]

            },

            fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
        )
        # CONVERSATION HANDLER FOR REMOVING CONTEST REMINDERS
        conv_handler9 = ConversationHandler(
            entry_points=[CommandHandler('dontRemindMe', removeRemind)],
            allow_reentry=True,
            states={
                REMNOTI: [CallbackQueryHandler(remnoti)]
            },

            fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
        )
        # CONVERSATION HANDLER FOR GETTING RANDOM QUESTION FROM CODEFORCES
        conv_handler10 = ConversationHandler(
            entry_points=[CommandHandler('randomcf', randomcf)],
            allow_reentry=True,
            states={

                QSELCF: [CallbackQueryHandler(qselcf)]

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
                SUBSEL:[CallbackQueryHandler(subsel)],
                SUBCC:[CallbackQueryHandler(subcc)],
                SUBCF: [CallbackQueryHandler(subcf)]
            },

            fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
        )
        # CONVERSATION HANDLER TO UNSUBSCRIBE FROM QUESTION OF THE DAY
        conv_handler13 = ConversationHandler(
            entry_points=[CommandHandler('unsubscribe', unsubsel)],
            allow_reentry=True,
            states={
                UNSUB: [CallbackQueryHandler(unsub)]
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