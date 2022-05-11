from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from fastapi import FastAPI
from tortoise import Tortoise
from aiogram.contrib.fsm_storage.redis import RedisStorage2
import logging
from data import config
from fastapi.templating import Jinja2Templates

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = RedisStorage2('localhost', 6379, db=0, pool_size=10, prefix='state_aio')

dp = Dispatcher(bot, storage=storage)

db = Tortoise()

app = FastAPI()
# app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")