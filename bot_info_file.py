import telebot
import sqlite3

TOKEN = ''
bot = telebot.TeleBot(TOKEN)


conn = sqlite3.connect('base.bd', check_same_thread=False)
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS stories (row_number integer, id integer, page integer(1),'
            ' story_text varchar(4096), main_theme integer(2), all_pages integer(1))')
# cur.execute('INSERT INTO stories (row_number, id, page, story_text) VALUES(?1, ?2, ?3, ?4)',
#             (1, 1, 1, "первая история"))
# cur.execute('INSERT INTO stories (row_number, id, page, story_text) VALUES(?1, ?2, ?3, ?4)',
#             (2, 1, 2, "первая история продолжение"))
# cur.execute('INSERT INTO stories (row_number, id, page, story_text) VALUES(?1, ?2, ?3, ?4)', (3, 2, 1,
#                                                                                               "Вторая -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------мега длинная история"))
# cur.execute('INSERT INTO stories (row_number, id, page, story_text) VALUES(?1, ?2, ?3, ?4)',
#             (4, 3, 1, "третья история"))
# cur.execute('INSERT INTO stories (row_number, id, page, story_text) VALUES(?1, ?2, ?3, ?4)',
#             (5, 1, 3, "первая история продолжение продолжения"))
# conn.commit()

cur.execute('CREATE TABLE IF NOT EXISTS waiting_for_chat (id integer, theme varchar(50))')
cur.execute('CREATE TABLE IF NOT EXISTS chatting (id integer, id_connected integer)')
conn.commit()
cur.close()
