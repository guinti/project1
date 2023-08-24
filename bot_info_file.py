import telebot
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
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
cur.execute(
    'CREATE TABLE IF NOT EXISTS poll_dictionary (poll_id integer, message_id integer, poll_question varchar, poll_options varchar)')
cur.execute('CREATE TABLE IF NOT EXISTS calendar (id integer, smile varchar, notes varchar, year integer, month integer, day integer, mood varchar)')
# cur.execute('INSERT INTO calendar(id, mood, smile, notes, year, month, day) VALUES(?, ?, ?, ?, ?, ?, ?)', (97124558, 5, '😳', "ыхыыхыы", 2023, 3, 12))
# cur.execute('INSERT INTO calendar(id, mood, smile, notes, year, month, day) VALUES(?, ?, ?, ?, ?, ?, ?)', (97124558, 4, '☺️', "ыхыыхыы2", 2023, 7, 13))
# cur.execute('INSERT INTO calendar(id, mood, smile, notes, year, month, day) VALUES(?, ?, ?, ?, ?, ?, ?)', (97124558, 5, '🧐', "ыхыыхыы2", 2023, 8, 1))
# cur.execute('INSERT INTO calendar(id, mood, smile, notes, year, month, day) VALUES(?, ?, ?, ?, ?, ?, ?)', (97124558, 3, '🥵', "ыхыыхыы", 2023, 7, 31))
# cur.execute('INSERT INTO calendar(id, mood, smile, notes, year, month, day) VALUES(?, ?, ?, ?, ?, ?, ?)', (97124558, 3, '🥵🧐', "ыхыыхыы", 2023, 8, 7))
# cur.execute('INSERT INTO calendar(id, mood, smile, notes, year, month, day) VALUES(?, ?, ?, ?, ?, ?, ?)', (97124558, 2, '', "", 2023, 8, 2))
# cur.execute('INSERT INTO calendar(id, mood, smile, notes, year, month, day) VALUES(?, ?, ?, ?, ?, ?, ?)', (97124558, 3, '🧐', "", 2023, 8, 16))
conn.commit()
cur.close()
