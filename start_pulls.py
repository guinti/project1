from bot_info_file import bot, conn
import time
from anon_bot import pull_theme_chat
from menu_file import menu

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Добро пожаловать в наш бот! Пожалуйста, пройдите входной тест)',
                     parse_mode='html')
    time.sleep(1)
    options = ["0-20% времени", "20-40%", "40-70%", "70-100%"]
    poll_options = options[0]
    for i in range(1, 4):
        poll_options += ',' + options[i]
    question_text = "Как часто вы испытывали стресс в последнем месяце?"
    send_poll = bot.send_poll(message.chat.id, question_text, options, is_anonymous=False)
    id = send_poll.poll.id  # создать библиотеку опросов
    message_id = send_poll.id
    cur = conn.cursor()
    cur.execute('INSERT INTO poll_dictionary(poll_id, message_id, poll_question, poll_options) VALUES(?, ?, ?, ?)',
                (id, message_id, question_text, poll_options))
    conn.commit()
    cur.execute("SELECT * FROM test_results WHERE id=?", (message.chat.id,))
    if cur.fetchone() is None:
        cur.execute('INSERT INTO test_results(id) VALUES(?)', (message.chat.id,))
        conn.commit()
        cur.close()


@bot.poll_answer_handler()
def handle_poll_answer(pollAnswer):
    poll_id = pollAnswer.poll_id
    user = pollAnswer.user.id
    chosen = pollAnswer.option_ids[0]
    cur = conn.cursor()
    cur.execute('SELECT * FROM poll_dictionary WHERE poll_id=?', (poll_id,))
    row = cur.fetchone()
    message_id = row[1]
    poll_question = row[2]
    bot.stop_poll(user, message_id)
    cur.execute('DELETE FROM poll_dictionary WHERE poll_id=?', (poll_id,))
    conn.commit()
    poll_options = row[3]
    options_list = poll_options.split(',')
    if poll_question == "На какую тему вы хотели бы пообщаться?":
        chosen = options_list[chosen]
        pull_theme_chat(cur, user, chosen)
    elif poll_question == "Как часто вы испытывали стресс в последнем месяце?":
        pull_start_1(cur, user, chosen)
    elif poll_question == "Насколько вы тревожный человек?":
        pull_start_2(cur, user, chosen)
    elif poll_question == "Насколько просто вы отвлекаетесь от выполнения задачи?":
        pull_start_3(cur, user, chosen)
    elif poll_question == "Насколько тяжело вам приступить к сложной задаче?":
        pull_start_4(cur, user, chosen)
    elif poll_question == "Как вы относитесь к специалистам по ментальному здоровью(психологам)?":
        pull_start_5(cur, user, chosen)


def pull_start_1(cur, user, chosen):
    cur.execute('UPDATE test_results SET question_1=? WHERE id=?', (chosen, user))
    conn.commit()
    options = ["тревожусь из-за любой мелочи", "есть, определенные вещи, из-за которых я пререодически тревожусь",
               "почти ничего не вызыввет тревогу"]
    poll_options = options[0]
    for i in range(1, 3):
        poll_options += ',' + options[i]
    question_text = "Насколько вы тревожный человек?"
    send_poll = bot.send_poll(user, question_text, options, is_anonymous=False)
    id = send_poll.poll.id  # создать библиотеку опросов
    message_id = send_poll.id
    cur.execute('INSERT INTO poll_dictionary(poll_id, message_id, poll_question, poll_options) VALUES(?, ?, ?, ?)',
                (id, message_id, question_text, poll_options))
    conn.commit()
    cur.close()


def pull_start_2(cur, user, chosen):
    cur.execute('UPDATE test_results SET question_2=? WHERE id=?', (chosen, user))
    conn.commit()
    options = ["Может отвлечь практически что угодно", "Могу отвлечься на что-то интересное",
               "Может отвлечь только что-то критичное", "Знаю, что нужно, и делаю"]
    poll_options = options[0]
    for i in range(1, 4):
        poll_options += ',' + options[i]
    question_text = "Насколько просто вы отвлекаетесь от выполнения задачи?"
    send_poll = bot.send_poll(user, question_text, options, is_anonymous=False)
    id = send_poll.poll.id  # создать библиотеку опросов
    message_id = send_poll.id
    cur.execute('INSERT INTO poll_dictionary(poll_id, message_id, poll_question, poll_options) VALUES(?, ?, ?, ?)',
                (id, message_id, question_text, poll_options))
    conn.commit()
    cur.close()


def pull_start_3(cur, user, chosen):
    cur.execute('UPDATE test_results SET question_3=? WHERE id=?', (chosen, user))
    conn.commit()
    options = ["легко", "приходится себя заставлять", "откладываю задачу до последнего"]
    poll_options = options[0]
    for i in range(1, 3):
        poll_options += ',' + options[i]
    question_text = "Насколько тяжело вам приступить к сложной задаче?"
    send_poll = bot.send_poll(user, question_text, options, is_anonymous=False)
    id = send_poll.poll.id  # создать библиотеку опросов
    message_id = send_poll.id
    cur.execute('INSERT INTO poll_dictionary(poll_id, message_id, poll_question, poll_options) VALUES(?, ?, ?, ?)',
                (id, message_id, question_text, poll_options))
    conn.commit()
    cur.close()


def pull_start_4(cur, user, chosen):
    cur.execute('UPDATE test_results SET question_4=? WHERE id=?', (chosen, user))
    conn.commit()
    options = ["хорошо, хожу/мог бы ходить", "с небольшим предубеждением, пойду если случится что-то серьезное",
               "считаю, что они не нужны"]
    poll_options = options[0]
    for i in range(1, 3):
        poll_options += ',' + options[i]
    question_text = "Как вы относитесь к специалистам по ментальному здоровью(психологам)?"
    send_poll = bot.send_poll(user, question_text, options, is_anonymous=False)
    id = send_poll.poll.id  # создать библиотеку опросов
    message_id = send_poll.id
    cur.execute('INSERT INTO poll_dictionary(poll_id, message_id, poll_question, poll_options) VALUES(?, ?, ?, ?)',
                (id, message_id, question_text, poll_options))
    conn.commit()
    cur.close()


def pull_start_5(cur, user, chosen):
    cur.execute('UPDATE test_results SET question_5=? WHERE id=?', (chosen, user))
    conn.commit()
    cur.close()
    menu(user)
