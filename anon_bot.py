import time
from telebot import types
from bot_info_file import bot
from bot_info_file import conn


@bot.message_handler(func=lambda message: message.text.lower() == "чат")
def chat(message):
    cur = conn.cursor()
    cur.execute('SELECT * FROM chatting WHERE id=?', (message.chat.id,))
    chatting = cur.fetchone()
    cur.execute('SELECT * FROM waiting_for_chat WHERE id=?', (message.chat.id,))
    waiting = cur.fetchone()
    if chatting is not None:
        bot.send_message(message.chat.id,
                         "Вы уже в чате. Если хотите закончить и начать следующий напишите \"завершить чат\"")
    if waiting is not None:
        bot.send_message(message.chat.id, "Для вас подбирается чат. Если вы передумали, напишите \"завершить чат\"")
    if chatting is None and waiting is None:
        chat_keyboard = types.InlineKeyboardMarkup(row_width=3)
        button_start_chat = types.InlineKeyboardButton('Подключиться к анонимному чату', callback_data='start_chat')
        chat_keyboard.add(button_start_chat)
        bot.send_message(message.chat.id, "В анонимном чате вы можете обсудить волнующие вас проблемы с людьми,"
                                          " которым это близко", reply_markup=chat_keyboard)  # исправить


@bot.callback_query_handler(func=lambda call: call.data.startswith('start_chat'))
def chatting(call):
    options = ["любая тема", "тревожность", "прокрастинация", "стресс", "другое"]
    poll_options = options[0]
    for i in range(1, 5):
        poll_options += ',' + options[i]
    question_text = "На какую тему вы хотели бы пообщаться?"
    send_poll = bot.send_poll(call.from_user.id, question_text, options, is_anonymous=False)
    id = send_poll.poll.id  # создать библиотеку опросов
    message_id = send_poll.id
    cur = conn.cursor()
    cur.execute('INSERT INTO poll_dictionary(poll_id, message_id, poll_question, poll_options) VALUES(?, ?, ?, ?)',
                (id, message_id, question_text, poll_options))
    conn.commit()
    cur.close()


def pull_theme_chat(cur, user, chosen):
    cur.execute("SELECT * FROM chatting WHERE id=?", (user,))
    is_chatting = cur.fetchone()
    cur.execute("SELECT * FROM waiting_for_chat WHERE id=?", (user,))
    is_waiting = cur.fetchone()
    if is_chatting is None and is_waiting is None:
        time.sleep(1)
        bot.send_message(user, 'Выполняется поиск чата. Когда он будет найден, вам придет сообщение')
        if chosen != 'любая тема':
            cur.execute('SELECT * FROM waiting_for_chat WHERE theme=? LIMIT ?', (chosen, 1))
        else:
            cur.execute('SELECT * FROM waiting_for_chat LIMIT ?', (1,))
        person = cur.fetchone()
        if person is None and chosen != 'любая тема':
            cur.execute('SELECT * FROM waiting_for_chat WHERE theme=? LIMIT ?', ('любая тема', 1))
            person = cur.fetchone()
        if person is None:
            cur.execute('INSERT INTO waiting_for_chat(id, theme) VALUES(?, ?)', (user, chosen))
            conn.commit()
        else:
            id = person[0]
            cur.execute('DElETE FROM waiting_for_chat WHERE id=?', (id,))
            cur.execute('INSERT INTO chatting(id, id_connected) VALUES(?, ?)', (id, user))
            cur.execute('INSERT INTO chatting(id, id_connected) VALUES(?, ?)', (user, id))
            conn.commit()
            bot.send_message(user, "Собеседник найден. Чат начат")
            bot.send_message(id, "Собеседник найден. Чат начат")
        cur.close()


@bot.message_handler(func=lambda message: message.text.lower() not in ["стоп", '/start', "чат", "истории пользователей", "календарь", "меню", 'методики', 'редактор целей'])
def chatting(message):
    cur=conn.cursor()
    cur.execute("SELECT * FROM waiting_for_chat WHERE id=?", (message.chat.id,))
    waiting=cur.fetchone()
    cur.execute("SELECT * FROM chatting WHERE id=?", (message.chat.id,))
    if cur.fetchone() is not None or waiting is not None:
        if (message.text.lower()== "завершить чат"):
            cur.execute('SELECT id_connected FROM chatting WHERE id=?', (message.chat.id,))
            id_connected = cur.fetchone()
            cur.execute('DELETE FROM chatting WHERE id=?', (message.chat.id,))
            cur.execute('DELETE FROM chatting WHERE id_connected=?', (message.chat.id,))
            conn.commit()
            if waiting is not None:
                cur.execute('DELETE FROM waiting_for_chat WHERE id=?', (message.chat.id,))
                conn.commit()
                bot.send_message(message.chat.id, 'Поиск чата отменен')
            else:
                bot.send_message(message.chat.id, 'Чат завершен')
                bot.send_message(id_connected[0], 'Чат завершен вторым участником')
        else:
            if waiting is None:
                cur.execute('SELECT * FROM chatting WHERE id=?', (message.chat.id,))
                id_connected = cur.fetchone()[1]
                bot.send_message(id_connected, message.text)
        cur.close()
