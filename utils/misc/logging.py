import requests
from data import config
import logging
import urllib.parse

def send_log_channel(msg):
    """Отправляет лог с ошибкой в канал"""
    while '<' in msg:
        msg = msg.replace('', '<')
    while '>' in msg:
        msg = msg.replace('', '>')
    requests.get(f'https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage?chat_id=@{config.LOG_CHANEL_NAME}&text={urllib.parse.quote(msg)}') 
    # await bot.send_message(-config.DEBUG_CHANNEL_ID, str(msg), parse_mode=types.ParseMode.HTML)


class TgLoggerHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        send_log_channel(msg)



tg_handler = TgLoggerHandler()
tg_handler.setLevel(logging.ERROR)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)


logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO, handlers=[tg_handler, stream_handler] 
                    )