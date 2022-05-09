import asyncio
import aioschedule
from datetime import datetime, timedelta
from models import models
from aiogram import Bot
from tortoise.queryset import Q
async def update_likes():
    await models.UserModel.filter(superlike_count=0).update(superlike_count=1)
    await models.UserModel.filter(free_likes__lt=3).update(free_likes=3)

    # await bot.send_message(chat_id=390442593, text=f'{x[0]}')
async def spam_motivation_message(bot: Bot):
    list_users = await models.UserModel.filter(Q(ban=False) & Q(tmz__isnull=False))
    for user in list_users:
        local_time_user = datetime.utcnow() + timedelta(hours=user.tmz)
        if datetime(day=local_time_user.day, 
                    month=local_time_user.month, 
                    year=local_time_user.year,
                    hour=8) <= local_time_user <= datetime(day=local_time_user.day, 
                                                           month=local_time_user.month, 
                                                           year=local_time_user.year,
                                                           hour=22):
            if user.end_registration is False:
                return await bot.send_message(chat_id=user.tg_id, text="Тект для тех кто не закончил регу")
            else:
                pass
            # вызываем юзера и смотрим закончил ли он регистрацию в случае отправяем месседж и выходим
            # инчае вызываем сырой запрос лайков пользователю, если есть отдаем и выходим
            # иначе вызываем запрос знакомств, если есть отдаем и выходим
            print(user, local_time_user)
# async def scheduler(bot):
# 	aioschedule.every(1).seconds.do(test_cron, bot)
#     print("i")
#     while True:
# 		await aioschedule.run_pending()
# 		await asyncio.sleep(1)

async def scheduler(bot):
    print("i")
    # aioschedule.every(10).seconds.do(spam_motivation_message, bot)
    aioschedule.every().day.at("12:00").do(update_likes)
    while True:
        await aioschedule.run_pending() 
        await asyncio.sleep(1)