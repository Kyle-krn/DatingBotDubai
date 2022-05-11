from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from fastapi import FastAPI, Request
from tortoise import Tortoise
from aiogram.contrib.fsm_storage.redis import RedisStorage2
import logging
from data import config
from fastapi.templating import Jinja2Templates
from fastapi_login import LoginManager #Loginmanager Class

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = RedisStorage2('localhost', 6379, db=0, pool_size=10, prefix='state_aio')

dp = Dispatcher(bot, storage=storage)

db = Tortoise()

app = FastAPI()
from fastapi.responses import RedirectResponse,HTMLResponse

SECRET = "secret-key"
# To obtain a suitable secret key you can run | import os; print(os.urandom(24).hex())




# class UnAn(BaseException):
#     pass


# manager = LoginManager(SECRET,token_url="/auth/login",custom_exception=UnAn, use_cookie=True)
# manager.cookie_name = "auth"
templates = Jinja2Templates(directory="templates")




# @app.exception_handler(UnAn)
# def auth_exception_handler(request: Request, exc):
#     """
#     Redirect the user to the login page if not logged in
#     """
#     return RedirectResponse(url='/login')