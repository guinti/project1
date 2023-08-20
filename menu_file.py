from telebot import types
from bot_info_file import bot


def menu(message):
    menu_keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True, one_time_keyboard=False)
    button_stories = types.KeyboardButton('Истории пользователей')
    button_calendar = types.KeyboardButton('Календарь')
    button_chat = types.KeyboardButton('Чат')
    button_methods = types.KeyboardButton('Методики')
    button_goal = types.KeyboardButton('Редактор целей')
    # мб надо добавить кнопку для перепрохождения теста( или просто прописать что есть команда start)
    menu_keyboard.add(button_calendar, button_methods, button_chat, button_goal, button_stories)
    text = '\"МУР\"'
    bot.send_message(message.chat.id, text, reply_markup=menu_keyboard)
