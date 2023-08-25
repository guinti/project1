from telebot import types
from bot_info_file import bot, conn
from targets_functions import start_targets_keyboard

cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS methods(text varchar, theme integer, number integer)")



@bot.message_handler(func=lambda message: message.text.lower() == "методики")
def methods(message):
    methods_keyboard = types.InlineKeyboardMarkup(row_width=2)
    button_calm = types.InlineKeyboardButton("Успокоиться", callback_data="metods10")
    button_productive = types.InlineKeyboardButton("Повысить продуктивность", callback_data="metods20")
    button_understand = types.InlineKeyboardButton("Разобраться с лишними мыслями", callback_data="metods30")
    button_over_productive = types.InlineKeyboardButton("Отдохнуть", callback_data="metods40")
    methods_keyboard.add(button_calm, button_productive, button_understand, button_over_productive)
    bot.send_message(message.chat.id, "Чего вы хотите?", reply_markup=methods_keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('metods'))
def show_methods(call):
    methods_theme=int(call.data[6])
    method_number=int(call.data[7])+1
    cur=conn.cursor()
    cur.execute("SELECT text FROM methods WHERE theme=? AND number=?", (methods_theme, method_number))
    text=cur.fetchone()[0]
    methods_show_keyboard = types.InlineKeyboardMarkup(row_width=2)
    back_to_themes_button=types.InlineKeyboardButton('←', callback_data='back_to_themes')
    cur.execute("SELECT text FROM methods WHERE theme=? AND number=?", (methods_theme, method_number+1))
    if cur.fetchone() is None:
        method_number=0
    next_method_button=types.InlineKeyboardButton('Другой метод', callback_data="metods"+str(methods_theme)+str(method_number))
    methods_show_keyboard.add(back_to_themes_button, next_method_button)
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=methods_show_keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('back_to_themes'))
def methods(call):
    methods_keyboard = types.InlineKeyboardMarkup(row_width=2)
    button_calm = types.InlineKeyboardButton("Успокоиться", callback_data="metods10")
    button_productive = types.InlineKeyboardButton("Повысить продуктивность", callback_data="metods20")
    button_understand = types.InlineKeyboardButton("Разобраться с лишними мыслями", callback_data="metods30")
    button_over_productive = types.InlineKeyboardButton("Отдохнуть", callback_data="metods40")
    methods_keyboard.add(button_calm, button_productive, button_understand, button_over_productive)
    bot.edit_message_text("Чего вы хотите?", call.from_user.id, call.message.message_id, reply_markup=methods_keyboard)