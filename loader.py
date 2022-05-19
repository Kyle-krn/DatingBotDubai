import os
from aiogram import Bot, Dispatcher, types
from fastapi import FastAPI
from tortoise import Tortoise
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from data import config
from utils.misc import logging
from fastapi.templating import Jinja2Templates

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = RedisStorage2('localhost', 6379, db=0, pool_size=10, prefix='state_aio')

dp = Dispatcher(bot, storage=storage)

db = Tortoise()

app = FastAPI()

templates = Jinja2Templates(directory="templates")


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
