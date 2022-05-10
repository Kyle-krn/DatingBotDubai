import asyncio
import aioschedule
from datetime import datetime, timedelta
from data.config import PHOTO_TYPES, VIDEO_TYPES
from handlers.dating.dating_handlers import search_dating
from keyboards.inline.inline_keyboards import like_keyboard
from models import models
from aiogram import Bot
from tortoise.queryset import Q
from models.row_user_likes import rowsql_likes
from utils.text_for_ad import generate_ad_text

async def update_likes():
    await models.UserModel.filter(superlike_count=0).update(superlike_count=1)
    await models.UserModel.filter(free_likes__lt=3).update(free_likes=3)

async def spam_motivation_message(bot: Bot):
    # photo_types = ('jpeg', 'jpg', "webm", "png")
    # video_types = ("mp4", "avi")
    list_users = [await models.UserModel.get(id=123)]
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
            elif user.verification is True:
                query = Q(relation__percent_compatibility__gt=0) & Q(target_user__verification=True) & Q(target_user__ban=False) & Q(like=False) & Q(superlike=False)
                user_view = user.user_view.filter(query).order_by('dislike', 'count_view', '-relation__percent_compatibility').limit(1)        #.limit(1)
                user_view = await user_view
                your_likes_view = await rowsql_likes(user_id=user.id)

                if len(your_likes_view) > 0:
                    your_likes_id = [i['id'] for i in your_likes_view][0]
                    user_view = await models.UserView.get(id=your_likes_id)
                    text = "<b>Тебя лайкнули! Если тебе нравится этот профиль, поставь лайк в ответ и получи контакт для общения!</b>\n\n"
                else:
                    if len(user_view) > 0:
                        user_view = user_view[0]
                        text = "<b>Тебе нравится этот профиль? Что если это взаимно? Поставь лайк и возможно это принесет тебе новое знакомство!</b>\n\n"
                    else:
                        return

                user_view.count_view += 1
                await user_view.save()
                target_user = await user_view.target_user
                avatar = await target_user.avatar
                    
                text += await generate_ad_text(target_user=target_user, relation=await user_view.relation)
                if avatar.file_type.lower() in PHOTO_TYPES:
                    return await bot.send_photo(chat_id=user.tg_id, photo=avatar.file_id, caption=text, reply_markup=await like_keyboard(view_id=user_view.id, superlike_count=user.superlike_count)) 
                elif avatar.file_type.lower() in VIDEO_TYPES:
                    return await bot.send_video(chat_id=user.tg_id, video=avatar.file_id, caption=text, reply_markup=await like_keyboard(view_id=user_view.id, superlike_count=user.superlike_count))
            


async def scheduler(bot):
    print("i")
    aioschedule.every(1).hours.do(spam_motivation_message, bot)
    aioschedule.every().day.at("12:00").do(update_likes)
    while True:
        await aioschedule.run_pending() 
        await asyncio.sleep(1)