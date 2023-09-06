from telebot import types
from bot_info_file import bot


def menu(message):
    menu_keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True, one_time_keyboard=False)
    button_stories = types.KeyboardButton('Истории пользователей')
    button_calendar = types.KeyboardButton('Календарь')
    button_chat = types.KeyboardButton('Чат')
    button_methods = types.KeyboardButton('Методики')
    button_goal = types.KeyboardButton('Редактор целей')
    menu_keyboard.add(button_calendar, button_methods, button_chat, button_goal, button_stories)
    text = 'Есть 5 разделов бота, все они представлены кнопками под окошком ввода. Кроме кнопок меню есть так же функция /start, ее можно использовать для перепрохождения начального теста.'
    bot.send_message(message, text, reply_markup=menu_keyboard)
