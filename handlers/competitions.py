"""
Created by Gotham on 04-08-2018.
"""
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler
import flood_protection
from contest_utility import ContestUtility
from datetime import datetime
import requests
import urllib3
import json
import sqlite3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
timeouts = flood_protection.Spam_settings()
SCHED,REMNOTI = range(5000, 5002)


class Competitions:
    def __init__(self, clist_user_name, clist_api_key, mount_point, bot, fallback):
        self.clist_user_name = clist_user_name
        self.clist_api_key = clist_api_key
        self.bot = bot
        self.ong = None
        self.upc = None
        self.mount_point = mount_point
        self.utility = ContestUtility(mount_point)
        self.jobstores = {
            'default': SQLAlchemyJobStore(url='sqlite:///' + mount_point + 'coders1.db')
        }
        self.schedule = BackgroundScheduler(jobstores=self.jobstores)
        self.schedule.start()
        self.conv_handler = ConversationHandler(
            entry_points=[CommandHandler('upcoming', self.upcoming)],
            allow_reentry=True,
            states={
                SCHED: [CallbackQueryHandler(self.remind, pattern=r"^[0-9]*$")]
            },
            fallbacks=[fallback]
        )
        self.conv_handler1 = ConversationHandler(
            entry_points=[CommandHandler('dontRemindMe', self.removeRemind)],
            allow_reentry=True,
            states={
                REMNOTI: [CallbackQueryHandler(self.remnoti, pattern=r'^.*notiplz.*$')]
            },

            fallbacks=[fallback]
        )

    @staticmethod
    def clist_requester(url, payload):
        response = requests.get(url, headers={'Content-Type': 'application/json', 'User-agent': 'Mozilla/5.0'},
                                params=payload, verify=False)
        return response.text

    # COMMAND HANDLER FUNCTION TO SHOW LIST OF ONGOING COMPETITIONS
    @timeouts.wrapper_for_class_methods
    def ongoing(self, bot, update):
        # PARSING JSON
        date1 = update.message.date
        payload = {'limit': '15', 'start__lt': str(date1), 'end__gt': str(date1),
                   'username': self.clist_user_name, 'api_key': self.clist_api_key,
                   'format': 'json', 'order_by': 'end'}
        raw_data = self.clist_requester(url="https://clist.by/api/v1/contest/", payload=payload)
        try:
            json_data = json.loads(raw_data)
            search_results = json_data['objects']
            self.utility.ongoing_sender(update=update, contest_list=search_results)
            self.ong = search_results
        except:
            self.utility.ongoing_sender(update, self.ong)

    @timeouts.wrapper_for_class_methods
    def upcoming(self, bot, update):
        # PARSING JSON
        date1 = update.message.date
        payload = {'limit': '15', 'start__gt': str(date1), 'order_by': 'start',
                   'username': self.clist_user_name,
                   'api_key': self.clist_api_key, 'format': 'json'}
        raw_data = self.clist_requester(url="https://clist.by/api/v1/contest/", payload=payload)
        try:
            json_data = json.loads(raw_data)
            search_results = json_data['objects']
            self.utility.upcoming_sender(update=update, contest_list=search_results)
            self.upc = search_results
        except:
            self.utility.upcoming_sender(update, self.upc)
        return SCHED

    # FUNCTION TO SET REMINDER
    def remind(self, bot, update):
        query = update.callback_query
        msg = query.data
        if str(msg).isdigit():
            msg = int(msg) - 1
            start1 = ContestUtility.time_converter(self.upc[msg]['start'], '-0030')
            dateT = str(self.upc[msg]['start']).replace("T", " ").split(" ")
            start1 = start1.replace("T", " ").split(" ")
            date = dateT[0].split("-")
            date1 = start1[0].split("-")
            time1 = start1[1].split(":")

            cur_time = datetime.now()

            if not cur_time >= datetime(int(date[0]), int(date[1]), int(date[2]), 0, 0):
                self.schedule.add_job(self.remindmsgDay, 'cron', year=date[0], month=date[1], day=date[2], replace_existing=True,
                                 id=str(query.message.chat_id) + str(self.upc[msg]['id']) + "0",
                                 args=[str(query.message.chat_id),
                                       str(self.upc[msg]['event']) + "\n" + str(self.upc[msg]['href'])])
            if not cur_time >= datetime(int(date1[0]), int(date1[1]), int(date1[2]), int(time1[0]), int(time1[1])):
                self.schedule.add_job(self.remindmsg, 'cron', year=date1[0], month=date1[1], day=date1[2], hour=time1[0],
                                 minute=time1[1],
                                 replace_existing=True,
                                 id=str(query.message.chat_id) + str(self.upc[msg]['id']) + "1",
                                 args=[str(query.message.chat_id),
                                       str(self.upc[msg]['event'] + "\n" + str(self.upc[msg]['href']))])
                bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,
                                      text="I will remind you about " + self.upc[msg][
                                          'event'] + "\nYou can use command /dontremindme to cancel reminder")
                if query.message.chat_id < 0:
                    bot.send_message(chat_id=query.message.chat_id,
                                     text="I detected that this is a group. The reminder will be sent to the group. If you want to get reminder personally then use this command in private message")
            else:
                bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,
                                      text="Sorry contest has already started")
        return ConversationHandler.END

    # WHAT HAPPENSWHEN REMINDER IS DEPLOYED
    def remindmsgDay(self, chatId, message):
        self.bot.send_message(chat_id=chatId, text="You have a contest within 24 hours\n " + message)

    def remindmsg(self, chatId, message):
        self.bot.send_message(chat_id=chatId, text="Your contest starts in half an hour\n " + message)

    @timeouts.wrapper_for_class_methods
    def removeRemind(self, bot, update):
        conn = sqlite3.connect(self.mount_point + 'coders1.db')
        c = conn.cursor()
        c.execute("SELECT id FROM apscheduler_jobs WHERE id LIKE  " + "'" + str(
            update.message.chat_id) + "%' AND id LIKE " + "'%1'")
        if c.fetchone():
            c.execute("SELECT id FROM apscheduler_jobs WHERE id LIKE  " + "'" + str(
                update.message.chat_id) + "%' AND id LIKE " + "'%1'")
            a = c.fetchall()
            keyboard = []
            for i in range(0, len(a)):
                s = str(a[i]).replace("('", "").replace("',)", "").replace(
                    '("', "").replace('",)', "")
                print(s)
                keyboard.append([InlineKeyboardButton(str(self.schedule.get_job(job_id=s).args[1].split("\n")[0]),
                                                      callback_data=s[:-1] + "notiplz")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text("Here are your pending reminders\nSelect the reminder you want to remove",
                                      reply_markup=reply_markup)
            c.close()
            return REMNOTI
        else:
            c.close()
            update.message.reply_text("You have no pending reminders")
            return ConversationHandler.END

    def remnoti(self, bot, update):
        query = update.callback_query
        val = str(query.data).replace("notiplz", "")
        try:
            self.schedule.remove_job(val + "0")
        except:
            pass
        try:
            self.schedule.remove_job(val + "1")
        except:
            pass
        bot.edit_message_text(text="Reminder removed", message_id=query.message.message_id,
                              chat_id=query.message.chat_id)
        return ConversationHandler.END
