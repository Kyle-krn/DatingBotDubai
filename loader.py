import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from fastapi import FastAPI, Request
import requests
from tortoise import Tortoise
from aiogram.contrib.fsm_storage.redis import RedisStorage2
import logging
from data import config
from fastapi.templating import Jinja2Templates
from fastapi_login import LoginManager #Loginmanager Class
import urllib.parse

def send_log_channel(msg):
    while '<' in msg:
        msg = msg.replace('', '<')
    while '>' in msg:
        msg = msg.replace('', '>')
    requests.get(f'https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage?chat_id=@erbrtnytyumynty&text={urllib.parse.quote(msg)}') 
    # await bot.send_message(-config.DEBUG_CHANNEL_ID, str(msg), parse_mode=types.ParseMode.HTML)


class TgLoggerHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        send_log_channel(msg)


tg_handler = TgLoggerHandler()
tg_handler.setLevel(logging.ERROR)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.ERROR)

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = RedisStorage2('localhost', 6379, db=0, pool_size=10, prefix='state_aio')

dp = Dispatcher(bot, storage=storage)

db = Tortoise()

app = FastAPI()
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
print(BASE_DIR)
SECRET = "secret-key"

templates = Jinja2Templates(directory="templates")
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO, handlers=[tg_handler, stream_handler] 
                    )