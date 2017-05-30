import logging
import helper
import json
import os
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from queue import Queue
from threading import Thread
from telegram import Bot
from telegram.ext import Dispatcher, CommandHandler, ConversationHandler, MessageHandler, RegexHandler, Updater, Filters, CallbackQueryHandler
import bs4 as bs
import html5lib
import urllib.error
import urllib.request
from urllib import parse
import sqlite3
from xlsxwriter.workbook import Workbook

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
TOKEN = 'YOUR-telegram-bot-token-here'
API_KEY = 'YOUR-HACKERRANK-API'
compiler = helper.HackerRankAPI(api_key = API_KEY)

NAME, JUDGE, HANDLE= range(3)
SELECTION, HOLO, SOLO, POLO, XOLO=range(5)
REMOVER=range(1)
UPDA=range(1)
LANG, CODE, DECODE, TESTCASES, RESULT, OTHER, FILE= range(7)
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

def start(bot, update):
    update.message.reply_text('welcome!\nOnly one person can register through one telegram id\nHere are the commands\nEnter /cancel at any time to cancel operation\nEnter /register to go to register menu to register your handle to the bot\nEnter /unregister to go to unregister menu to unregister from the bot\nEnter /ranklist to go to ranklist menu to get ranklist\nEnter /ongoing to get a list of ongoing competitions\nEnter /upcoming to get a list of upcoming competitions\nEnter /compiler to compile and run\nEnter /update to initialise updating of your info\n Automatic updation of all data will take place every day\n To see all the commands enter /help any time.')

def help(bot,update):
    update.message.reply_text(
        'Only one person can register through one telegram id\nHere are the commands\nEnter /register to go to register menu to register your handle to the bot\nEnter /cancel at any time to cancel operation\nEnter /unregister to go to unregister menu to unregister from the bot\nEnter /ranklist to go to ranklist menu to get ranklist\nEnter /ongoing to get a list of ongoing competitions\nEnter /upcoming to get a list of upcoming competitions\nEnter /compiler to compile and run\nEnter /update to initialise updating of your info\n Automatic updation of all data will take place every day\n To see all the commands enter /help any time.')

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def register(bot,update):
    update.message.reply_text('Hi,please enter your name ')
    return NAME


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


def lang(bot,update,user_data):
    query=update.callback_query
    val=query.data
    if val=="other":
        s1=""
        for i in compiler.supportedlanguages():
            s1=s1+i+","
        bot.edit_message_text(text="enter the name of language\n"+s1,chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        return OTHER
    else:
        user_data['lang']=val
        keyboard = [[InlineKeyboardButton("Enter Source Code", callback_data='code'),
                     InlineKeyboardButton("Send a .txt file", callback_data='file')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(text="please select",reply_markup=reply_markup,chat_id=query.message.chat_id,message_id=query.message.message_id)
        return CODE


def code(bot,update,user_data):
    query = update.callback_query
    val = query.data
    if val=="code":
        bot.edit_message_text(text="please enter your code\nPlease make sure that the first line is not a comment line",chat_id=query.message.chat_id,message_id=query.message.message_id)
        return DECODE
    else:
        bot.edit_message_text(text="please send your .txt file", chat_id=query.message.chat_id,message_id=query.message.message_id)
        return FILE


def filer(bot,update,user_data):
    file_id=update.message.document.file_id
    newFile = bot.get_file(file_id)
    newFile.download('abcd.txt')
    with open('abcd.txt', 'r') as f:
        source = f.read()
    user_data['code']=source
    update.message.reply_text('Please send test cases together as you would do in online ide\nIf you dont want to provide test cases send "#null" without quotes')
    os.remove('abcd.txt')
    return TESTCASES

def decode(bot,update,user_data):
    user_data['code']=update.message.text
    update.message.reply_text('Please send test cases together as you would do in online ide\nIf you dont want to provide test cases send "#null" without quotes')
    return TESTCASES

def testcases(bot,update,user_data):
    s = update.message.text
    if s=="#null":
        s1 = (str(user_data['code'])).replace("«", "<<").replace("»", ">>")
        result = compiler.run({'source': s1,
                               'lang': user_data['lang']
                               })
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

def other(bot,update,user_data):
    s=update.message.text
    user_data['lang'] = s
    keyboard = [[InlineKeyboardButton("Enter Source Code", callback_data='code'),
                 InlineKeyboardButton("Send a file", callback_data='file')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("please select",reply_markup=reply_markup)
    return CODE


def ongoing(bot,update):
    rawData = urllib.request.urlopen('http://challengehuntapp.appspot.com/v2').read().decode('utf-8')
    jsonData = json.loads(rawData)
    searchResults = jsonData['active']
    s = ""
    for er in searchResults:
        title = er['contest_name']
        duration = er['duration']
        host = er['host_name']
        contest = er['contest_url']
        s = s + title + "\nDuration:" + duration + "\n" + host + "\n" + contest + "\n\n"
    update.message.reply_text(s)


def upcoming(bot,update):
    rawData = urllib.request.urlopen('http://challengehuntapp.appspot.com/v2').read().decode('utf-8')
    jsonData = json.loads(rawData)
    searchResults = jsonData['pending']
    i = 0
    s = ""
    for er in searchResults:
        i = i + 1
        if i == 20:
            break
        title = er['contest_name']
        start = er['start']
        duration = er['duration']
        host = er['host_name']
        contest = er['contest_url']
        s = s + title + "\n" + "Start: " + start.replace("T"," ") + "\n" + "Duration: " + duration + "\n" + host + "\n" + contest + "\n\n"
    update.message.reply_text(s)


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



sched = BackgroundScheduler()


@sched.scheduled_job('cron', hour=0, minute=0)
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
    print("updated")

sched.start()

def adminupdate(bot,update):
    updaters()


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

def updasel(bot,update):
    query = update.callback_query
    val = query.data
    a = str(query.message.chat_id)
    conn = sqlite3.connect('coders1.db')
    c = conn.cursor()
    if val=="ALL":
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




def remover(bot,update):
    query=update.callback_query
    val=query.data
    conn = sqlite3.connect('coders1.db')
    c = conn.cursor()
    a=str(query.message.chat_id)
    if val == "ALL":
        c.execute("DELETE FROM datas WHERE id = (?)",(a,))
        c.execute("DELETE FROM handles WHERE id = (?)", (a,))
        conn.commit()
        bot.edit_message_text(text='Unregistering please wait',
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
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
        c.execute("UPDATE datas SET " + val + " = (?)  WHERE id = (?) ", ("",a))
        c.execute("UPDATE handles SET " + val + " = (?)  WHERE id = (?) ", ("",a))
        conn.commit()
        bot.edit_message_text(text='Unregistering please wait',
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
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
    bot.send_message(chat_id=query.message.chat_id, text="Successfully unregistered")
    conn.commit()
    conn.close()
    return ConversationHandler.END


def ranklist(bot,update):
    keyboard = [[InlineKeyboardButton("EVERY ONE", callback_data='all'),
                 InlineKeyboardButton("MINE", callback_data='mine')],
                [InlineKeyboardButton("GET BY NAME", callback_data='getName')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Please select the ranklist you want",reply_markup=reply_markup)
    return SELECTION


def name(bot,update,user_data):
    user_data['name']=update.message.text.upper()
    keyboard = [[InlineKeyboardButton("Hackerearth", callback_data='HE'),InlineKeyboardButton("Hackerrank", callback_data='HR')],[InlineKeyboardButton("Codechef", callback_data='CC'),InlineKeyboardButton("Spoj", callback_data='SP')],[InlineKeyboardButton("Codeforces", callback_data='CF')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('please enter the online judge you want to setup with  the bot',reply_markup=reply_markup)
    return JUDGE


def judge(bot,update,user_data):
    query = update.callback_query
    user_data['code']=query.data
    bot.edit_message_text(text='please enter your handle eg. gotham13121997',
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
    return HANDLE


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


def handle(bot,update,user_data):
    user=str(update.message.chat_id)
    handle1=update.message.text
    name1=user_data['name']
    code1=user_data['code']
    if code1=='HE':
        opener = urllib.request.build_opener()
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
            update.message.reply_text('wrong id')
            user_data.clear()
            return ConversationHandler.END
    elif code1=='HR':
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
    conn=sqlite3.connect('coders1.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO datas (id, name, "+code1+") VALUES (?, ?, ?)",(user,name1,vals))
    c.execute("INSERT OR IGNORE INTO handles (id, name, "+code1+") VALUES (?, ?, ?)",(user,name1,handle1))
    if c.rowcount==0:
        c.execute("UPDATE datas SET "+code1+" = (?) , name= (?) WHERE id = (?) ",(vals,name1,user))
        c.execute("UPDATE handles SET " + code1 + " = (?) , name= (?) WHERE id = (?) ", (handle1,name1,user))
    conn.commit()
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
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('register', register)],

            states={


                NAME: [MessageHandler(Filters.text, name,pass_user_data=True)],

                JUDGE: [CallbackQueryHandler(judge,pass_user_data=True)],

                HANDLE: [MessageHandler(Filters.text, handle,pass_user_data=True)]
            },

            fallbacks=[CommandHandler('cancel', cancel,pass_user_data=True)]
        )

        conv_handler1=ConversationHandler(
            entry_points=[CommandHandler('ranklist', ranklist)],

            states={

                SELECTION:[CallbackQueryHandler(selection)],

                HOLO: [CallbackQueryHandler(holo)],

                SOLO: [CallbackQueryHandler(solo)],

                POLO: [MessageHandler(Filters.text,polo,pass_user_data=True)],

                XOLO: [CallbackQueryHandler(xolo,pass_user_data=True)]
            },

            fallbacks=[CommandHandler('cancel', cancel,pass_user_data=True)]
        )

        conv_handler2 = ConversationHandler(
            entry_points=[CommandHandler('unregister', unregister)],

            states={

                REMOVER: [CallbackQueryHandler(remover)]

            },

            fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
        )

        conv_handler3=ConversationHandler(
            entry_points=[CommandHandler('update', updatesel)],

            states={

                UPDA: [CallbackQueryHandler(updasel)]

            },

            fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
        )

        conv_handler4=ConversationHandler(
            entry_points=[CommandHandler('compiler', compilers)],

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
        dp.add_handler(conv_handler)
        dp.add_handler(conv_handler1)
        dp.add_handler(conv_handler2)
        dp.add_handler(conv_handler3)
        dp.add_handler(conv_handler4)
        dp.add_handler(CommandHandler('help',help))
        dp.add_handler(CommandHandler('start',start))
        dp.add_handler(CommandHandler('ongoing',ongoing))
        dp.add_handler(CommandHandler('upcoming',upcoming))
        dp.add_handler(CommandHandler('adminhandle',adminhandle))
        dp.add_handler(CommandHandler('adminupdate', adminupdate))
        # log all errors
        dp.add_error_handler(error)
    # Add your handlers here
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