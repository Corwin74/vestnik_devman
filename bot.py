import logging
import time
import requests
from environs import Env
import telegram


logger = logging.getLogger(__file__)

DVMN_URL = 'https://dvmn.org/api/long_polling/'
SLEEP_TIME = 600


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    env = Env()
    env.read_env()
    dvmn_token = env('DVMN_API_TOKEN')
    tlgm_bot_token = env('TLGM_BOT_TOKEN')
    tlgm_chat_id = env('TLGM_CHAT_ID')
    bot = telegram.Bot(token=tlgm_bot_token)
    while True:
        last_time = ''
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
                        status = 'Преподавателю все понравилось.' + \
                                 'Можно приступать к следующему уроку!'
                    lesson_title = attempt['lesson_title']
                    lesson_url = attempt['lesson_url']
                    bot.send_message(chat_id=tlgm_chat_id,
                        text=f'У вас проверили работу "{lesson_title}"\n\n{status}\n{lesson_url}')
            last_time = review.get('timestamp_to_request', last_time)
            last_time = review.get('last_attempt_timestamp', last_time)
        except requests.exceptions.ReadTimeout:
            pass
        except requests.exceptions.ConnectionError:
            time.sleep(SLEEP_TIME)


if __name__ == '__main__':
    main()
