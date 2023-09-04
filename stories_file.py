from telebot import types

import writing_stories

from bot_info_file import bot, conn


@bot.message_handler(func=lambda message: message.text.lower() == "истории пользователей")
def stories(message):
    stories_keyboard = types.InlineKeyboardMarkup(row_width=3)
    button_read_stories = types.InlineKeyboardButton('Читать истории', callback_data='read_stories0')
    button_write_story = types.InlineKeyboardButton('Мои истории', callback_data='write_story')
    stories_keyboard.add(button_read_stories, button_write_story)
    bot.send_message(message.chat.id, "Здесь вы можете читать и писать истории бла бла бла",
                     # исправить
                     reply_markup=stories_keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('read_stories'))
def reading(call):
    marker = call.data[12]
    cur = conn.cursor()
    if marker == 'p':
        offset = call.data[13:]
        cur.execute('SELECT * FROM stories WHERE page=? AND row_number < ? ORDER BY row_number DESC LIMIT ?',
                    (1, offset, 1))
        row = cur.fetchone()  # кнопка "влево" не должна появляться на самом первом тексте
    else:
        offset = call.data[12:]
        cur.execute('SELECT * FROM stories WHERE page=? AND row_number > ? ORDER BY row_number LIMIT ?', (1, offset, 1))
        row = cur.fetchone()
    cur.close()
    if row is None and offset == '0':  # только если при запросе всех историй ничего нет
        write_story_keyboard = types.InlineKeyboardMarkup(row_width=3)
        button_write_story = types.InlineKeyboardButton('Написать свою', callback_data='write_story')
        write_story_keyboard.add(button_write_story)
        bot.edit_message_text("Историй еще нет. Ваша может стать первой", call.message.chat.id,
                              call.message.message_id, reply_markup=write_story_keyboard)
    elif row is not None:
        offset = row[0]
        writer_id = row[1]
        page = row[2] + 1
        story_text = row[3]
        read_story_keyboard = types.InlineKeyboardMarkup()
        button_next_story = types.InlineKeyboardButton('→', callback_data='read_stories' + str(offset))
        button_prev_story = types.InlineKeyboardButton('←', callback_data='read_storiesp' + str(offset))
        button_continue_story = types.InlineKeyboardButton('Продолжение',
                                                           callback_data='continue' + str(page) + str(writer_id))
        buttons_list = []
        if offset != 0 and offset != 1:
            buttons_list.append(button_prev_story)
        cur = conn.cursor()
        cur.execute('SELECT * FROM stories WHERE page=? AND id=?', (page, writer_id))
        if cur.fetchone() is not None:
            buttons_list.append(button_continue_story)
        cur.execute('SELECT * FROM stories WHERE page=? AND row_number > ? ORDER BY row_number LIMIT ?', (1, offset, 1))
        if cur.fetchone() is not None:
            buttons_list.append(button_next_story)
        read_story_keyboard.add(*buttons_list)
        bot.edit_message_text(story_text, call.message.chat.id,
                              call.message.message_id, reply_markup=read_story_keyboard)
    else:
        bot.edit_message_text("К сожалению данная история удалена", call.message.chat.id,
                              call.message.message_id)
    cur.close()



@bot.callback_query_handler(func=lambda call: call.data.startswith('continue'))
def continue_reading(call):
    list_number = call.data[8]
    writer_id = call.data[9:]
    cur = conn.cursor()
    cur.execute('SELECT * FROM stories WHERE id = ? AND page = ?', (writer_id, list_number))
    row = cur.fetchone()
    if row is not None:
        story_text = row[3]
        read_story_keyboard = types.InlineKeyboardMarkup()
        button_prev_story_part = types.InlineKeyboardButton('Предыдущий текст', callback_data='continue' + str(
            int(list_number) - 1) + writer_id)
        if list_number == '2':
            cur.execute('SELECT * FROM stories WHERE id = ? AND page = ?', (writer_id, int(list_number) - 1))
            offset = cur.fetchone()[0]
            button_prev_story_part = types.InlineKeyboardButton('Предыдущий текст',
                                                                callback_data='read_stories' + str(offset - 1))
        buttons_list = []
        buttons_list.append(button_prev_story_part)
        button_continue_story = types.InlineKeyboardButton('Продолжение',
                                                           callback_data='continue' + str(int(list_number) + 1) + str(
                                                               writer_id))
        cur.execute('SELECT * FROM stories WHERE id = ? AND page = ?', (writer_id, int(list_number) + 1))
        if cur.fetchone() is not None:
            buttons_list.append(button_continue_story)
        read_story_keyboard.add(*buttons_list)
        bot.edit_message_text(story_text, call.message.chat.id,
                              call.message.message_id, reply_markup=read_story_keyboard)
    cur.close()
