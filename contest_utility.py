"""
Created by Gotham on 25-08-2018.
"""
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utility import Utility


class ContestUtility(Utility):

    @staticmethod
    def contest_parser(contest):
        title = contest['event']
        start = contest['start']
        sec = timedelta(seconds=int(contest['duration']))
        d = datetime(1, 1, 1) + sec
        duration = ("%d days %d hours %d min" % (d.day - 1, d.hour, d.minute))
        host = contest['resource']['name']
        contest1 = contest['href']
        start1 = Utility.time_converter(start, '+0530')
        return {"title": title, "start": start, "duration": duration,
                "host": host, "contest": contest1, "start1": start1}

    def ongoing_sender(self, update, contest_list):
        i = 0
        s = ""
        for er in contest_list:
            i = i + 1
            if i == 16:
                break
            parsed_contest = self.contest_parser(er)
            s = s + parsed_contest["title"] + "\n" + "Start:\n" + parsed_contest["start"].replace("T", " ") + \
                " GMT\n" + str(parsed_contest["start1"]).replace("T", " ") + \
                " IST\n" + "Duration:" + parsed_contest["duration"] + "\n" \
                + parsed_contest["host"] + "\n" + parsed_contest["contest"] + "\n\n"
        update.message.reply_text(s)

    def upcoming_sender(self, update, contest_list):
        i = 0
        s = ""
        keyboard = []
        keyboard1 = []
        for er in contest_list:
            i = i + 1
            # LIMITING NO OF EVENTS TO 20
            if i == 16:
                break
            parsed_contest = self.contest_parser(er)
            s = s + str(i) + ". " + parsed_contest["title"] + "\n" + "Start:\n" + \
                parsed_contest["start"].replace("T", " ")\
                + " GMT\n" + str(parsed_contest["start1"]).replace("T", " ") + " IST\n" + \
                "Duration: " + str(parsed_contest["duration"]) + "\n" + \
                parsed_contest["host"] + "\n" + parsed_contest["contest"] + "\n\n"
            keyboard1.append(InlineKeyboardButton(str(i), callback_data=str(i)))
            if i % 5 == 0:
                keyboard.append(keyboard1)
                keyboard1 = []
        keyboard.append(keyboard1)
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(s + "Select competition number to get notification" + "\n\n",
                                  reply_markup=reply_markup)
