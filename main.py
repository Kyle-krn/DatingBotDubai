
from aiogram import types, Dispatcher, Bot
from loader import dp, bot, db
import asyncio
from data.config import BOT_TOKEN, TORTOISE_ORM
from tasks import scheduler
from models import models
from tortoise.queryset import Q

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

WEBHOOK_PATH = f"/bot/{BOT_TOKEN}"
WEBHOOK_URL = "https://1913-178-155-4-29.ngrok.io" + "/bot"

@app.on_event("startup")
async def on_startup():
    webhook_info = await bot.get_webhook_info()
    # print(webhook_info)
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


@app.on_event("shutdown")
async def on_shutdown():
    await dp.storage.close()
    await dp.storage.wait_closed()
    await bot.delete_webhook()
    await bot.session.close()
    


@app.get("/verif", response_class=HTMLResponse)
async def test(request: Request):
    not_verif_user = await models.UserModel.filter(Q(verification=False) & Q(ban=False)).order_by('-last_verification_time')
    data_users = []
    for user in not_verif_user:
        avatar = await user.avatar
        data_users.append({"name": user.name,
                           "tg_username": user.tg_username,
                           "file_path": avatar.file_path,
                           "photo_bool": avatar.photo_bool,
                           "hobbies": await user.hobbies})

    return templates.TemplateResponse("item.html", {"request": request, "users": data_users})
