import schedule
import time

def send_message():
    chat_id = 'TARGET_CHAT_ID'
    message = "Привет, это сообщение отправлено по расписанию!"
    bot.send_message(chat_id, message)

schedule.every().day.at("08:00").do(send_message)

while True:
    schedule.run_pending()
    time.sleep(1)