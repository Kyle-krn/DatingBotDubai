import asyncio

from aiogram import types, Dispatcher
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled
from models import models
from handlers.start import bot_start
class ThrottlingMiddleware(BaseMiddleware):
    """
    Simple middleware
    """

    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()
        if handler:
            limit = getattr(handler, "throttling_rate_limit", self.rate_limit)
            key = getattr(handler, "throttling_key", f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"
        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            await self.message_throttled(message, t)
            raise CancelHandler()

    async def message_throttled(self, message: types.Message, throttled: Throttled):
        if throttled.exceeded_count <= 2:
            await message.reply("Too many requests!")


class BanMiddleware(BaseMiddleware):
    async def on_process_message(self, message: types.Message, data: dict):
        await self.check_ban_user(message)
    
    async def on_process_callback_query(self, call: types.CallbackQuery, data: dict):
        await self.check_ban_user(call.message)
    
    async def check_ban_user(self, message: types.Message):
        try:
            user = await models.UserModel.get(tg_id=message.chat.id)
        except Exception as e:
            await bot_start(message)
            raise CancelHandler()
        if user.tg_username != message.chat.username:
            user.tg_username = message.chat.username
            await user.save()
        if user.name != message.chat.full_name:
            user.name = message.chat.full_name
            await user.save()
            
        if user.ban is True:
            raise CancelHandler()
        

