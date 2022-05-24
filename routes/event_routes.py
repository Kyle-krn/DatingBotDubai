from aiogram import types, Dispatcher, Bot
from loader import dp, bot, db
import asyncio
from data.config import TORTOISE_ORM, WEBHOOK_URL
from tasks import scheduler
from fastapi import APIRouter
from utils.postgres_func import init_postgres_func

from utils.postgres_func.insert_data_table import init_data_db


event_router = APIRouter()


@event_router.on_event("startup")
async def on_startup():
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(
            url=WEBHOOK_URL
        )
    await db.init(config=TORTOISE_ORM)
    await init_data_db()
    await init_postgres_func()
    asyncio.create_task(scheduler(bot))


@event_router.post("/bot")
async def bot_webhook(update: dict):
    telegram_update = types.Update(**update)
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    await dp.process_update(telegram_update)


@event_router.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.storage.close()
    await dp.storage.wait_closed()
    await bot.session.close()