from bot_info_file import bot, conn
from targets_functions import start_targets_keyboard
import targets_filling
import targets_delete
import targets_change
import targets_done
from targets_functions import send_purposes


@bot.message_handler(func=lambda message: message.text.lower() == "редактор целей")
def purpose_menu_start(message):
    cur = conn.cursor()
    cur.execute("SELECT * FROM purposes WHERE id =? AND purpose_above=?", (message.chat.id, 0))
    rows = cur.fetchall()
    cur.close()
    start_targets_keyboard(rows, message.chat.id, message.chat.id, 1)


@bot.callback_query_handler(func=lambda call: call.data.startswith('purp_start'))
def purpose_menu(call):
    cur = conn.cursor()
    cur.execute("SELECT * FROM purposes WHERE id =? AND purpose_above=?", (call.from_user.id, 0))
    rows = cur.fetchall()
    cur.close()
    start_targets_keyboard(rows, call.from_user.id, call.message.message_id, 12)


@bot.callback_query_handler(func=lambda call: call.data.startswith('purpose'))
def purpose_info(call):
    if call.data[7] not in ['i', 'a']:
        sub_number = call.data[7:]
    else:
        sub_number = call.data[8:]
    send_purposes(sub_number, call)
