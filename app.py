import logging
import helper
import json
from datetime import datetime, timedelta
import os
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from queue import Queue
from threading import Thread
from telegram import Bot
from  telegram import ParseMode
from telegram.ext import Dispatcher, CommandHandler, ConversationHandler, MessageHandler, RegexHandler, Updater, Filters, CallbackQueryHandler
import bs4 as bs
import html5lib
import urllib.error
import urllib.request
from urllib import parse
import sqlite3
import random
from xlsxwriter.workbook import Workbook

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
TOKEN = 'YOUR_TELEGRAM-BOT-TOKEN-HERE'
API_KEY = 'YOUR-HACKERRANK-API-KEY-HERE'
compiler = helper.HackerRankAPI(api_key = API_KEY)
# FOR CONVERSATION HANDLERS
NAME, JUDGE, HANDLE= range(3)
SELECTION, HOLO, SOLO, POLO, XOLO=range(5)
REMOVER=range(1)
UPDA=range(1)
QSELCC=range(1)
LANG, CODE, DECODE, TESTCASES, RESULT, OTHER, FILE= range(7)
GFG1,GFG2,GFG3=range(3)

# CONNECTING TO SQLITE DATABASE AND CREATING TABLES
conn = sqlite3.connect('coders1.db')
create_table_request_list = [
                'CREATE TABLE handles(id TEXT PRIMARY KEY,name TEXT,HE TEXT,HR TEXT,CF TEXT,SP TEXT,CC TEXT)',
                'CREATE TABLE  datas(id TEXT PRIMARY KEY,name TEXT,HE TEXT,HR TEXT,CF TEXT,SP TEXT,CC TEXT)',
            ]
for create_table_request in create_table_request_list:
                try:
                    conn.execute(create_table_request)
                except:
                    pass
conn.commit()
conn.close()

# GETTING QUESTIONS FROM CODECHEF WEBSITE
# STORING THEM ACCORDING TO THE TAG EASY,MEDIUM,HARD,BEGINNER,CHALLENGE
# STORING TITLE OF QUESTIONS AND THEIR CODE IN SEPERATE LISTS
i=0
while(True):
    # TRYING 5 TIMES AS SOMETIMES IT GIVES URL ERROR IN ONE GO
    if i==5:
        break
    try:
        reqcce = urllib.request.Request("https://www.codechef.com/problems/easy/",headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"})
        reqccs = urllib.request.Request("https://www.codechef.com/problems/school/",headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"})
        reqccm = urllib.request.Request("https://www.codechef.com/problems/medium/",headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"})
        reqcch = urllib.request.Request("https://www.codechef.com/problems/hard/",headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"})
        reqccc = urllib.request.Request("https://www.codechef.com/problems/challenge/",headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"})
        concce = urllib.request.urlopen( reqcce )
        soupcce=bs.BeautifulSoup(concce,"html5lib")
        scce=soupcce.find_all('div',{"class":"problemname"})
        s1cce=soupcce.find_all('a',{"title":"Submit a solution to this problem."})
        conccs = urllib.request.urlopen( reqccs )
        soupccs=bs.BeautifulSoup(conccs,"html5lib")
        sccs=soupccs.find_all('div',{"class":"problemname"})
        s1ccs=soupccs.find_all('a',{"title":"Submit a solution to this problem."})
        conccm = urllib.request.urlopen( reqccm )
        soupccm=bs.BeautifulSoup(conccm,"html5lib")
        sccm=soupccm.find_all('div',{"class":"problemname"})
        s1ccm=soupccm.find_all('a',{"title":"Submit a solution to this problem."})
        concch = urllib.request.urlopen( reqcch )
        soupcch=bs.BeautifulSoup(concch,"html5lib")
        scch=soupcch.find_all('div',{"class":"problemname"})
        s1cch=soupcch.find_all('a',{"title":"Submit a solution to this problem."})
        conccc = urllib.request.urlopen( reqccc )
        soupccc=bs.BeautifulSoup(conccc,"html5lib")
        sccc=soupccc.find_all('div',{"class":"problemname"})
        s1ccc=soupccc.find_all('a',{"title":"Submit a solution to this problem."})
        break
    except urllib.error.URLError:
        i=i+1
        continue

# COMMAND HANDLER FUNCTION FOR /start COMMAND
def start(bot, update):
    update.message.reply_text('welcome!\nOnly one person can register through one telegram id\nHere are the commands\nEnter /cancel at any time to cancel operation\nEnter /randomcc to get a random question from codechef\nEnter /register to go to register menu to register your handle to the bot\nEnter /unregister to go to unregister menu to unregister from the bot\nEnter /ranklist to go to ranklist menu to get ranklist\nEnter /ongoing to get a list of ongoing competitions\nEnter /upcoming to get a list of upcoming competitions\nEnter /compiler to compile and run\nEnter /update to initialise updating of your info\n Automatic updation of all data will take place every day\n To see all the commands enter /help any time.')

# COMMAND HANDLER FUNCTION FOR /help COMMAND
def help(bot, update):
    update.message.reply_text('Only one person can register through one telegram id\nHere are the commands\nEnter /register to go to register menu to register your handle to the bot\nEnter /cancel at any time to cancel operation\nEnter /randomcc to get a random question from codechef\nEnter /unregister to go to unregister menu to unregister from the bot\nEnter /ranklist to go to ranklist menu to get ranklist\nEnter /ongoing to get a list of ongoing competitions\nEnter /upcoming to get a list of upcoming competitions\nEnter /compiler to compile and run\nEnter /update to initialise updating of your info\n Automatic updation of all data will take place every day\n To see all the commands enter /help any time.')

# FUNCTION FOR LOGGING ALL KINDS OF ERRORS
def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


# START OF CONVERSATION HANDLER FOR GETTING RANDOM QUESTION FROM CODECHEF
# FUNCTION TO GET INPUT ABOUT THE TYPE OF QUESTION FROM USER
def randomcc(bot,update):
    keyboard = [[InlineKeyboardButton("Beginner", callback_data='BEGINNER'),
                 InlineKeyboardButton("Easy", callback_data='EASY')],
                [InlineKeyboardButton("Medium", callback_data='MEDIUM'),
                 InlineKeyboardButton("Hard", callback_data='HARD')],
                [InlineKeyboardButton("Challenge", callback_data='CHALLENGE')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please select the type of question',reply_markup=reply_markup)
    return QSELCC

# FUNCTION FOR SENDING THE RANDOM QUESTION TO USER ACCORDING TO HIS CHOICE
def qselcc(bot,update):
    global scce,s1cce,scch,s1cch,sccm,s1ccm,sccs,s1ccs,sccc,s1ccc
    query=update.callback_query
    val=query.data
    if val=='BEGINNER':
        n = random.randint(0, len(sccs) - 1)
        strt=sccs[n].text.strip("\n\n ")
        strn=s1ccs[n].text
    if val=='EASY':
        n = random.randint(0, len(scce) - 1)
        strt=scce[n].text.strip("\n\n ")
        strn=s1cce[n].text
    if val=='MEDIUM':
        n = random.randint(0, len(sccm) - 1)
        strt=sccm[n].text.strip("\n\n ")
        strn=s1ccm[n].text
    if val=='HARD':
        n = random.randint(0, len(scch) - 1)
        strt=scch[n].text.strip("\n\n ")
        strn=s1cch[n].text
    if val=='CHALLENGE':
        n = random.randint(0, len(sccc) - 1)
        strt=sccc[n].text.strip("\n\n ")
        strn=s1ccc[n].text
    bot.edit_message_text(text="Random "+val+" question from codechef\n\n"+strt+"\n"+"https://www.codechef.com/problems/"+strn, chat_id=query.message.chat_id,
                          message_id=query.message.message_id)
    return ConversationHandler.END
# END OF CONVERSATION HANDLER FOR GETTING RANDOM QUESTION FROM CODECHEF


# START OF CONVERSATION HANDLER FOR REGISTERING THE USERS HANDLES
def register(bot,update):
    s=update.message.chat_id
    # CHECKING IF THE CHAT ID IS CHAT ID OF GROUP (-VE) NOT SURE ABOUT THIS THOUGH
    if s<0:
        update.message.reply_text("Sorry cant register through group, Please register through personal message")
        return ConversationHandler.END
    update.message.reply_text('Hi,please enter your name ')
    return NAME


# FUNCTION FOR GETTING THE NAME AND ASKING ABOUT WHICH JUDGE USER WANTS TO REGISTER THEIR HANDLE FOR
def name(bot,update,user_data):
    user_data['name']=update.message.text.upper()
    #THIS IS HOW AN INLINE KEYBOARD IS MADE AND USED
    keyboard = [[InlineKeyboardButton("Hackerearth", callback_data='HE'),InlineKeyboardButton("Hackerrank", callback_data='HR')],[InlineKeyboardButton("Codechef", callback_data='CC'),InlineKeyboardButton("Spoj", callback_data='SP')],[InlineKeyboardButton("Codeforces", callback_data='CF')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('please enter the online judge you want to setup with  the bot',reply_markup=reply_markup)
    return JUDGE


# FUNCTION FOR GETTING THE ONLINE JUDGE AND ASKING FOR HANDLE
def judge(bot,update,user_data):
    #AND THIS IS HOW WE GET THE CALLBACK DATA WHEN INLINE KEYBOARD KEY IS PRESSED
    query = update.callback_query
    user_data['code']=query.data
    bot.edit_message_text(text='please enter your handle eg. gotham13121997',
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
    return HANDLE


# FUNCTION FOR GETTING THE HANDLE AND REGISTERING IT IN DATABASE
# ALL THE MAGIC BEGINS HERE
def handle(bot,update,user_data):
    user=str(update.message.chat_id)
    handle1=update.message.text
    name1=user_data['name']
    code1=user_data['code']
    if code1=='HE':
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
    elif code1=='HR':
        # IF HACKERRANK
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        try:
            sauce = opener.open('https://www.hackerrank.com/'+handle1+'?hr_r=1')
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
    elif code1=='CC':
        # IF CODECHEF
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        try:
            sauce = opener.open('https://www.codechef.com/users/'+handle1)
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
    elif code1=='SP':
        # IF SPOJ
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        try:
            sauce = opener.open('http://www.spoj.com/users/'+handle1+'/')
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
    elif code1=='CF':
        # IF CODEFORCES
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        try:
            sauce = opener.open('http://codeforces.com/profile/'+handle1)
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
    conn=sqlite3.connect('coders1.db')
    c = conn.cursor()
    # STORING THE PROFILE INFO IN datas TABLE
    # STORING HANDLES IN handles TABLE
    c.execute("INSERT OR IGNORE INTO datas (id, name, "+code1+") VALUES (?, ?, ?)",(user,name1,vals))
    c.execute("INSERT OR IGNORE INTO handles (id, name, "+code1+") VALUES (?, ?, ?)",(user,name1,handle1))
    if c.rowcount==0:
        c.execute("UPDATE datas SET "+code1+" = (?) , name= (?) WHERE id = (?) ",(vals,name1,user))
        c.execute("UPDATE handles SET " + code1 + " = (?) , name= (?) WHERE id = (?) ", (handle1,name1,user))
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
            worksheet.write(i, j, row[j],format)
            worksheet.set_row(i,170)
    worksheet.set_column(0,5,40)
    workbook.close()
    c.execute("SELECT name, "+code1+" FROM datas")
    workbook = Workbook(code1+".xlsx")
    worksheet = workbook.add_worksheet()
    format = workbook.add_format()
    format.set_align('top')
    format.set_text_wrap()
    mysel = c.execute("SELECT name, "+code1+" FROM datas")
    for i, row in enumerate(mysel):
        for j, value in enumerate(row):
            worksheet.write(i, j, row[j], format)
            worksheet.set_row(i, 170)
    worksheet.set_column(0, 5, 40)
    workbook.close()
    conn.close()
    update.message.reply_text("Succesfully Registered")
    update.message.reply_text(name1+"    \n"+vals)
    user_data.clear()
    return ConversationHandler.END
# END OF CONVERSATION HANDLER FOR REGISTERING THE USERS HANDLES


# START OF CONVERSATION HANDLER FOR COMPILING AND RUNNING
def compilers(bot,update):
    keyboard = [[InlineKeyboardButton("C++", callback_data='cpp'),
                 InlineKeyboardButton("Python", callback_data='python')],
                [InlineKeyboardButton("C", callback_data='c'),
                 InlineKeyboardButton("Java", callback_data='java')],
                [InlineKeyboardButton("Python3", callback_data='python3'),
                 InlineKeyboardButton("Java8", callback_data='java8')],
                [InlineKeyboardButton("Other", callback_data='other')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please selet the language',reply_markup=reply_markup)
    return LANG

# FUNCTION TO GET THE PROGRAMMING LANGUAGE
def lang(bot,update,user_data):
    query=update.callback_query
    val=query.data
    if val=="other":
        # IF USER CHOOSES OTHER
        s1=""
        for i in compiler.supportedlanguages():
            s1=s1+i+","
        bot.edit_message_text(text="enter the name of language\n"+s1,chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        return OTHER
    else:
        # ELSE ASKING WETHER HE WANTS TO SEND SOURCE CODE OR A .TXT FILE
        user_data['lang']=val
        keyboard = [[InlineKeyboardButton("Enter Source Code", callback_data='code'),
                     InlineKeyboardButton("Send a .txt file", callback_data='file')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(text="please select",reply_markup=reply_markup,chat_id=query.message.chat_id,message_id=query.message.message_id)
        return CODE

# FUNCTION TO GET THE SOURCE CODE OR .TXT FILE AS INPUT
def code(bot,update,user_data):
    query = update.callback_query
    val = query.data
    if val=="code":
        bot.edit_message_text(text="please enter your code\nPlease make sure that the first line is not a comment line",chat_id=query.message.chat_id,message_id=query.message.message_id)
        return DECODE
    else:
        bot.edit_message_text(text="please send your .txt file", chat_id=query.message.chat_id,message_id=query.message.message_id)
        return FILE

# FUNCTION TO DOWNLOAD THE FILE SENT AND EXTRACT ITS CONTENTS
def filer(bot,update,user_data):
    file_id=update.message.document.file_id
    newFile = bot.get_file(file_id)
    newFile.download('abcd.txt')
    with open('abcd.txt', 'r') as f:
        source = f.read()
    user_data['code']=source
    update.message.reply_text('Please send test cases together as you would do in online ide\nIf you dont want to provide test cases send "#null" without quotes')
    # REMOVING THE FILE AFTER PROCESS IS COMPLETE
    os.remove('abcd.txt')
    return TESTCASES

# FUNCTION TO GET THE SOURCE CODE SENT BY USER
def decode(bot,update,user_data):
    user_data['code']=update.message.text
    update.message.reply_text('Please send test cases together as you would do in online ide\nIf you dont want to provide test cases send "#null" without quotes')
    return TESTCASES

# FUNCTION TO GET THE TEST CASES FROM THE USER
def testcases(bot,update,user_data):
    s = update.message.text
    if s=="#null":
        # CONVERTING UNICODE CHARACTER TO DOUBLE GREATER THAN OR LESS THAN
        # WEIRD
        s1 = (str(user_data['code'])).replace("«", "<<").replace("»", ">>")
        # USING COMPILER FUNCTION FROM helper.py script
        result = compiler.run({'source': s1,
                               'lang': user_data['lang']
                               })
        #GETTING OUTPUT FROM result CLASS in helper.py script
        output=result.output
        time1=result.time
        memory1=result.memory
        message1=result.message
        if time1 is not None:
            time1=time1[0]
        if memory1 is not None:
            memory1=memory1[0]
        if output is not None:
            output=output[0]
        update.message.reply_text("Output:\n"+str(output)+"\n"+"Time: "+str(time1)+"\nMemory: "+str(memory1)+"\nMessage: "+str(message1))
    else:
        #AGAIN THE SAME DRILL
        s1=(str(user_data['code'])).replace("«","<<").replace("»",">>")
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
        update.message.reply_text("Output:\n" + str(output) + "\n" + "Time: " + str(time1) + "\nMemory: " + str(
            memory1) + "\nMessage: " + str(message1))
    user_data.clear()
    return ConversationHandler.END

# FUNCTION FOR THE CASE WHERE USER HAD SELECTED OTHER
def other(bot,update,user_data):
    s=update.message.text
    user_data['lang'] = s
    keyboard = [[InlineKeyboardButton("Enter Source Code", callback_data='code'),
                 InlineKeyboardButton("Send a file", callback_data='file')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("please select",reply_markup=reply_markup)
    return CODE
# END OF CONVERSATION HANDLER FOR COMPILING AND RUNNING


# START OF CONVERSATION HANDLER FOR GEEKS FOR GEEKS
def gfg(bot,update):
    keyboard = [[InlineKeyboardButton("ALGORITHMS", callback_data='Algorithms.json'),
                 InlineKeyboardButton("DATA STRUCTURES", callback_data='DS.json')],
                [InlineKeyboardButton("GATE", callback_data='GATE.json'),
                 InlineKeyboardButton("INTERVIEW", callback_data='Interview.json')]]
    reply_markup=InlineKeyboardMarkup(keyboard)
    update.message.reply_text("please select", reply_markup=reply_markup)
    return GFG1


# FUNCTION TO SHOW SUBMENU 1
def gfg1(bot,update,user_data):
    query=update.callback_query
    val=query.data
    user_data['gfg']=val
    if(val=="Algorithms.json"):
        keyboard = [[InlineKeyboardButton("Analysis of Algorithms", callback_data='Analysis of Algorithms'),
                     InlineKeyboardButton("Searching and Sorting", callback_data='Searching and Sorting')],
                    [InlineKeyboardButton("Greedy Algorithms", callback_data='Greedy Algorithms'),
                     InlineKeyboardButton("Dynamic Programming", callback_data='Dynamic Programming')],
                    [InlineKeyboardButton("Strings and Pattern Searching", callback_data='Strings and Pattern Searching'),
                     InlineKeyboardButton("Backtracking", callback_data='Backtracking')],
                    [InlineKeyboardButton("Geometric Algorithms", callback_data='Geometric Algorithms'),
                     InlineKeyboardButton("Mathematical Algorithms", callback_data='Mathematical Algorithms')],
                    [InlineKeyboardButton("Bit Algorithms", callback_data='Bit Algorithms'),
                     InlineKeyboardButton("Randomized Algorithms", callback_data='Randomized Algorithms')],
                    [InlineKeyboardButton("Misc Algorithms", callback_data='Misc Algorithms'),
                     InlineKeyboardButton("Recursion", callback_data='Recursion')],
                    [InlineKeyboardButton("Divide and Conquer", callback_data='Divide and Conquer')]]
    elif(val=="DS.json"):
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
    elif(val=="GATE.json"):
        keyboard = [[InlineKeyboardButton("Operating Systems", callback_data='Operating Systems'),
                     InlineKeyboardButton("Database Management Systems", callback_data='Database Management Systems')],
                    [InlineKeyboardButton("Automata Theory", callback_data='Automata Theory'),
                     InlineKeyboardButton("Compilers", callback_data='Compilers')],
                    [InlineKeyboardButton("Computer Networks",
                                          callback_data='Computer Networks'),
                     InlineKeyboardButton("GATE Data Structures and Algorithms", callback_data='GATE Data Structures and Algorithms')]]
    elif(val=="Interview.json"):
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
    bot.edit_message_text(text="Please select",reply_markup=reply_markup,chat_id=query.message.chat_id,message_id=query.message.message_id)
    return GFG2


# FUNCTION TO SHOW SUBMENU 2
def gfg2(bot,update,user_data):
    query=update.callback_query
    val=query.data
    if(val=="Advanced Data Structures"):
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
        s1=""
        a=0
        for i in se:
            a=a+1
            if(a<=50):
                s = s + '<a href="' + se[i] + '">' + i + '</a>\n\n'
            else:
                s1=s1+'<a href="' + se[i] + '">' + i + '</a>\n\n'
        bot.edit_message_text(text=val+"\n\n"+s, chat_id=query.message.chat_id,
                              message_id=query.message.message_id,parse_mode=ParseMode.HTML)
        if(len(s1)!=0):
            bot.send_message(text=val+"\n\n"+s1, chat_id=query.message.chat_id,parse_mode=ParseMode.HTML)
        user_data.clear()
        return ConversationHandler.END


# FUNCTION TO SHOW SUBMENU 3
def gfg3(bot,update,user_data):
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
    return  ConversationHandler.END
# END OF CONVERSATION HANDLER FOR GEEKS FOR GEEKS


# GLOBAL VARIABLES STORE THE PREVIOUS DATA TEMPORARILY IN CASE THE WEBPAGE IS BEING MAINTAINED
ong=""
upc=""
# COMMAND HANDLER FUNCTION TO SHOW LIST OF ONGOING COMPETITIONS
def ongoing(bot,update):
    global ong
    #PARSING JSON
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
        ong=s
        update.message.reply_text(s)
    except:
        update.message.reply_text(ong)


# FUNCTION TO CONVERT TIME FROM UTC TO OTHER TIME ZONE
def time_converter(old_time, time_zone):
    time_zone = float(time_zone[:3] + ('.5' if time_zone[3] == '3' else '.0'))
    str_time = datetime.strptime(old_time, "%Y-%m-%dT%H:%M:%S")
    return (str_time + timedelta(hours=time_zone)).strftime("%Y-%m-%dT%H:%M:%S")


# COMMAND HANDLER FUNCTION TO SHOW A LIST OF UPCOMING COMPETITIONS
def upcoming(bot,update):
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
            if i == 20:
                break
            title = er['contest_name']
            start = er['start']
            duration = er['duration']
            host = er['host_name']
            contest = er['contest_url']
            start1 = time_converter(start, '+0530')
            s = s + title + "\n" + "Start:\n" + start.replace("T", " ") + " GMT\n" + str(start1).replace("T",
                                                                                                         " ") + " IST\n" + "Duration: " + duration + "\n" + host + "\n" + contest + "\n\n"
        upc=s
        update.message.reply_text(s)
    except:
        update.message.reply_text(upc)


# START OF CONVERSATION HANDLER FOR UNREGISTERING
def unregister(bot,update):
    keyboard = [[InlineKeyboardButton("Hackerearth", callback_data='HE'),
                 InlineKeyboardButton("Hackerrank", callback_data='HR')],
                [InlineKeyboardButton("Codechef", callback_data='CC'),
                 InlineKeyboardButton("Spoj", callback_data='SP')],
                [InlineKeyboardButton("Codeforces", callback_data='CF'),
                 InlineKeyboardButton("ALL", callback_data='ALL')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Select the judge you want to unregister from",reply_markup=reply_markup)
    return REMOVER


# FUNCTION FOR REMOVING DATA FROM DATABASE ACCORDING TO USERS CHOICE
def remover(bot,update):
    query=update.callback_query
    val=query.data
    conn = sqlite3.connect('coders1.db')
    c = conn.cursor()
    a=str(query.message.chat_id)
    if val == "ALL":
        # IF USER CHOSE ALL THEN DELETING HIS ENTIRE ROW FROM TABLES
        c.execute("DELETE FROM datas WHERE id = (?)",(a,))
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
        # OTHER WISE REMOVING THE PARTICULAR ENTRY
        c.execute("UPDATE datas SET " + val + " = (?)  WHERE id = (?) ", ("",a))
        c.execute("UPDATE handles SET " + val + " = (?)  WHERE id = (?) ", ("",a))
        conn.commit()
        bot.edit_message_text(text='Unregistering please wait',
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        c.execute("SELECT name, " + val + " FROM datas")
        # RECREATING XLSX FILE
        workbook = Workbook(val + ".xlsx")
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
    bot.send_message(chat_id=query.message.chat_id, text="Successfully unregistered")
    conn.commit()
    conn.close()
    return ConversationHandler.END
# END OF CONVERSATION HANDLER FOR UNREGISTERING


sched = BackgroundScheduler()


# FUNCTION FOR UPDATING ALL THE QUESTIONS FROM CODECHEF
# SCHEDULED TO AUTOMATICALLY HAPPEN AT 18:30 GMT WHICH IS 0:0 IST
@sched.scheduled_job('cron', day_of_week='sat-sun',hour=18, minute=30)
def qupd():
    global reqccc,reqcce,reqcch,reqccm,reqccs,conccc,concce,concch,conccm,conccs,scce,s1cce,scch,s1cch,sccm,s1ccm,sccs,s1ccs,sccc,s1ccc,soupccc,soupcce,soupcch,soupccm,soupccs
    try:
        reqcce = urllib.request.Request("https://www.codechef.com/problems/easy/",headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"})
        reqccs = urllib.request.Request("https://www.codechef.com/problems/school/",headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"})
        reqccm = urllib.request.Request("https://www.codechef.com/problems/medium/",headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"})
        reqcch = urllib.request.Request("https://www.codechef.com/problems/hard/",headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"})
        reqccc = urllib.request.Request("https://www.codechef.com/problems/challenge/",headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"})
        concce = urllib.request.urlopen( reqcce )
        soupcce=bs.BeautifulSoup(concce,"html5lib")
        scce=soupcce.find_all('div',{"class":"problemname"})
        s1cce=soupcce.find_all('a',{"title":"Submit a solution to this problem."})
        conccs = urllib.request.urlopen( reqccs )
        soupccs=bs.BeautifulSoup(conccs,"html5lib")
        sccs=soupccs.find_all('div',{"class":"problemname"})
        s1ccs=soupccs.find_all('a',{"title":"Submit a solution to this problem."})
        conccm = urllib.request.urlopen( reqccm )
        soupccm=bs.BeautifulSoup(conccm,"html5lib")
        sccm=soupccm.find_all('div',{"class":"problemname"})
        s1ccm=soupccm.find_all('a',{"title":"Submit a solution to this problem."})
        concch = urllib.request.urlopen( reqcch )
        soupcch=bs.BeautifulSoup(concch,"html5lib")
        scch=soupcch.find_all('div',{"class":"problemname"})
        s1cch=soupcch.find_all('a',{"title":"Submit a solution to this problem."})
        conccc = urllib.request.urlopen( reqccc )
        soupccc=bs.BeautifulSoup(conccc,"html5lib")
        sccc=soupccc.find_all('div',{"class":"problemname"})
        s1ccc=soupccc.find_all('a',{"title":"Submit a solution to this problem."})
    except urllib.error.URLError:
        pass


# ADMIN COMMAND HANDLER FUNCTION TO UPDATE ALL THE QUESTIONS WHEN HE WANTS
def admqupd(bot,update):
    qupd()


# FUNCTION FOR UPDATING ALL THE DETAILS IN DATAS TABLE
# SCHEDULED TO AUTOMATICALLY HAPPEN AT 18:30 GMT WHICH IS 0:0 IST
@sched.scheduled_job('cron', hour=18, minute=30)
def updaters():
    conn = sqlite3.connect('coders1.db')
    c = conn.cursor()
    c.execute('SELECT id, HE, HR, CC, SP, CF FROM handles')
    for row in c.fetchall():
        a = ""
        he=""
        hr=""
        sp=""
        cc=""
        cf=""
        for wo in range(0,6):
            if wo==0:
                a=row[wo]
            elif wo == 1 and (row[wo]!='' and row[wo] is not None) :
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
            elif wo == 2 and (row[wo]!='' and row[wo] is not None):
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
            elif wo == 3 and (row[wo]!='' and row[wo] is not None):
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
            elif wo == 4 and (row[wo]!='' and row[wo] is not None):
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
            elif wo == 5 and (row[wo]!='' and row[wo] is not None):
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
        c.execute("UPDATE datas SET HE=(?), HR=(?), CC=(?), SP=(?), CF=(?) WHERE id=(?)",(he,hr,cc,sp,cf,a))
    #RECREATING ALL THE XLSX FILES
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

sched.start()

# ADMIN COMMAND HANDLER FUNCTION TO RUN UPDATE WHEN HE WANTS
def adminupdate(bot,update):
    updaters()

# ADMIN COMMAND HANDLER FUNCTION TO GET THE DETAILS OF HANDLES OF ALL THE USERS IN DATABASE
def adminhandle(bot,update):
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


# START OF CONVERSATION HANDLER FOR UPDATING USERS DATA ON HIS WISH
def updatesel(bot,update):
    keyboard = [[InlineKeyboardButton("Hackerearth", callback_data='HE'),
                 InlineKeyboardButton("Hackerrank", callback_data='HR')],
                [InlineKeyboardButton("Codechef", callback_data='CC'),
                 InlineKeyboardButton("Spoj", callback_data='SP')],
                [InlineKeyboardButton("Codeforces", callback_data='CF'),
                 InlineKeyboardButton("ALL", callback_data='ALL')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("PLEASE SELECT THE JUDGE FROM WHICH YOU WANT TO UPDATE YOUR PROFILE", reply_markup=reply_markup)
    return UPDA

# FUNCTION TO UPDATE PARTICULR ENTRY USER SELECTED
def updasel(bot,update):
    query = update.callback_query
    val = query.data
    a = str(query.message.chat_id)
    conn = sqlite3.connect('coders1.db')
    c = conn.cursor()
    if val=="ALL":
        #IF USER SELECTED ALL UPDATING ALL HIS VALUES
        c.execute('SELECT id, HE, HR, CC, SP, CF FROM handles WHERE id=(?)',(a,))
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
            c.execute("UPDATE datas SET HE=(?), HR=(?), CC=(?), SP=(?), CF=(?) WHERE id=(?)", (he, hr, cc, sp, cf, str(a)))
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
    else:
        # ELSE ONLY UPDATING THE PARTICULAR ENTRY
        c.execute("SELECT "+val+" FROM handles WHERE id=(?)", (a,))
        for row in c.fetchall():
            if row[0] =="" or row[0] is None:
                bot.edit_message_text(text='You are not registered to the bot with'+val,
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id)
                conn.close()
                return ConversationHandler.END
            else:
                print(row[0])
                if val=="HE":
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
                elif val=='HR':
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
                elif val=="CC":
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
                elif val=="SP":
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
                elif val=="CF":
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
        # RECREATING ALL THE XLMX FILES
        c.execute("SELECT name, " + val + " FROM datas")
        workbook = Workbook(val + ".xlsx")
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
    bot.edit_message_text(text='Successfully updated',
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)
    conn.commit()
    conn.close()
    return ConversationHandler.END
# END OF CONVERSATION HANDLER FOR UPDATING USERS DATA ON HIS WISH


# START OF CONVERSATION HANDLER TO GET THE RANKLIST
def ranklist(bot,update):
    keyboard = [[InlineKeyboardButton("EVERY ONE", callback_data='all'),
                 InlineKeyboardButton("MINE", callback_data='mine')],
                [InlineKeyboardButton("GET BY NAME", callback_data='getName')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Please select the ranklist you want",reply_markup=reply_markup)
    return SELECTION


# FUNCTION TO GET THE USER REQUEST AND SHOW MENU OF RANKLISTS
def selection(bot,update):
    query=update.callback_query
    val=query.data
    if val=="all":
        keyboard = [[InlineKeyboardButton("Hackerearth", callback_data='HE'),
                     InlineKeyboardButton("Hackerrank", callback_data='HR')],
                    [InlineKeyboardButton("Codechef", callback_data='CC'),
                     InlineKeyboardButton("Spoj", callback_data='SP')],
                    [InlineKeyboardButton("Codeforces", callback_data='CF'),
                     InlineKeyboardButton("ALL", callback_data='ALL')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(text='please select the judge or select all for showing all',reply_markup=reply_markup,
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        return HOLO
    elif val=="mine":
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
        return SOLO
    elif val=="getName":
        bot.edit_message_text(text='please enter the name',
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        return POLO


# FUNCTION TO GET THE USERS RANKLIST
def solo(bot,update):
    query=update.callback_query
    val=query.data
    conn = sqlite3.connect('coders1.db')
    c = conn.cursor()
    if val=="ALL":
        a=str(query.message.chat_id)
        c.execute("SELECT name, HE, HR, SP, CC, CF FROM datas WHERE id="+a)
        bot.edit_message_text(text='Sending please wait',
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        workbook = Workbook('me.xlsx')
        worksheet = workbook.add_worksheet()
        format = workbook.add_format()
        format.set_align('top')
        format.set_text_wrap()
        mysel = c.execute("SELECT name, HE, HR, SP, CC, CF FROM datas WHERE id="+a)
        for i, row in enumerate(mysel):
            for j, value in enumerate(row):
                worksheet.write(i, j, row[j], format)
                worksheet.set_row(i, 170)
        worksheet.set_column(0, 5, 40)
        workbook.close()
        bot.send_document(chat_id=query.message.chat_id, document=open('me.xlsx', 'rb'))
        os.remove('me.xlsx')
    else:
        a = str(query.message.chat_id)
        c.execute("SELECT "+val+" FROM datas WHERE id=" + a)
        for i in c.fetchall():
            if i[0] is None or i[0]=="":
                bot.edit_message_text(text="NOT REGISTERED",
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id)
            else:
                bot.edit_message_text(text=""+i[0],
                                  chat_id=query.message.chat_id,
                                  message_id=query.message.message_id)
    conn.commit()
    conn.close()
    return ConversationHandler.END


# FUNCTION TO GET THE RANKLIST MENU OF THE USER BY SEARCHING IS NAME
def polo(bot,update,user_data):
    msg=update.message.text.upper()
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
        user_data['name1']=msg
        conn.close()
        return XOLO
    else:
        conn.close()
        update.message.reply_text("Sorry this name not found")
        return ConversationHandler.END


# FUNCTION TO SHOW THE KIND OF RANKLIST USER WANTS
def xolo(bot,update,user_data):
    query=update.callback_query
    val=query.data
    name1=user_data['name1']
    conn = sqlite3.connect('coders1.db')
    c = conn.cursor()
    if val=="ALL":
        c.execute("SELECT name, HE, HR, SP, CC, CF FROM datas WHERE name=(?)",(name1,))
        bot.edit_message_text(text='Sending please wait',
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        workbook = Workbook('det.xlsx')
        worksheet = workbook.add_worksheet()
        format = workbook.add_format()
        format.set_align('top')
        format.set_text_wrap()
        mysel = c.execute("SELECT name, HE, HR, SP, CC, CF FROM datas WHERE name=(?)",(name1,))
        for i, row in enumerate(mysel):
            for j, value in enumerate(row):
                worksheet.write(i, j, row[j], format)
                worksheet.set_row(i, 170)
        worksheet.set_column(0, 5, 40)
        workbook.close()
        bot.send_document(chat_id=query.message.chat_id, document=open('det.xlsx', 'rb'))
        os.remove('det.xlsx')
    else:
        c.execute("SELECT "+val+" FROM datas WHERE name=(?)", (name1,))
        for i in c.fetchall():
            if i[0] is None or i[0]=="":
                bot.edit_message_text(text="Not Registered",
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id)
            else:
                bot.edit_message_text(text=""+i[0],
                                  chat_id=query.message.chat_id,
                                  message_id=query.message.message_id)
    user_data.clear()
    conn.close()
    return ConversationHandler.END


# FUNCTION TO SHOW THE RANKLIST OF ALL THE PEOPLE
def holo(bot,update):
    query = update.callback_query
    val = query.data
    if val=="ALL":
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
            bot.send_document(chat_id=query.message.chat_id, document=open(""+val+".xlsx", 'rb'))
        except FileNotFoundError:
            bot.edit_message_text(text='Sorry no entry found',
                                  chat_id=query.message.chat_id,
                                  message_id=query.message.message_id)
            return ConversationHandler.END
    return ConversationHandler.END
# END OF CONVERSATION HANDLER TO GET THE RANKLIST


# COMMAND HANDLER FUNCTION FO CANCELLING
def cancel(bot, update,user_data):
    update.message.reply_text('Cancelled')
    user_data.clear()
    return ConversationHandler.END


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


                NAME: [MessageHandler(Filters.text, name,pass_user_data=True)],

                JUDGE: [CallbackQueryHandler(judge,pass_user_data=True)],

                HANDLE: [MessageHandler(Filters.text, handle,pass_user_data=True)]
            },

            fallbacks=[CommandHandler('cancel', cancel,pass_user_data=True)]
        )
        # CONVERSATION HANDLER FOR GETTING RANKLIST
        conv_handler1=ConversationHandler(
            entry_points=[CommandHandler('ranklist', ranklist)],
            allow_reentry=True,
            states={

                SELECTION:[CallbackQueryHandler(selection)],

                HOLO: [CallbackQueryHandler(holo)],

                SOLO: [CallbackQueryHandler(solo)],

                POLO: [MessageHandler(Filters.text,polo,pass_user_data=True)],

                XOLO: [CallbackQueryHandler(xolo,pass_user_data=True)]
            },

            fallbacks=[CommandHandler('cancel', cancel,pass_user_data=True)]
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
        conv_handler3=ConversationHandler(
            entry_points=[CommandHandler('update', updatesel)],
            allow_reentry=True,
            states={

                UPDA: [CallbackQueryHandler(updasel)]

            },

            fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
        )
        # CONVERSATION HANDLER FOR COMPILING AND RUNNING
        conv_handler4=ConversationHandler(
            entry_points=[CommandHandler('compiler', compilers)],
            allow_reentry=True,
            states={

                LANG: [CallbackQueryHandler(lang,pass_user_data=True)],
                CODE: [CallbackQueryHandler(code,pass_user_data=True)],
                DECODE: [MessageHandler(Filters.text,decode,pass_user_data=True)],
                TESTCASES: [MessageHandler(Filters.text,testcases,pass_user_data=True)],
                OTHER: [MessageHandler(Filters.text,other,pass_user_data=True)],
                FILE: [MessageHandler(Filters.document, filer, pass_user_data=True)]

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

                GFG1: [CallbackQueryHandler(gfg1,pass_user_data=True)],

                GFG2: [CallbackQueryHandler(gfg2,pass_user_data=True)],

                GFG3: [CallbackQueryHandler(gfg3,pass_user_data=True)]
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
        dp.add_handler(CommandHandler('help',help))
        dp.add_handler(CommandHandler('start',start))
        dp.add_handler(CommandHandler('ongoing',ongoing))
        dp.add_handler(CommandHandler('upcoming',upcoming))
        dp.add_handler(CommandHandler('adminhandle',adminhandle))
        dp.add_handler(CommandHandler('adminupdate', adminupdate))
        dp.add_handler(CommandHandler('updateq',admqupd))
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