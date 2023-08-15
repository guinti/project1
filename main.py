import telebot
from telebot import types
import threading
import schedule
import time


from bot_info_file import bot
from menu_file import menu
import stories_file
from stories_file import stories
# import sending_facts
import sqlite3


# conn = sqlite3.connect('base.bd', check_same_thread=False)
# cur = conn.cursor()


@bot.message_handler(commands=['start'])
def start(message):
    registr = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)  # кнопка
    button = types.KeyboardButton('Зарегистрироваться')  # последнее - id кнопки
    registr.add(button)  # добавляем кнопку к созданному "окну" registr
    bot.send_message(message.chat.id, 'Бла-бла-бла наш бот бла-бла-бла',
                     parse_mode='html', reply_markup=registr)
    time.sleep(1)
    options = ["Вариант 1", "Вариант 2", "Вариант 3"]
    bot.send_poll(message.chat.id, "Выберите ваш любимый вариант:", options, is_anonymous=False,
                  allows_multiple_answers=True)


def send_message():
    chat_id = 97124558
    message = "Привет, это сообщение отправлено по расписанию!"
    bot.send_message(chat_id, message)


@bot.message_handler(func=lambda message: message.text.lower() == "меню")
def handle_message(message):
    menu(message)

# @bot.message_handler(func=lambda message: message.text.lower() == "истории пользователей")
# def handle_message(message):
#     stories(message)


# Запускаем планирование в отдельном потоке
# def run_schedule():
#     schedule.every().day.at("16:01").do(send_message)
#     while True:
#         schedule.run_pending()
#         time.sleep(1)


# threading.Thread(target=run_schedule).start()
bot.polling(none_stop=True)
