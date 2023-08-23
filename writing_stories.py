from telebot import types

from bot_info_file import bot, conn


@bot.callback_query_handler(func=lambda call: call.data.startswith('write_story'))
def writing(call):
    person_stories_keyboard = types.InlineKeyboardMarkup(row_width=3)
    button_read_my_stories = types.InlineKeyboardButton('Написанные истории', callback_data='read_my_stories1')
    button_write_story = types.InlineKeyboardButton('Написать свою', callback_data='write_my_story')
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM stories WHERE id=?', (call.from_user.id,))
    personal_stories_count = cur.fetchone()[0]
    cur.execute('SELECT * FROM stories WHERE id=?', (call.from_user.id,))
    if cur.fetchone() is None:
        person_stories_keyboard.add(button_write_story)
    elif personal_stories_count == 9:
        person_stories_keyboard.add(button_read_my_stories)
    else:
        person_stories_keyboard.add(button_read_my_stories, button_write_story)
    bot.edit_message_text("Написать истории бла бла. Правила написания бла бла 4096 бла бла", call.message.chat.id,
                          call.message.message_id, reply_markup=person_stories_keyboard)
    cur.close()


@bot.callback_query_handler(func=lambda call: call.data == 'write_my_story')
def writing(call):
    def last_step(message):
        story = message.text
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM stories WHERE id=?', (message.chat.id,))
        page = cur.fetchone()[0]
        cur.execute('SELECT COUNT(*) FROM stories')
        row_number = cur.fetchone()[0]
        cur.execute('INSERT INTO stories(row_number, id, page, story_text) VALUES(?, ?, ?, ?)',
                    (row_number + 1, message.chat.id, page + 1, story))
        conn.commit()
        bot.send_message(message.chat.id, 'Ваша история добавленаВ)')
        cur.close()

    bot.edit_message_text("Напишите свою сторию. Правила написания бла бла 4096 бла бла кряу", call.message.chat.id,
                          call.message.message_id)
    bot.register_next_step_handler(call.message, last_step)


@bot.callback_query_handler(func=lambda call: call.data.startswith('read_my_stories'))
def wrote(call):
    page = call.data[15]
    marked = 0
    if page == 'p':
        marked = 1
        page = call.data[16]
    buttons = []
    person_stories_keyboard = types.InlineKeyboardMarkup(row_width=3)
    my_prev_story = types.InlineKeyboardButton('←', callback_data='read_my_storiesp' + str(int(page) - 1))
    if int(page) > 1:
        buttons.append(my_prev_story)
    my_next_story = types.InlineKeyboardButton('→', callback_data='read_my_stories' + str(int(page) + 1))
    change_story = types.InlineKeyboardButton('Изменить', callback_data='change' + page)
    cur = conn.cursor()
    cur.execute('SELECT * FROM stories WHERE id=? AND page=?', (call.from_user.id, int(page)))
    row = cur.fetchone()
    buttons.append(change_story)
    buttons.append(my_next_story)
    person_stories_keyboard.add(*buttons)
    if row is None:
        another_person_stories_keyboard = types.InlineKeyboardMarkup()
        write_my_story = types.InlineKeyboardButton('Написать историю', callback_data='write_my_story')
        another_person_stories_keyboard.add(my_prev_story, write_my_story)
        bot.edit_message_text("Написать историю бла бла. Это будет Ваша " + str(int(page)) + ' история',
                              call.message.chat.id,
                              call.message.message_id, reply_markup=another_person_stories_keyboard)
    else:
        story_text = row[3]
        if marked == 1:
            cur.execute('SELECT * FROM stories WHERE id=? AND page=?', (call.from_user.id, int(page)))
            story_text = cur.fetchone()[3]
        bot.edit_message_text(story_text, call.message.chat.id,
                              call.message.message_id, reply_markup=person_stories_keyboard)
    cur.close()


@bot.callback_query_handler(func=lambda call: call.data.startswith('change'))
def change(call):
    page = call.data[6]

    def last_step(message, page):
        story = message.text
        cur = conn.cursor()
        if story == '.':
            cur.execute('SELECT row_number FROM stories WHERE id=? AND page=?', (message.chat.id, page))
            row_deleted = cur.fetchone()[0]
            cur.execute('DELETE FROM stories WHERE id=? AND page=?', (message.chat.id, page))
            conn.commit()
            cur.execute('SELECT row_number, page FROM stories WHERE id=? AND page > ? ORDER BY row_number', (message.chat.id, page))
            rows = cur.fetchall()
            for row in rows:
                row_number = row[0]
                page = row[1] - 1
                cur.execute('UPDATE stories SET page = ? WHERE row_number = ?', (page, row_number))
                conn.commit()
            cur.execute('SELECT COUNT(*) FROM stories',)
            row_count = cur.fetchone()[0] + 1
            while (row_deleted <= row_count):  #очень медленно мб, мб изменю
                row_deleted += 1
                cur.execute('UPDATE stories SET row_number = ? WHERE row_number = ?', (row_deleted-2, row_deleted - 1))
                conn.commit()
            bot.send_message(message.chat.id, 'Ваша история удалена')
        else:
            cur.execute('UPDATE stories SET story_text =? WHERE id=? AND page=?', (story, message.chat.id, page))
            conn.commit()
            bot.send_message(message.chat.id, 'Ваша история изменена👍')

    cur = conn.cursor()
    cur.execute('SELECT * FROM stories WHERE id=? AND page=?', (call.from_user.id, page))
    text = cur.fetchone()[3]
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id)
    bot.send_message(call.from_user.id,
                     "Измените свою историю. Если ваше сообщение будет состоять только из \".\"(точки), ваша история будет удалена. 4096 бла бла кряу")
    bot.register_next_step_handler(call.message, lambda message: last_step(message, page))
