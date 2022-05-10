
from fastapi import FastAPI
from aiogram import types, Dispatcher, Bot
from loader import dp, bot, db
import asyncio
from data.config import BOT_TOKEN, TORTOISE_ORM
from tasks import scheduler


app = FastAPI()

WEBHOOK_PATH = f"/bot/{BOT_TOKEN}"
WEBHOOK_URL = "https://1913-178-155-4-29.ngrok.io" + "/bot"

@app.on_event("startup")
async def on_startup():
    webhook_info = await bot.get_webhook_info()
    print(webhook_info)
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(
            url=WEBHOOK_URL
        )
    await db.init(config=TORTOISE_ORM)
    asyncio.create_task(scheduler(bot))

@app.post("/bot")
async def bot_webhook(update: dict):
    # print(update)
    telegram_update = types.Update(**update)
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    await dp.process_update(telegram_update)

@app.get('/test')
async def test():
    return "hi"

@app.on_event("shutdown")
async def on_shutdown():
    await dp.storage.close()
    await dp.storage.wait_closed()
    await bot.delete_webhook()
    await bot.session.close()
    