import threading
import schedule
import time

from bot_info_file import bot
from menu_file import menu
import stories_file
from stories_file import stories
import start_pulls
import sending_facts
from sending_facts import run_schedule
import anon_bot
import calendar_file
import mood_graphs
import targets_file
import methods_file

schedule_thread = threading.Thread(target=run_schedule)
schedule_thread.start()


@bot.message_handler(func=lambda message: message.text.lower() == "меню")
def handle_message(message):
    menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text.lower() == "истории пользователей")
def handle_message(message):
    stories(message)


bot.polling(none_stop=True)
