import asyncio
import logging

import requests
from loader import bot
from aiogram import types
from data import config

# def send_log_channel(msg):
#     print('jere')
#     while '<' in msg:
#         msg = msg.replace('', '<')
#     while '>' in msg:
#         msg = msg.replace('', '>')
#     x = requests.get(f'https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage?chat_id=@erbrtnytyumynty&text={msg}') 
    # await bot.send_message(-config.DEBUG_CHANNEL_ID, str(msg), parse_mode=types.ParseMode.HTML)


# class TgLoggerHandler(logging.Handler):
#     def emit(self, record):
#         print(record)
#         msg = self.format(record)
#         send_log_channel(msg)
#         # print(x)

# tg_handler = TgLoggerHandler()
# tg_handler.setLevel(logging.ERROR)
# stream_handler = logging.StreamHandler()
# stream_handler.setLevel(logging.INFO)




-1001221479581