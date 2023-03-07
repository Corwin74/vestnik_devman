import logging
import time
import requests
from environs import Env
import telegram


logger = logging.getLogger(__file__)

DVMN_URL = 'https://dvmn.org/api/long_polling/'
SLEEP_TIME = 600


class TlgmLogsHandler(logging.Handler):

    def __init__(self, token, chat_id):
        super().__init__()
        self.bot = telegram.Bot(token=token)
        self.admin_chat_id = chat_id

    def emit(self, record):
        self.bot.send_message(
                         chat_id=self.admin_chat_id,
                         text=self.format(record)
        )


def main():

    env = Env()
    env.read_env()
    dvmn_token = env('DVMN_API_TOKEN')
    tlgm_bot_token = env('TLGM_BOT_TOKEN')
    tlgm_chat_id = env('TLGM_CHAT_ID')

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger.setLevel(logging.INFO)
    tlgm_handler = TlgmLogsHandler(tlgm_bot_token, tlgm_chat_id)
    logger.addHandler(tlgm_handler)
    logger.info('Started A Bot "Vestnik Devman".')

    last_time = ''
    headers = {'Authorization': dvmn_token}

    while True:
        try:
            params = {'timestamp': last_time}
            response = requests.get(DVMN_URL, headers=headers, params=params)
            response.raise_for_status()
            review = response.json()
            if review['status'] == 'found':
                for attempt in review['new_attempts']:
                    if attempt['is_negative']:
                        status = 'К сожалению в работе нашлись ошибки.'
                    else:
                        status = (
                                  'Преподавателю все понравилось.'
                                  'Можно приступать к следующему уроку!'
                        )
                    lesson_title = attempt['lesson_title']
                    lesson_url = attempt['lesson_url']
                    tlgm_handler.bot.send_message(
                        chat_id=tlgm_chat_id,
                        text=(
                              f'У вас проверили работу "{lesson_title}"\n\n'
                              f'{status}\n{lesson_url}'
                        )
                    )
            last_time = review.get('timestamp_to_request', last_time)
            last_time = review.get('last_attempt_timestamp', last_time)
        except requests.exceptions.ReadTimeout:
            pass
        except requests.exceptions.ConnectionError:
            logger.error('Connection Error!')
            time.sleep(SLEEP_TIME)
            logger.info('Trying to reconnect...')
        except requests.exceptions.HTTPError:
            logger.error('HTTPError!')
            time.sleep(SLEEP_TIME)
            logger.info('Trying to reconnect...')
        except Exception:
            logger.exception("O-o-o-p-s!")
            time.sleep(SLEEP_TIME)
            last_time = ''


if __name__ == '__main__':
    main()
