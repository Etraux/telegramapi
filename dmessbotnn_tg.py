import pandas as pd
from datetime import datetime, timedelta
from pytz import timezone
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from secret import API_KEY

TOKEN = API_KEY
CSV_PATH = 'path_to_your_csv_file.csv'

def compare_chat_members(context):
    chat_id = context.job.context
    members = context.bot.get_chat_members_count(chat_id)
    df = pd.read_csv(CSV_PATH)
    for index, row in df.iterrows():
        if row['user_id'] not in members:
            context.bot.send_message(chat_id='-919115264', text="You haven't posted today.")

def remind_to_post(context):
    chat_id = context.job.context
    today = datetime.now(timezone('Etc/GMT+3')).date()
    previous_work_day = today - timedelta(days=1 if today.weekday() != 0 else 3)
    message = f"Today is {today.strftime('%Y-%m-%d')}, don't forget to post a message. The previous work day was {previous_work_day.strftime('%Y-%m-%d')}."
    context.bot.send_message(chat_id='-919115264', text=message)

def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Schedule job to compare chat members at 5PM (GMT+3) from Monday to Friday
    job_queue = updater.job_queue
    job_queue.run_daily(compare_chat_members, datetime.time(17, 0, 0, tzinfo=timezone('Etc/GMT+3')), days=(0, 1, 2, 3, 4), context=dp.chat_data)

    # Schedule job to remind colleagues to post at 9AM (GMT+3) from Monday to Friday
    job_queue.run_daily(remind_to_post, datetime.time(9, 0, 0, tzinfo=timezone('Etc/GMT+3')), days=(0, 1, 2, 3, 4), context=dp.chat_data)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
