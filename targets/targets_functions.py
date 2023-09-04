from telebot import types
from bot_info_file import bot, conn


def start_targets_keyboard(rows, id, message_id, k):
    targets_keyboard = types.InlineKeyboardMarkup(row_width=1)
    if rows:
        buttons = []
        amount = len(rows)
        for row in rows:
            text = ""
            if row[4] == 100:
                text = "🥇"
            button_goal = types.InlineKeyboardButton(row[1] + " " + text, callback_data="purpose" + str(row[6]))
            buttons.append(button_goal)
        if amount < 5:
            button_add_goal = types.InlineKeyboardButton("Добавить цель", callback_data="add_purpose")
            buttons.append(button_add_goal)
        targets_keyboard.add(*buttons)
        if k == 1:
            bot.send_message(id, "Ура, возвращаемся к вашим целям!)",
                             reply_markup=targets_keyboard)  # исправить
        else:
            bot.edit_message_text("Ура, возвращаемся к вашим целям!)", id, message_id, reply_markup=targets_keyboard)
    else:
        button_add_goal = types.InlineKeyboardButton("Добавить цель", callback_data="add_purpose")
        targets_keyboard.add(button_add_goal)
        if k == 1:
            bot.send_message(id, "Вы пока не установили цели. Самое время записать первую;)",
                             reply_markup=targets_keyboard)
        else:
            bot.edit_message_text("Вы пока не установили цели. Самое время записать первую;)", id, message_id,
                                  reply_markup=targets_keyboard)


def send_purposes(sub_number, call):
    started_number = sub_number
    cur = conn.cursor()
    text = ''
    buttons = []
    cur.execute("SELECT * FROM purposes WHERE id=? AND subgoal_number=?", (call.from_user.id, sub_number))
    if cur.fetchone() is not None:
        button_back = types.InlineKeyboardButton('←', callback_data="purpose" + str(int(started_number) // 10))
        if len(sub_number) == 3:
            cur.execute("SELECT * FROM purposes WHERE id=? AND subgoal_number=?", (call.from_user.id, sub_number))
            row = cur.fetchone()
            text = '\n            ' + row[1]
            if row[4] == 100:
                text += '  ✅'
            elif row[3] is not None:
                text += '   ' + row[3]
            sub_number = sub_number[0:2]

        if len(sub_number) == 2:
            cur.execute("SELECT * FROM purposes WHERE id=? AND subgoal_number=?", (call.from_user.id, sub_number))
            row = cur.fetchone()
            text1 = row[1]
            if row[4] == 100:
                text1 += '  ✅'
            else:
                text1 += '   ' + str(row[4]) + '%'
            if row[3] is not None and row[4] != 100:
                text1 += '   ' + row[3]
            text3 = '\n        ' + text1
            if text == '':
                cur.execute("SELECT * FROM purposes WHERE id=? AND purpose_above=?", (call.from_user.id, sub_number))
                rows = cur.fetchall()
                if rows:
                    text1 = ''
                    text2 = ''
                    t = 0
                    for row in rows:
                        t += 1
                        if row[4] == 100:
                            text1 += '\n            ' + str(t) + ")" + row[1] + '  ✅'
                        elif row[3] is not None:
                            text2 += '\n            ' + str(t) + ")" + row[1] + '   ' + row[3]
                        else:
                            text2 += '\n            ' + str(t) + ")" + row[1]
                        button_subpurpose = types.InlineKeyboardButton(str(t), callback_data='purpose' + str(row[6]))
                        buttons.append(button_subpurpose)
                    text = text2 + text1
                if len(rows) < 10:
                    button_add_subpurpose = types.InlineKeyboardButton("+пункт",
                                                                       callback_data='subgoal_addi' + sub_number)
                    buttons.append(button_add_subpurpose)
            text = text3 + text
            sub_number = sub_number[0]

        if len(sub_number) == 1:
            cur.execute("SELECT * FROM purposes WHERE id=? AND subgoal_number=?", (call.from_user.id, sub_number))
            row = cur.fetchone()
            caption = row[1]
            if row[4] == 100:
                caption += '  ✅'
            else:
                caption += '   ' + str(row[4]) + '%'
            if row[3] is not None and row[4] != 100:
                caption += '   сделать до: ' + row[3]
            if text == '':
                cur.execute("SELECT * FROM purposes WHERE id=? AND purpose_above=?", (call.from_user.id, sub_number))
                rows = cur.fetchall()
                if rows:
                    text1 = ''
                    text2 = ''
                    t = 0
                    for row in rows:
                        t += 1
                        if row[4] == 100:
                            text1 += '\n        ' + str(t) + ")" + row[1] + '  ✅'
                        elif row[3] is not None:
                            text2 += '\n        ' + str(t) + ")" + row[1] + '   ' + str(row[4]) + '%   ' + row[3]
                        else:
                            text2 += '\n        ' + str(t) + ")" + row[1] + '   ' + str(row[4]) + '%'
                        button_subpurpose = types.InlineKeyboardButton(str(t), callback_data='purpose' + str(row[6]))
                        buttons.append(button_subpurpose)
                    text = text2 + text1
                if len(rows) < 10:
                    button_add_subpurpose = types.InlineKeyboardButton("+подцель",
                                                                       callback_data='subgoal_addi' + sub_number)
                    buttons.append(button_add_subpurpose)
            caption = caption + text

            purposes_keyboard = types.InlineKeyboardMarkup(row_width=5)
            button_change_purpose = types.InlineKeyboardButton("Изменить", callback_data='purp_change' + started_number)
            cur.execute("SELECT * FROM purposes WHERE id=? AND subgoal_number=?", (call.from_user.id, started_number))
            row = cur.fetchone()
            if row[4] != 100:
                button_text = 'Отметить ✅'
            else:
                button_text = 'Снять ✅'
            button_done_purpose = types.InlineKeyboardButton(button_text, callback_data='purp_done' + started_number)
            button_del_purpose = types.InlineKeyboardButton("Удалить", callback_data='purp_del' + started_number)
            purposes_keyboard.add(button_change_purpose, button_del_purpose, button_done_purpose)
            if buttons:
                purposes_keyboard.add(*buttons)

            if started_number == sub_number:
                button_back = types.InlineKeyboardButton('←', callback_data="purp_start")
                purposes_keyboard.add(button_back)
                bot.edit_message_text(caption, call.message.chat.id, call.message.message_id,
                                      reply_markup=purposes_keyboard)
            else:
                purposes_keyboard.add(button_back)
                bot.edit_message_text(caption, call.message.chat.id, call.message.message_id,
                                      reply_markup=purposes_keyboard)
    cur.close()
