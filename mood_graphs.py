from telebot import types
import datetime
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from bot_info_file import bot, conn
from calendar_functions import get_days_in_month


@bot.callback_query_handler(func=lambda call: call.data.startswith('graph'))
def graph_function(call):
    months = call.data[5]
    if months == 'g': months = '12'
    months = int(months)
    year = int(call.data[6:10])
    month = int(call.data[10:])

    cur = conn.cursor()
    moods = []
    dates = []
    for i in range(0, months):
        if month == 1:
            month = 12
            year -= 1
        elif i!=0:
            month -= 1
        for j in range(0, get_days_in_month(month, year)):
            day = get_days_in_month(month, year) - j
            cur.execute('SELECT mood FROM calendar WHERE id=? AND year=? AND month=? AND day=?',
                        (call.from_user.id, year, month, day))
            print(year, month, day)
            mood = cur.fetchone()
            if mood is not None:
                print(111)
                moods.insert(0, int(mood[0]))
                date_string = str(year) + "-" + str(month) + "-" + str(day)  # Формат: ГГГГ-ММ-ДД
                date = datetime.datetime.strptime(date_string, "%Y-%m-%d")
                dates.insert(0, date.date())

    print(dates)
    plt.plot(dates, moods)
    plt.xlabel('Дни')
    plt.ylabel('Настроение')
    if months == 1:
        text_end = "последний месяц"
    if months == 3:
        text_end = "последние 3 месяца"
    if months == 6:
        text_end = "последние 6 месяцев"
    if months == 12:
        text_end = "последние 12 месяцев"
    plt.title('График настроения за ' + text_end)

    image_stream = io.BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)
    bot.send_photo(call.from_user.id, photo=image_stream)
    plt.close()
    cur.close()
