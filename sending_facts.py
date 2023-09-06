import schedule
import time
from bot_info_file import bot, conn
import datetime
from telebot import types
import random


def send_message_calendar():
    cur = conn.cursor()
    cur.execute("SELECT * FROM test_results")
    rows = cur.fetchall()
    today = datetime.date.today()
    date_string = str(today.year) + str(today.month) + "_" + str(today.day)
    for row in rows:
        keyboard_day = types.InlineKeyboardMarkup()
        button_day = types.InlineKeyboardButton('Заполнить', callback_data='that_day' + date_string)
        keyboard_day.add(button_day)
        bot.send_message(row[0], "Заполните сегодняшний день в календаре?", reply_markup=keyboard_day)
    cur.close()


def send_message_facts():
    cur = conn.cursor()
    cur.execute("SELECT * FROM test_results")
    rows = cur.fetchall()
    for row in rows:
        cur.execute("SELECT * FROM facts WHERE question_1=? OR question_2=? OR question_3=? OR question_4=?"
                    " OR question_1=? OR question_2=? OR question_3=? OR question_4=?", (row[1], row[2],
                                                                                         row[3], row[4],
                                                                                         11, 11, 11, 11))
        facts = cur.fetchall()
        cur.execute("SELECT COUNT(*) FROM facts WHERE question_1=? OR question_2=? OR question_3=? OR question_4=?"
                    " OR question_1=? OR question_2=? OR question_3=? OR question_4=?", (row[1], row[2],
                                                                                         row[3], row[4],
                                                                                         11, 11, 11, 11))
        number = random.randint(0, cur.fetchone()[0] - 1)
        bot.send_message(row[0], facts[number][0])
    cur.close()


def send_message_purpose():
    cur = conn.cursor()
    cur.execute("SELECT * FROM test_results")
    rows = cur.fetchall()
    for row in rows:
        cur.execute("SELECT COUNT(*) FROM purposes WHERE id=? AND purpose_above=? AND done_percentage!=?", (row[0], 0,
                                                                                                            100))
        amount = cur.fetchone()
        if amount is not None and amount[0] != 0:
            keyboard = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton('Цели', callback_data='purp_start')
            keyboard.add(button)
            text = "У вас несколько(" + str(
                amount[0]) + ") незаконченных целей. Хотите посмотреть, что вам еще нужно сделать?"
            bot.send_message(row[0], text, reply_markup=keyboard)


def send_message_purpose2(question_3, question_4):
    cur = conn.cursor()
    cur.execute("SELECT * FROM test_results WHERE question_3=? OR question_4=?", (question_3, question_4))
    rows = cur.fetchall()
    for row in rows:
        cur.execute("SELECT COUNT(*) FROM purposes WHERE id=? AND purpose_above=? AND done_percentage<?", (row[0], 0,
                                                                                                           100))
        amount = cur.fetchone()
        if amount is not None and amount[0] != 0:
            keyboard = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton('Цели', callback_data='purp_start')
            keyboard.add(button)
            text = "У вас " + str(amount[0]) + " незаконченных целей. Хотите посмотреть, что вам еще нужно сделать?"
            bot.send_message(row[0], text, reply_markup=keyboard)


# Запускаем планирование в отдельном потоке
def run_schedule():
    schedule.every().day.at("09:00").do(send_message_facts)
    schedule.every().day.at('13:03').do(send_message_purpose)
    schedule.every().day.at('14:00').do(lambda: send_message_purpose2(1, 1))
    schedule.every().day.at('18:00').do(lambda: send_message_purpose2(2, 1))
    schedule.every().day.at('21:00').do(lambda: send_message_purpose2(0, 2))
    schedule.every().day.at('21:30').do(send_message_calendar)
    while True:
        schedule.run_pending()
        time.sleep(1)
