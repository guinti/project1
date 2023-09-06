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
cur.execute('CREATE TABLE IF NOT EXISTS waiting_for_chat (id integer, theme varchar(50))')
cur.execute('CREATE TABLE IF NOT EXISTS chatting (id integer, id_connected integer)')
cur.execute(
    'CREATE TABLE IF NOT EXISTS poll_dictionary (poll_id integer, message_id integer, poll_question varchar,'
    ' poll_options varchar)')
cur.execute('CREATE TABLE IF NOT EXISTS calendar (id integer, smile varchar, notes varchar, year integer,'
            ' month integer, day integer, mood varchar)')
cur.execute('CREATE TABLE IF NOT EXISTS purposes (purpose_above integer, purpose varchar, id integer, day_finish date,'
            ' done_percentage integer, part_of_purpose_above integer, subgoal_number integer)')
cur.execute('CREATE TABLE IF NOT EXISTS test_results (id integer, question_1 integer, question_2 integer,'
            ' question_3 integer, question_4 integer, question_5 integer)')
cur.execute('CREATE TABLE IF NOT EXISTS facts (fact varchar, question_1 integer, question_2 integer,'
            ' question_3 integer, question_4 integer, question_5 integer)')
conn.commit()
cur.close()
