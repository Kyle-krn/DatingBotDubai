from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from tortoise import Tortoise
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from data import config

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
# storage = MemoryStorage()
storage = RedisStorage2('localhost', 6379, db=0, pool_size=10, prefix='state_aio')

dp = Dispatcher(bot, storage=storage)

db = Tortoise()
