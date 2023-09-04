from telebot import types
from bot_info_file import bot, conn


@bot.callback_query_handler(func=lambda call: call.data.startswith('purp_del'))
def purpose_del_or_no(call):
    purp_num = call.data[8:]
    keybiard_del = types.InlineKeyboardMarkup()
    button_back = types.InlineKeyboardButton('←', callback_data="purpose" + purp_num)
    button_del = types.InlineKeyboardButton('Да', callback_data="purp_yes_del" + purp_num)
    keybiard_del.add(button_back, button_del)
    cur = conn.cursor()
    cur.execute("SELECT * FROM purposes WHERE id=? AND subgoal_number=?", (call.from_user.id, int(purp_num)))
    row = cur.fetchone()
    cur.close()
    if row is not None:
        bot.send_message(call.from_user.id, row[1] + '\nВы точно хотите удалить?',
                         reply_markup=keybiard_del)
    bot.delete_message(call.from_user.id, call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('purp_yes_del'))
def purpose_del(call):
    sub_number = call.data[12:]
    cur = conn.cursor()
    cur.execute("SELECT * FROM purposes WHERE id=? AND subgoal_number=?", (call.from_user.id, int(sub_number)))
    row = cur.fetchone()
    if row is not None:
        if len(sub_number) == 1:
            cur.execute("DELETE FROM purposes WHERE id=? AND ((subgoal_number>? AND subgoal_number<?)"
                        " OR purpose_above=? OR subgoal_number=?)", (call.from_user.id, int(sub_number) * 100 - 1,
                                                                     int(sub_number) * 100 + 100, int(sub_number),
                                                                     int(sub_number)))
            conn.commit()
        if len(sub_number) == 2:
            cur.execute("SELECT COUNT(*) FROM purposes WHERE id=? AND purpose_above=?",
                        (call.from_user.id, int(sub_number) // 10))
            amount = cur.fetchone()[0] - 1
            cur.execute(
                'DELETE FROM purposes WHERE id=? AND ((subgoal_number>? AND subgoal_number<?) OR subgoal_number=?)',
                (call.from_user.id, int(sub_number) * 10 - 1, int(sub_number) * 10 + 10, int(sub_number)))
            cur.execute("SELECT * FROM purposes WHERE id=? AND purpose_above=?",
                        (call.from_user.id, int(sub_number) // 10))
            rows = cur.fetchall()
            sum_new = 0
            t = 0
            for purpose in rows:
                cur.execute('UPDATE purposes SET part_of_purpose_above=? WHERE id=? AND subgoal_number=?',
                            (100 // amount, row[2], purpose[6]))
                conn.commit()
                sum_new += purpose[4] * (100 // amount) // 100
                if purpose[4] != 100:
                    t = 1

            if t == 0:
                cur.execute('UPDATE purposes SET done_percentage=? WHERE id=? AND subgoal_number=?',
                            (100, row[2], row[6] // 10))
            else:
                cur.execute('UPDATE purposes SET done_percentage=? WHERE id=? AND subgoal_number=?',
                            (sum_new, row[2], row[6] // 10))
            conn.commit()
        if len(sub_number) == 3:
            cur.execute("SELECT COUNT(*) FROM purposes WHERE id=? AND purpose_above=?",
                        (call.from_user.id, int(sub_number) // 10))
            amount = cur.fetchone()[0] - 1
            cur.execute('DELETE FROM purposes WHERE id=? AND subgoal_number=?', (row[2], row[6]))
            conn.commit()
            cur.execute("SELECT * FROM purposes WHERE id=? AND purpose_above=?",
                        (call.from_user.id, int(sub_number) // 10))
            rows = cur.fetchall()
            sum_new = 0
            for purpose in rows:
                cur.execute('UPDATE purposes SET part_of_purpose_above=? WHERE id=? AND subgoal_number=?',
                            (100 // amount, row[2], purpose[6]))
                conn.commit()
                sum_new += purpose[4] * (100 // amount) // 100
            cur.execute("SELECT * FROM purposes WHERE id=? AND subgoal_number=?", (row[2], row[6] // 10))
            sum_last = cur.fetchone()[4]
            t = 0
            if sum_new >= 96:
                cur.execute('UPDATE purposes SET done_percentage=? WHERE id=? AND subgoal_number=?',
                            (100, row[2], row[6] // 10))
            else:
                cur.execute('UPDATE purposes SET done_percentage=? WHERE id=? AND subgoal_number=?',
                            (sum_new, row[2], row[6] // 10))
                t = 1
            conn.commit()
            cur.execute("SELECT * FROM purposes WHERE id=? AND subgoal_number=?", (row[2], row[6] // 100))
            sum = cur.fetchone()[4]
            if sum + sum_new - sum_last < 0:
                cur.execute('UPDATE purposes SET done_percentage=? WHERE id=? AND subgoal_number=?',
                            (0, row[2], row[6] // 100))
            elif t == 0:
                cur.execute('UPDATE purposes SET done_percentage=? WHERE id=? AND subgoal_number=?',
                            (100, row[2], row[6] // 100))
            else:
                cur.execute('UPDATE purposes SET done_percentage=? WHERE id=? AND subgoal_number=?',
                            (sum + sum_new - sum_last, row[2], row[6] // 100))
        bot.delete_message(call.from_user.id, call.message.message_id)
        keybiard_del = types.InlineKeyboardMarkup()
        if row[6] // 10 == 0:
            button_back = types.InlineKeyboardButton('←', callback_data="purp_start")
        else:
            button_back = types.InlineKeyboardButton('←', callback_data="purposea" + str(row[6] // 10))
        keybiard_del.add(button_back)
        bot.send_message(call.from_user.id, "Удалено", reply_markup=keybiard_del)
    cur.close()
