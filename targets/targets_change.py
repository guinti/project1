from telebot import types
from bot_info_file import bot, conn
import re
import datetime
from calendar_functions import get_days_in_month


@bot.callback_query_handler(func=lambda call: call.data.startswith('purp_change'))
def purpose_change(call):
    purp_num = call.data[11:]
    button_back = types.InlineKeyboardButton('←', callback_data="purpose" + purp_num)
    change_name = types.InlineKeyboardButton('Название', callback_data="purp_name_change" + purp_num)
    change_data = types.InlineKeyboardButton('Дата', callback_data='purp_data_change' + purp_num)
    keyboard_change_purpose = types.InlineKeyboardMarkup()
    keyboard_change_purpose.add(change_name, change_data)
    keyboard_change_purpose.add(button_back)
    cur = conn.cursor()
    cur.execute("SELECT * FROM purposes WHERE id=? AND subgoal_number=?", (call.from_user.id, int(purp_num)))
    row = cur.fetchone()
    cur.close()
    if row is not None:
        bot.send_message(call.from_user.id,
                         row[1] + " " + row[3] + '\nВы можете изменить дату завершения или название. Выберите:',
                         reply_markup=keyboard_change_purpose)
    bot.delete_message(call.from_user.id, call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('purp_name_change'))
def purpose_change_name(call):
    subpurpose_number = int(call.data[16:])
    cur = conn.cursor()
    cur.execute("SELECT * FROM purposes WHERE id=? AND subgoal_number=?", (call.from_user.id, subpurpose_number))
    row = cur.fetchone()
    if row is not None:
        def purpose_name_start(message, row):
            cur = conn.cursor()
            cur.execute("UPDATE purposes SET purpose=? WHERE id=? AND subgoal_number=?", (message, row[2], row[6]))
            conn.commit()
            bot.send_message(row[2], "Название обновлено:()")
            cur.close()

        bot.edit_message_text("Напишите новое название", call.from_user.id, call.message.message_id)
        bot.register_next_step_handler(call.message,
                                       lambda message: purpose_name_start(message.text, row))
    else:
        bot.delete_message(call.from_user.id, call.message.message_id)
    cur.close()


@bot.callback_query_handler(func=lambda call: call.data.startswith('purp_data_change'))
def purpose_change_data(call):
    subpurpose_number = int(call.data[16:])
    cur = conn.cursor()
    cur.execute("SELECT * FROM purposes WHERE id=? AND subgoal_number=?", (call.from_user.id, subpurpose_number))
    row = cur.fetchone()
    if row is not None:
        def purpose_data_start(message, row):
            if re.match(r'^\d{4}-\d{2}-\d{2}$', message):
                year = int(message[:4])
                month = int(message[5:7])
                day = int(message[8:])
                today = datetime.date.today()
                if year < today.year or year > 2100:
                    bot.send_message(call.from_user.id,
                                     "Извините, год не может быть меньше настоящего или больше 2100. Введите дату"
                                     " заново")
                    bot.register_next_step_handler(call.message,
                                                   lambda mess: purpose_data_start(mess.text, row))
                elif month > 12 or month == 0:
                    bot.send_message(call.from_user.id,
                                     "Извините, нет месяца с таким номером. Введите дату заново")
                    bot.register_next_step_handler(call.message,
                                                   lambda mess: purpose_data_start(mess.text, row))
                elif day == 0 or day > get_days_in_month(month, year):
                    bot.send_message(call.from_user.id,
                                     "Извините, в выбранном месяце нет дня с таким номером. Введите дату заново")
                    bot.register_next_step_handler(call.message,
                                                   lambda mess: purpose_data_start(mess.text, row))
                else:
                    date_string = str(year) + "-" + str(month) + "-" + str(day)  # Формат: ГГГГ-ММ-ДД
                    date = datetime.datetime.strptime(date_string, "%Y-%m-%d")
                    if date.date() <= today:
                        bot.send_message(call.from_user.id,
                                         "Дата должна быть больше сегодняшней")
                        bot.register_next_step_handler(call.message,
                                                       lambda mess: purpose_data_start(mess.text, row))
                    else:
                        cur = conn.cursor()
                        cur.execute("UPDATE purposes SET day_finish=? WHERE id=? AND subgoal_number=?",
                                    (message, row[2], row[6]))
                        conn.commit()
                        cur.close()
                        bot.send_message(row[2], 'Вы изменили дату')
            else:
                bot.send_message(row[2], 'Нужно ввести данные в формате гггг-мм-дд. Попробуйте еще раз')
                bot.register_next_step_handler(call.message,
                                               lambda message: purpose_data_start(message.text, row))

        bot.edit_message_text("Введите новую дату", call.from_user.id, call.message.message_id)
        bot.register_next_step_handler(call.message,
                                       lambda message: purpose_data_start(message.text, row))
    else:
        bot.delete_message(call.from_user.id, call.message.message_id)
    cur.close()
