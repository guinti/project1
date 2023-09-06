from telebot import types
from bot_info_file import bot, conn
import re
import datetime
from calendar_functions import get_days_in_month


@bot.callback_query_handler(func=lambda call: call.data.startswith('add_purpose'))
def purpose_start(call):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM purposes WHERE id=?", (call.from_user.id,))
    if cur.fetchone()[0] == 5:
        bot.edit_message_text("Извините, вы уже установили максимальное количество целей", call.from_user.id,
                              call.message.message_id)
    else:
        def purpose_fill_start(message, user_id):
            cur = conn.cursor()
            cur.execute("SELECT * FROM purposes WHERE id=? AND subgoal_number=?", (user_id, 1))
            row = cur.fetchone()
            subgoal_number = 1
            while row is not None:
                cur.execute("SELECT * FROM purposes WHERE id=? AND subgoal_number=?", (user_id, row[6] + 1))
                subgoal_number = row[6] + 1
                row = cur.fetchone()
            cur.execute("INSERT INTO purposes(id, purpose, done_percentage, purpose_above, part_of_purpose_above,"
                        " subgoal_number) VALUES(?, ?, ?, ?, ?, ?)", (user_id, message, 0, 0, 0, subgoal_number))
            conn.commit()
            cur.close()
            bot.send_message(user_id,
                             "Отлично! Укажите дату, до которой нужно выполнить цель, в формате гггг-мм-дд."
                             " Если ваша цель бессрочна, введите \"-\"")
            bot.register_next_step_handler(call.message,
                                           lambda mess: purpose_fill_1step(mess.text, user_id, subgoal_number))

        def purpose_fill_1step(mess_text, chat_id, subgoal_num):
            subgoals_keyboard = types.InlineKeyboardMarkup()
            subgoals_button = types.InlineKeyboardButton("Добавить подцели",
                                                         callback_data='subgoal_add' + str(subgoal_num))
            subgoals_keyboard.add(subgoals_button)
            if mess_text != '-' and not re.match(r'^\d{4}-\d{2}-\d{2}$', mess_text):
                bot.send_message(chat_id,
                                 "Извините, вы вводите данные не в том формате. Нужно указать дату в формате гггг-мм-дд"
                                 " или ввести \"-\"")
                bot.register_next_step_handler(call.message,
                                               lambda mess: purpose_fill_1step(mess.text, chat_id, subgoal_num))
            elif mess_text == '-':
                bot.send_message(chat_id,
                                 "Отлично, у вас бессрочная цель🎉\n Хотите добавить подцели(до 10)? Так вы с большей"
                                 " вероятностью достигнете результата",
                                 reply_markup=subgoals_keyboard)
            elif re.match(r'^\d{4}-\d{2}-\d{2}$', mess_text):
                year = int(mess_text[:4])
                month = int(mess_text[5:7])
                day = int(mess_text[8:])
                today = datetime.date.today()
                if year < today.year or year > 2100:
                    bot.send_message(chat_id,
                                     "Извините, год не может быть меньше настоящего или больше 2100. Введите дату"
                                     " заново")
                    bot.register_next_step_handler(call.message,
                                                   lambda mess: purpose_fill_1step(mess.text, chat_id, subgoal_num))
                elif month > 12 or month == 0:
                    bot.send_message(chat_id,
                                     "Извините, нет месяца с таким номером. Введите дату заново")
                    bot.register_next_step_handler(call.message,
                                                   lambda mess: purpose_fill_1step(mess.text, chat_id, subgoal_num))
                elif day == 0 or day > get_days_in_month(month, year):
                    bot.send_message(chat_id,
                                     "Извините, в выбранном месяце нет дня с таким номером. Введите дату заново")
                    bot.register_next_step_handler(call.message,
                                                   lambda mess: purpose_fill_1step(mess.text, chat_id, subgoal_num))
                else:
                    date_string = str(year) + "-" + str(month) + "-" + str(day)  # Формат: ГГГГ-ММ-ДД
                    date = datetime.datetime.strptime(date_string, "%Y-%m-%d")
                    if date.date() <= today:
                        bot.send_message(chat_id,
                                         "Извините, вы можете установить дату завершения только большую чем сегодняшняя"
                                         " дата. Введите дату заново")
                        bot.register_next_step_handler(call.message,
                                                       lambda mess: purpose_fill_1step(mess.text, chat_id,
                                                                                       subgoal_num))
                    else:
                        bot.send_message(chat_id,
                                         "Дата завершения установлена✨\n Хотите добавить подцели(до 10)? Так вы с"
                                         " большей вероятностью достигнете результата",
                                         reply_markup=subgoals_keyboard)
                        cur = conn.cursor()
                        cur.execute("UPDATE purposes SET day_finish=? WHERE id=? AND subgoal_number=?",
                                    (date.date(), chat_id, subgoal_num))
                        conn.commit()
                        cur.close()

        bot.edit_message_text("Напишите вашу цель(название/заголовок)", call.from_user.id,
                              call.message.message_id)
        cur.close()
        bot.register_next_step_handler(call.message,
                                       lambda message: purpose_fill_start(message.text, call.from_user.id))


@bot.callback_query_handler(func=lambda call: call.data.startswith('subgoal_add'))
def subpurpose_start(call):
    if call.data[11] != 'i':
        subgoal_number = int(call.data[11:])
    else:
        subgoal_number = int(call.data[12:])
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM purposes WHERE id=? AND purpose_above=?", (call.from_user.id, subgoal_number))
    if cur.fetchone()[0] == 10:
        bot.edit_message_text("Извините, вы уже установили максимальное количество подцелей", call.from_user.id,
                              call.message.message_id)
    else:
        def subpurpose_fill_start(message, user_id, subgoal_num):
            cur = conn.cursor()
            cur.execute("SELECT * FROM purposes WHERE id=? AND subgoal_number=?", (user_id, subgoal_num))
            if cur.fetchone() is None:
                if subgoal_num//10==0:
                    bot.send_message(user_id, "К сожалению, цели, к которой вы пытаетесь добавить"
                                          " подцель больше не существует")
                else:
                    bot.send_message(user_id, "К сожалению, подцели, к которой вы пытаетесь добавить"
                                              " пункт больше не существует")
            else:
                subgoal_num = subgoal_num * 10
                cur.execute("SELECT * FROM purposes WHERE id=? AND subgoal_number=?", (user_id, subgoal_num))
                row = cur.fetchone()
                while row is not None:
                    cur.execute("SELECT * FROM purposes WHERE id=? AND subgoal_number=?", (user_id, row[6] + 1))
                    subgoal_num = row[6] + 1
                    row = cur.fetchone()
                cur.execute("INSERT INTO purposes(id, purpose, done_percentage, purpose_above, part_of_purpose_above,"
                            " subgoal_number) VALUES(?, ?, ?, ?, ?, ?)",
                            (user_id, message, 0, subgoal_num // 10, 0, subgoal_num))
                conn.commit()
                if subgoal_num // 100==0:
                    bot.send_message(user_id,
                                 "Отлично! Укажите дату, до которой нужно выполнить подцель, в формате гггг-мм-дд. "
                                 "Если дедлайн вашей подцели такой же, как у цели, введите \"-\"")
                else:
                    bot.send_message(user_id,
                                     "Отлично! Укажите дату, до которой нужно выполнить пункт, в формате гггг-мм-дд. "
                                     "Если дедлайн вашего пункта такой же, как у подцели, введите \"-\"")
                bot.register_next_step_handler(call.message,
                                               lambda mess: subpurpose_fill_1step(mess.text, user_id, subgoal_num))

                # начало изменения процента выполненого
                goal_above = subgoal_num // 10
                cur.execute("SELECT COUNT(*) FROM purposes WHERE id=? AND purpose_above=?", (user_id, goal_above))
                amount_subgoals = cur.fetchone()[0]
                cur.execute("UPDATE purposes SET part_of_purpose_above=? WHERE id=? AND purpose_above=?",
                            (100 // amount_subgoals, user_id, goal_above))
                conn.commit()
                cur.execute("SELECT * FROM purposes WHERE id=? AND purpose_above=?", (user_id, goal_above))
                rows = cur.fetchall()
                sum_done = 0
                for row in rows:
                    sum_done += row[5] * row[4] // 100
                cur.execute("SELECT * FROM purposes WHERE id=? AND subgoal_number=?", (user_id, goal_above))
                row = cur.fetchone()
                sum_before = row[5] * row[4] // 100
                cur.execute("UPDATE purposes SET done_percentage=? WHERE id=? AND subgoal_number=?",
                            (sum_done, user_id, goal_above))
                conn.commit()
                goal_above = goal_above // 10
                if goal_above != 0:
                    cur.execute("SELECT done_percentage FROM purposes WHERE id=? AND subgoal_number=?",
                                (user_id, goal_above))
                    done_persentage = cur.fetchone()[0]
                    if done_persentage - sum_before + sum_done < 0:
                        cur.execute("UPDATE purposes SET done_percentage=? WHERE id=? AND subgoal_number=?",
                                    (0, user_id, goal_above))
                        conn.commit()
                    if done_persentage - sum_before + sum_done >= 96:
                        cur.execute("UPDATE purposes SET done_percentage=? WHERE id=? AND subgoal_number=?",
                                    (100, user_id, goal_above))
                        conn.commit()
                    else:
                        cur.execute("UPDATE purposes SET done_percentage=? WHERE id=? AND subgoal_number=?",
                                    (done_persentage - sum_before + sum_done, user_id, goal_above))
                        conn.commit()
                cur.close()

        def subpurpose_fill_1step(mess_text, chat_id, subgoal_num):
            cur = conn.cursor()
            cur.execute("SELECT * FROM purposes WHERE id=? AND subgoal_number=?", (chat_id, subgoal_num))
            if cur.fetchone() is None:
                if subgoal_num//100==0:
                    bot.send_message(chat_id,
                                 "К сожалению, подцели, которую вы пытаетесь доработать, больше нет")
                else:
                    bot.send_message(chat_id,
                                     "К сожалению, пункта, который вы пытаетесь доработать, больше нет")
            else:
                cur.execute('SELECT COUNT(*) FROM purposes WHERE id=? AND purpose_above=?',
                            (call.from_user.id, subgoal_num // 10))
                count = cur.fetchone()[0]
                subgoals_keyboard = types.InlineKeyboardMarkup()
                buttons = []
                subgoals_button = types.InlineKeyboardButton("Добавить пункты",
                                                             callback_data='subgoal_add' + str(subgoal_num))
                next_subgoals_button = types.InlineKeyboardButton("Добавить следующую подцель",
                                                                  callback_data='subgoal_add' + str(subgoal_num // 10))
                s_n = subgoal_num
                if subgoal_num > 99:
                    s_n = subgoal_num // 10
                    subgoals_button = types.InlineKeyboardButton("Добавить следующий пункт",
                                                                 callback_data='subgoal_add' + str(subgoal_num // 10))
                    next_subgoals_button = types.InlineKeyboardButton("Добавить следующую подцель",
                                                                      callback_data='subgoal_add' + str(
                                                                          subgoal_num // 100))
                cur.execute('SELECT COUNT(*) FROM purposes WHERE id=? AND purpose_above=?',
                            (call.from_user.id, subgoal_num // 10))
                if s_n < 100:
                    buttons = [subgoals_button]
                if cur.fetchone()[0] < 10:
                    buttons.append(next_subgoals_button)
                subgoals_keyboard.add(*buttons)
                if mess_text != '-' and not re.match(r'^\d{4}-\d{2}-\d{2}$', mess_text):
                    bot.send_message(chat_id,
                                     "Извините, вы вводите данные не в том формате. Нужно указать дату в формате "
                                     "гггг-мм-дд или ввести \"-\"")
                    bot.register_next_step_handler(call.message,
                                                   lambda mess: subpurpose_fill_1step(mess.text, chat_id, subgoal_num))
                elif mess_text == '-':
                    if buttons == []:
                        bot.send_message(chat_id,
                                         "Время для пункта устоновлено✊\n Больше в цель нельзя ничего добавить")
                    elif buttons == [subgoals_button]:
                        bot.send_message(chat_id,
                                         "Время подцели устоновлено🌟\n Хотите добавить пункты(до 10)? Это может"
                                         " вам помочь еще больше. Другие подцели добавить нельзя)",
                                         reply_markup=subgoals_keyboard)
                    elif buttons == [next_subgoals_button]:
                        bot.send_message(chat_id,
                                         "Время подцели устоновлено💫\n Хотите добавить другие подцели(до 10)? "
                                         "Пункты к этой подцели больше добавлять нельзя)",
                                         reply_markup=subgoals_keyboard)
                    else:
                        bot.send_message(chat_id,
                                         "Время подцели устоновлено🐬\n Хотите добавить другие подцели(до 10) или"
                                         " пункты(до 10)?",
                                         reply_markup=subgoals_keyboard)
                    cur.execute("SELECT * FROM purposes WHERE id=? AND subgoal_number=?", (chat_id, subgoal_num // 10))
                    date = cur.fetchone()[3]
                    if date is not None:
                        cur.execute("UPDATE purposes SET day_finish=? WHERE id=? AND subgoal_number=?",
                                    (date, chat_id, subgoal_num))
                        conn.commit()
                elif re.match(r'^\d{4}-\d{2}-\d{2}$', mess_text):
                    year = int(mess_text[:4])
                    month = int(mess_text[5:7])
                    day = int(mess_text[8:])
                    today = datetime.date.today()
                    if year < today.year or year > 2100:
                        bot.send_message(chat_id,
                                         "Извините, год не может быть меньше настоящего или больше 2100."
                                         " Введите дату заново")
                        bot.register_next_step_handler(call.message,
                                                       lambda mess: subpurpose_fill_1step(mess.text, chat_id,
                                                                                          subgoal_num))
                    elif month > 12 or month == 0:
                        bot.send_message(chat_id,
                                         "Извините, нет месяца с таким номером. Введите дату заново")
                        bot.register_next_step_handler(call.message,
                                                       lambda mess: subpurpose_fill_1step(mess.text, chat_id,
                                                                                          subgoal_num))
                    elif day == 0 or day > get_days_in_month(month, year):
                        bot.send_message(chat_id,
                                         "Извините, в выбранном месяце нет дня с таким номером. Введите дату заново")
                        bot.register_next_step_handler(call.message,
                                                       lambda mess: subpurpose_fill_1step(mess.text, chat_id,
                                                                                          subgoal_num))
                    else:
                        date_string = str(year) + "-" + str(month) + "-" + str(day)  # Формат: ГГГГ-ММ-ДД
                        date = datetime.datetime.strptime(date_string, "%Y-%m-%d")
                        if date.date() <= today:
                            bot.send_message(chat_id,
                                             "Извините, вы можете установить дату завершения только большую чем "
                                             "сегодняшняя дата. Введите дату заново")
                            bot.register_next_step_handler(call.message,
                                                           lambda mess: subpurpose_fill_1step(mess.text, chat_id,
                                                                                              subgoal_num))
                        else:
                            cur.execute("SELECT * FROM purposes WHERE id=? AND subgoal_number=?",
                                        (chat_id, subgoal_num // 10))
                            purpose_date = cur.fetchone()[3]
                            if purpose_date is not None and datetime.datetime.strptime(purpose_date, "%Y-%m-%d").date() < date.date():
                                bot.send_message(chat_id, "Нельзя поставить дату, превышающую дату (под)цели")
                                bot.register_next_step_handler(call.message,
                                                               lambda mess: subpurpose_fill_1step(mess.text, chat_id,
                                                                                                  subgoal_num))
                            else:
                                if buttons == []:
                                    bot.send_message(chat_id,
                                                     "Время для пункта устоновлено✊\n Больше в цель нельзя ничего"
                                                     " добавить")
                                elif buttons == [subgoals_button]:
                                    bot.send_message(chat_id,
                                                     "Время подцели устоновлено🌟\n Хотите добавить пункты(до 10)? "
                                                     "Это может вам помочь еще больше. Другие подцели добавить нельзя)",
                                                     reply_markup=subgoals_keyboard)
                                elif buttons == [next_subgoals_button]:
                                    bot.send_message(chat_id,
                                                     "Время подцели устоновлено💫\n Хотите добавить другие подцели"
                                                     "(до 10)? Пункты к этой подцели больше добавлять нельзя)",
                                                     reply_markup=subgoals_keyboard)
                                else:
                                    bot.send_message(chat_id,
                                                     "Время подцели устоновлено🌈\n"
                                                     "Хотите добавить другие подцели(до 10) или пункты(до 10)?",
                                                     reply_markup=subgoals_keyboard)

                                cur.execute("UPDATE purposes SET day_finish=? WHERE id=? AND subgoal_number=?",
                                            (date.date(), chat_id, subgoal_num))
                                conn.commit()
                                cur.close()
        if call.data[11] != 'i':
            bot.edit_message_text("Напишите подцель(название/заголовок)", call.from_user.id,
                                  call.message.message_id)
        else:
            bot.delete_message(call.from_user.id, call.message.message_id)
            bot.send_message(call.from_user.id, "Напишите подцель(название/заголовок)")
        cur.close()
        bot.register_next_step_handler(call.message,
                                       lambda message: subpurpose_fill_start(message.text, call.from_user.id,
                                                                             subgoal_number))
