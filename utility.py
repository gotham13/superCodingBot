"""
Created by Gotham on 31-07-2018.
"""
from datetime import datetime, timedelta
from xlsxwriter.workbook import Workbook
from telegram import ReplyKeyboardRemove
import os
import ratings


class Utility:
    def __init__(self, mount_point):
        self.mount_point = mount_point

    # FUNCTION FOR PAGINATING AND SENDING THE OUTPUT
    @staticmethod
    def paginate(bot, update, result):
        markup = ReplyKeyboardRemove()
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
        if len(output) <= 2897:
            update.message.reply_text("Output:\n" + str(output) + "\n" + "Time: " + str(time1) + "\nMemory: " + str(
                memory1) + "\nMessage: " + str(message1), reply_markup=markup)
        else:
            with open("out.txt", "w") as text_file:
                text_file.write("Output:\n" + str(output) + "\n" + "Time: " + str(time1) + "\nMemory: " + str(
                    memory1) + "\nMessage: " + str(message1))
            bot.send_document(chat_id=update.message.chat_id, document=open('out.txt', 'rb'), reply_markup=markup)
            os.remove('out.txt')

    # FUNCTION TO CREATE XLSX FILES
    @staticmethod
    def xlsx_creator(mysel, file_name):
        workbook = Workbook(file_name)
        worksheet = workbook.add_worksheet()
        format_of_workbook = workbook.add_format()
        format_of_workbook.set_align('top')
        format_of_workbook.set_text_wrap()
        for i, row in enumerate(mysel):
            for j, l in enumerate(row):
                print(l)
                worksheet.write(i, j, row[j], format_of_workbook)
                worksheet.set_row(i, 170)
        worksheet.set_column(0, 5, 40)
        workbook.close()

    # FUNCTION TO RECREATE XLSX FILES
    def recreate_xlsx(self, c):
        mysel = c.execute(
            "SELECT datas.name, datas.HE, datas.HR, datas.SP, datas.CF, datas.CC FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority.CF AS FLOAT) DESC, CAST(priority.CC AS FLOAT) DESC, CAST(priority.HR AS FLOAT) DESC, CAST(priority.HE AS FLOAT) DESC")
        self.xlsx_creator(mysel, self.mount_point + 'all.xlsx')
        mysel = c.execute(
            "SELECT datas.name, datas.HE FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority.HE AS FLOAT) DESC")
        self.xlsx_creator(mysel, self.mount_point + "HE.xlsx")
        mysel = c.execute(
            "SELECT datas.name, datas.HR FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority.HR AS FLOAT) DESC")
        self.xlsx_creator(mysel, self.mount_point + "HR.xlsx")
        mysel = c.execute("SELECT name, SP FROM datas")
        self.xlsx_creator(mysel, self.mount_point + "SP.xlsx")
        mysel = c.execute(
            "SELECT datas.name, datas.CF FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority.CF AS FLOAT) DESC")
        self.xlsx_creator(mysel, self.mount_point + "CF.xlsx")
        mysel = c.execute(
            "SELECT datas.name, datas.CC FROM datas INNER JOIN priority ON datas.id=priority.id ORDER BY CAST(priority.CC AS FLOAT) DESC")
        self.xlsx_creator(mysel, self.mount_point + "CC.xlsx")

    # COMMON UPDATE FUNCTION
    def update_function(self, c):
        rating_obj = ratings.Rating()
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
                    all_data = rating_obj.hackerearth(str(row[wo]))
                    if not all_data is None:
                        he = all_data
                elif wo == 2 and (row[wo] != '' and row[wo] is not None):
                    all_data = rating_obj.hackerrank(str(row[wo]))
                    if not all_data is None:
                        hr = all_data
                elif wo == 3 and (row[wo] != '' and row[wo] is not None):
                    count = 0
                    while count < 5:
                        all_data = rating_obj.codechef(row[wo])
                        if all_data is not None:
                            cc = all_data
                            break
                        else:
                            count = count + 1
                            continue
                elif wo == 4 and (row[wo] != '' and row[wo] is not None):
                    all_data = rating_obj.spoj(str(row[wo]))
                    if all_data is not None:
                        sp = all_data
                elif wo == 5 and (row[wo] != '' and row[wo] is not None):
                    all_data = rating_obj.codeforces(str(row[wo]))
                    if all_data is not None:
                        cf = all_data
            if not he == '' or (he == '' and (row[1] == '' or row[1] is None)):
                c.execute("UPDATE datas SET HE=(?) WHERE id=(?)", (he, str(a)))
                rating = rating_obj.rating_hackerearth(he)
                if not rating is None:
                    c.execute("UPDATE  priority SET HE = (?) WHERE id = (?) ", (rating, str(a)))
            if not hr == '' or (hr == '' and (row[2] == '' or row[2] is None)):
                c.execute("UPDATE datas SET HR=(?) WHERE id=(?)", (hr, str(a)))
                rating = rating_obj.rating_hackerrank(hr)
                if not rating is None:
                    c.execute("UPDATE  priority SET HR = (?) WHERE id = (?) ", (rating, str(a)))
            if not cf == '' or (cf == '' and (row[5] == '' or row[5] is None)):
                c.execute("UPDATE datas SET CF=(?) WHERE id=(?)", (cf, str(a)))
                rating = rating_obj.rating_codeforces(cf)
                if rating is not None:
                    c.execute("UPDATE  priority SET CF = (?) WHERE id = (?) ", (rating, str(a)))
            if not cc == '' or (cc == '' and (row[3] == '' or row[3] is None)):
                c.execute("UPDATE datas SET CC=(?) WHERE id=(?)", (cc, str(a)))
                rating = rating_obj.rating_codechef(cc)
                if rating is not None:
                    c.execute("UPDATE  priority SET CC = (?) WHERE id = (?) ", (rating, str(a)))
            if sp != '' or (sp == '' and (row[4] == '' or row[4] is None)):
                c.execute("UPDATE datas SET SP=(?) WHERE id=(?)", (sp, str(a)))
        # RECREATING ALL THE XLSX FILES
        self.recreate_xlsx(c)

    # FUNCTION TO CONVERT TIME FROM UTC TO OTHER TIME ZONE
    @staticmethod
    def time_converter(old_time, time_zone):
        time_zone = float(time_zone[:3] + ('.5' if time_zone[3] == '3' else '.0'))
        str_time = datetime.strptime(old_time, "%Y-%m-%dT%H:%M:%S")
        return (str_time + timedelta(hours=time_zone)).strftime("%Y-%m-%dT%H:%M:%S")
