import pandas as pd
from datetime import datetime, timedelta
from pytz import timezone
from telegram import Bot
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, JobQueue
from secret import API_KEY

TOKEN = API_KEY
chat_id = '-919115264'
csv_file = 'members.csv'
members = pd.read_csv(csv_file)
members['last_message_date'] = pd.to_datetime(members['last_message_date'], format='%d/%m/%Y')
members['username'] = members['username'].astype(str)

def check_posts(context):
    bot = Bot(token=TOKEN)
    now = datetime.now(timezone('Europe/Moscow'))
    for index, member in members.iterrows():
        if member['last_message_date'].date() < now.date():
            bot.send_message(chat_id=chat_id, text=f'@{member["username"]}, you haven\'t posted today.')

def remind(context):
    bot = Bot(token=TOKEN)
    now = datetime.now(timezone('Europe/Moscow'))
    prev_day = now - timedelta(days=1)
    if now.weekday() == 0:  # if today is Monday
        prev_day = now - timedelta(days=3)  # previous day should be Friday
    bot.send_message(chat_id=chat_id, text=f'Reminder to post a daily message. Today is {now.strftime("%d/%m/%Y")}, previous work day was {prev_day.strftime("%d/%m/%Y")}.')

def handle_message(update, context):
    username = update.message.from_user.username
    if username in members['username'].values:
        members.loc[members['username'] == username, 'last_message_date'] = datetime.now(timezone('Europe/Moscow'))
        members.to_csv(csv_file, index=False)

def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_message))
    j = updater.job_queue
    j.run_daily(check_posts, time=timedelta(hours=17), days=(0, 1, 2, 3, 4))  # 5PM GMT+3
    j.run_daily(remind, time=timedelta(hours=9), days=(0, 1, 2, 3, 4))  # 9AM GMT+3
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
