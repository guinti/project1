from telebot import types
import datetime
from bot_info_file import bot, conn
from calendar_functions import calendar_keyboard
from calendar_functions import day_step
from calendar_functions import smile_step


@bot.message_handler(func=lambda message: message.text.lower() == "календарь")
def calendar(message):
    today = datetime.date.today()
    month = today.month
    year = today.year
    keyboard = calendar_keyboard(year, month, message.chat.id)
    bot.send_message(message.chat.id, "Календарь настроения", reply_markup=keyboard)  # исправить


@bot.callback_query_handler(func=lambda call: call.data.startswith('calendar'))
def another_months(call):
    year = int(call.data[8:12])
    month = int(call.data[12:])
    keyboard = calendar_keyboard(year, month, call.from_user.id)
    bot.edit_message_text("Календарь настроения", call.message.chat.id,
                          call.message.message_id, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('day'))
def day_info(call):
    year = int(call.data[3:7])
    if call.data[8] == '_':
        month = int(call.data[7])
        day = int(call.data[9:])
    else:
        month = int(call.data[7:9])
        day = int(call.data[10:])
    today=datetime.date.today()
    date_string = str(year) + "-" + str(month) + "-" + str(day)  # Формат: ГГГГ-ММ-ДД
    date = datetime.datetime.strptime(date_string, "%Y-%m-%d")
    if date.date() <= today:
        cur = conn.cursor()
        cur.execute("SELECT * FROM calendar WHERE id=? AND year=? AND month=? AND day=?",
                    (call.from_user.id, year, month, day))
        row = cur.fetchone()
        day_keyboard = types.InlineKeyboardMarkup()
        button_back = types.InlineKeyboardButton('←', callback_data='calendar' + str(year) + str(month))
        message_text = "Заполнить"
        text = str(day) + '-' + str(month) + '-' + str(year) + '\nЗдесь пока ничего нет🙂😉'
        key_text = 'that_day'
        if row is not None:
            text = str(day) + '-' + str(month) + '-' + str(year) + ' ' + row[1] + '\n' + "Настроение: " + str(
                row[6]) + " из 5\n" + row[2]
            message_text = 'Изменить'
            key_text += 'i'
        if row is not None and row[2] == '' and row[1] != '':
            text = row[1]
        button_change = types.InlineKeyboardButton(message_text,
                                                   callback_data=key_text + str(year) + str(month) + '_' + str(day))
        day_keyboard.add(button_back, button_change)
        bot.edit_message_text(text, call.message.chat.id,
                              call.message.message_id, reply_markup=day_keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('that_day'))
def day_change(call):
    if call.data[8] == 'i':
        year = int(call.data[9:13])
        if call.data[14] == '_':
            month = int(call.data[13])
            day = int(call.data[15:])
        else:
            month = int(call.data[13:15])
            day = int(call.data[16:])
        cur = conn.cursor()
        cur.execute("SELECT * FROM calendar WHERE id=? AND year=? AND month=? AND day=?",
                    (call.from_user.id, year, month, day))
        row = cur.fetchone()
        text = str(day) + '-' + str(month) + '-' + str(year) + ' ' + row[1] + '\n' + "Настроение: " + str(
                row[6]) + " из 5\n" + row[2]
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id)
        bot.send_message(call.from_user.id,
                         "Измените свою запись:\n Удалить запись(полностью): отправьте сообщение из \".\"(точки).\n"
                         "Изменить текст: хотите удалить текст - отправьте \"-\", иначе просто напишите исправленный текст(максимальная длина 4000 символов)\n"
                         "Изменить смайлик: напишите перед новым \"/\" и отправьте.")
        bot.register_next_step_handler(call.message, lambda message: day_step(message.text, row))
        cur.close()
    else:
        date = call.data[8:]
        keyboard = types.InlineKeyboardMarkup(row_width=5)
        button_1 = types.InlineKeyboardButton('🥰',
                                              callback_data='mood' + '5' + date)
        button_2 = types.InlineKeyboardButton('😌',
                                              callback_data='mood' + '4' + date)
        button_3 = types.InlineKeyboardButton('😐',
                                              callback_data='mood' + '3' + date)
        button_4 = types.InlineKeyboardButton('😕',
                                              callback_data='mood' + '2' + date)
        button_5 = types.InlineKeyboardButton('☹️',
                                              callback_data='mood' + '1' + date)
        keyboard.add(button_1, button_2, button_3, button_4, button_5)
        bot.edit_message_text('Моё настроение:', call.message.chat.id,
                              call.message.message_id, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('mood'))
def start_diary(call):
    mood = call.data[4]
    text = call.data[5:]
    year = int(call.data[5:9])
    if call.data[10] == '_':
        month = int(call.data[9])
        day = int(call.data[11:])
    else:
        month = int(call.data[9:11])
        day = call.data[12:]
    cur = conn.cursor()
    cur.execute("INSERT INTO calendar (id, mood, year, month, day, notes, smile) VALUES(?, ?, ?, ?, ?, ?, ?)",
                (call.from_user.id, mood, year, month, day, '', ''))
    conn.commit()
    cur.close()
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Заполнить дневник", callback_data='diary' + text)
    keyboard.add(button)
    bot.edit_message_text("бла бла бла что-то там(если дневник не заполнить, ляляля)", call.message.chat.id,
                          call.message.message_id, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('diary'))
def start_diary(call):
    year = int(call.data[5:9])
    if call.data[10] == '_':
        month = int(call.data[9])
        day = int(call.data[11:])
    else:
        month = int(call.data[9:11])
        day = call.data[12:]
    cur = conn.cursor()
    cur.execute("SELECT * FROM calendar WHERE id=? AND year=? AND month=? AND day=?",
                (call.from_user.id, year, month, day))
    row = cur.fetchone()
    cur.close()
    bot.edit_message_text(
        "Выберите смайлик, который будет отображаться на календаре. Если вы напишите \"-\", то будет поставлен смайлик, соответствующий вашему настроению",
        call.message.chat.id,
        call.message.message_id)
    bot.register_next_step_handler(call.message, lambda message: smile_step(message.text, row, call))
