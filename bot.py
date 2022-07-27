import logging
import requests
from environs import Env
from telegram import Update
from telegram.ext import CommandHandler, Updater, CallbackContext

logger = logging.getLogger(__file__)

DVMN_URL = 'https://dvmn.org/api/long_polling/'


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
    text=f"Hello, {update.effective_chat.first_name}!")

def check_devman_status(context: CallbackContext):
    dvmn_token, chat_id = context.job.context
    last_time = context.bot_data.get('last_time', '')
    headers = {'Authorization': dvmn_token}
    params = {'timestamp': last_time}
    try:
        response = requests.get(DVMN_URL, headers=headers, params=params)
        response.raise_for_status()
        review = response.json()
        if review['status'] == 'found':
            for attempt in review['new_attempts']:
                if attempt['is_negative']:
                    status = 'К сожалению в работе нашлись ошибки.'
                else:
                    status = 'Преподавателю все понравилось. Можно приступать к следующему уроку!'
                lesson_title = attempt['lesson_title']
                lesson_url = attempt['lesson_url']
                context.bot.send_message(chat_id=chat_id, text=f'У вас проверили работу \
                                         "{lesson_title}"\n\n{status}\n{lesson_url}')
        last_time = review.get('timestamp_to_request', last_time)
        last_time = review.get('last_attempt_timestamp', last_time)
        context.bot_data['last_time'] = last_time
    except requests.exceptions.ReadTimeout:
        pass
    except requests.exceptions.ConnectionError:
        print('Connection Error!')


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    env = Env()
    env.read_env()
    dvmn_token = env('DVMN_API_TOKEN')
    tlgm_bot_token =  env('TLGM_BOT_TOKEN')
    tlgm_chat_id =  env('TLGM_CHAT_ID')
    updater = Updater(token=tlgm_bot_token, use_context=True)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    j = updater.job_queue
    j.run_repeating(check_devman_status, 300, 10, context=(dvmn_token, tlgm_chat_id))

    #updater.start_polling()


if __name__ == '__main__':
    main()
