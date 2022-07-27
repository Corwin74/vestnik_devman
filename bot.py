import logging
import requests
from environs import Env
from telegram import Update
from telegram.ext import CommandHandler, Updater, CallbackContext


env = Env()
env.read_env()

DVMN_URL = 'https://dvmn.org/api/long_polling/'
DVMN_TOKEN = env('DVMN_TOKEN')
BOT_TOKEN =  env('BOT_TOKEN')
CHAT_ID =  env('CHAT_ID')


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

def send_message(context, message):
    context.bot.send_message(chat_id=CHAT_ID, text=message)

def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
    text=f"Hello, {update.effective_chat.first_name}!")

def check_devman_status(context: CallbackContext):
    last_time = context.bot_data.get('last_time', '')
    headers = {'Authorization': DVMN_TOKEN}
    params = {'timestamp': last_time}
    try:
        response = requests.get(DVMN_URL, headers=headers, params=params)
        response.raise_for_status()
        resp = response.json()
        if resp['status'] == 'found':
            for attempt in resp['new_attempts']:
                if attempt['is_negative']:
                    status = 'К сожалению в работе нашлись ошибки.'
                else:
                    status = 'Преподавателю все понравилось. Можно приступать к следующему уроку!'
                lesson_title = attempt['lesson_title']
                lesson_url = attempt['lesson_url']
                send_message(context,
                            f'У вас проверили работу "{lesson_title}"\n\n{status}\n{lesson_url}')
        last_time = resp.get('timestamp_to_request', last_time)
        last_time = resp.get('last_attempt_timestamp', last_time)
        context.bot_data['last_time'] = last_time
    except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
        print('Error connecting to Devamn server!')
    except KeyError as exc:
        print('Key error!')
        print(exc)


updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

j = updater.job_queue
j.run_repeating(check_devman_status, 300, 10)

updater.start_polling()
