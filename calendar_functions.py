from telebot import types
from bot_info_file import bot, conn
import datetime


months_of_a_year = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь",
                    "Ноябрь",
                    "Декабрь"]


def get_days_in_month(month, year):
    if month in [1, 3, 5, 7, 8, 10, 12]: return 31
    if month in [4, 6, 9, 11]: return 30
    if month == 2:
        if year in [2024, 2028, 2032, 2036, 2040, 2044, 2048, 2052, 2056, 2060, 2064, 2068, 2072, 2076, 2080, 2084, 2088, 2092, 2096, 2100]:
            return 29
        else:
            return 28


def calendar_keyboard(year, month, chat_id):
    button_month = types.InlineKeyboardButton(months_of_a_year[month - 1] + ' ' + str(year),
                                              callback_data='month' + str(year) + months_of_a_year[month - 1])
    cur = conn.cursor()
    cur.execute("SELECT * FROM calendar WHERE id=? AND (year<? OR (year=? AND month<?))",
                (chat_id, year, year, month))
    rows = cur.fetchall()
    buttons = []
    if rows != []:
        row = rows[-1]
        button_left = types.InlineKeyboardButton('←', callback_data='calendar' + str(row[3]) + str(
            row[4]))  # год и месяц предыдущего заполнения
        buttons.append(button_left)
    buttons.append(button_month)
    cur.execute("SELECT * FROM calendar WHERE id=? AND (year>? OR (year=? AND month>?))",
                (chat_id, year, year, month))
    row = cur.fetchone()
    if row is not None:
        button_right = types.InlineKeyboardButton('→', callback_data='calendar' + str(row[3]) + str(
            row[4]))  # год и месяц следующего заполнения
        buttons.append(button_right)
    today = datetime.date.today()
    today_month = today.month
    today_year = today.year
    if row is None and (today_year > year or (today_month > month and today_year == year)):
        button_right = types.InlineKeyboardButton('→', callback_data='calendar' + str(today_year) + str(
            today_month))  # год и месяц следующего заполнения
        buttons.append(button_right)
    calendar_keyboard = types.InlineKeyboardMarkup(row_width=7)
    calendar_keyboard.add(*buttons)

    date_string = str(year) + "-" + str(month) + "-01"  # Формат: ГГГГ-ММ-ДД
    date = datetime.datetime.strptime(date_string, "%Y-%m-%d")
    day_of_week = date.weekday()  # Получаем номер дня недели (понедельник - 0, воскресенье - 6)
    days_in_month = get_days_in_month(month, year)

    day = 1
    next_buttons = []
    last = days_in_month + 7 - (day_of_week + days_in_month) % 7
    number_day = day_of_week
    while number_day != 0:
        button_nothing = types.InlineKeyboardButton(" ", callback_data='nothing')
        next_buttons.append(button_nothing)
        number_day -= 1
    while last >= 0:
        if day > days_in_month:
            if last != 0:
                button_nothing = types.InlineKeyboardButton(" ", callback_data='nothing')
                next_buttons.append(button_nothing)
        else:
            cur.execute("SELECT * FROM calendar WHERE id=? AND YEAR=? AND month =? AND day=?",
                        (chat_id, year, month, day))
            row = cur.fetchone()
            if row is not None:
                button_day = types.InlineKeyboardButton(str(day) + "\n " + row[1],
                                                        callback_data='day' + str(year) + str(month) + '_' + str(day))
            else:
                button_day = types.InlineKeyboardButton(str(day),
                                                        callback_data='day' + str(year) + str(month) + '_' + str(day))
            next_buttons.append(button_day)
        day += 1
        day_of_week += 1
        last -= 1
    cur.close()
    calendar_keyboard.add(*next_buttons)
    button_graph_info = types.InlineKeyboardButton("График настроения за последние:", callback_data='nothing')
    calendar_keyboard.add(button_graph_info)
    button_graph_12 = types.InlineKeyboardButton("1 год", callback_data='graph' + 'g' + str(year) + str(month))
    button_graph_6 = types.InlineKeyboardButton("6 месяцев", callback_data='graph' + '6' + str(year) + str(month))
    button_graph_3 = types.InlineKeyboardButton("3 месяца", callback_data='graph' + '3' + str(year) + str(month))
    button_graph_1 = types.InlineKeyboardButton("1 месяц", callback_data='graph' + '1' + str(year) + str(month))

    return calendar_keyboard.add(button_graph_12, button_graph_6, button_graph_3, button_graph_1)


def day_step(message, row):
    cur = conn.cursor()
    if message == '.':
        cur.execute('DELETE FROM calendar WHERE id=? AND year=? AND month=? AND day=?',
                    (row[0], row[3], row[4], row[5]))
        conn.commit()
        bot.send_message(row[0], 'Запись удалена')
    elif message == '-':
        cur.execute('UPDATE calendar SET notes=? WHERE id=? AND year=? AND month=? AND day=?',
                    ('', row[0], row[3], row[4], row[5]))
        conn.commit()
        bot.send_message(row[0], 'Текст удален')
    elif message[0] == '/':
        cur.execute('UPDATE calendar SET smile=? WHERE id=? AND year=? AND month=? AND day=?',
                    (message[1:], row[0], row[3], row[4], row[5]))
        conn.commit()
        bot.send_message(row[0], 'Смайлик изменен')
    else:
        cur.execute('UPDATE calendar SET notes=? WHERE id=? AND year=? AND month=? AND day=?',
                    (message, row[0], row[3], row[4], row[5]))
        conn.commit()
        bot.send_message(row[0], 'Запись изменена')
    cur.close()


def smile_step(message, row, call):
    smiles = ['☹️', '😕', '😐', '😌', '🥰']
    cur = conn.cursor()
    if message == '-':
        cur.execute("UPDATE calendar SET smile=? WHERE id=? AND year=? AND month=? AND day=?",
                    (smiles[int(row[6]) - 1], row[0], row[3], row[4], row[5]))
        conn.commit()
    else:
        cur.execute("UPDATE calendar SET smile=? WHERE id=? AND year=? AND month=? AND day=?",
                    (message, row[0], row[3], row[4], row[5]))
        conn.commit()
    cur.close()
    bot.send_message(row[0],
                     "Напишите запись для дневника. Если хотите оставить ее пустой, напишите '-'. Максимальное количество символов - 4096")
    bot.register_next_step_handler(call.message, lambda message: dairy_step(message.text, row))


def dairy_step(message, row):
    cur = conn.cursor()
    if message == '-':
        cur.execute("UPDATE calendar SET notes=? WHERE id=? AND year=? AND month=? AND day=?",
                    ("", row[0], row[3], row[4], row[5]))
    else:
        cur.execute("UPDATE calendar SET notes=? WHERE id=? AND year=? AND month=? AND day=?",
                    (message, row[0], row[3], row[4], row[5]))
    conn.commit()
    bot.send_message(row[0], "Ура! Сделана запись за " + str(row[5]) + '-' + str(row[4]) + '-' + str(row[3]))
