import asyncio
import aioschedule
from datetime import datetime, timedelta
from data.config import PHOTO_TYPES, VIDEO_TYPES
from keyboards.inline.inline_keyboards import like_keyboard
from models import models
from aiogram import Bot
from tortoise.queryset import Q
from models.row_user_likes import rowsql_likes
from utils.text_for_ad import generate_ad_text
from aiogram.utils.exceptions import BotBlocked


async def update_likes():
    '''Раз в день добавляет лайки и суперлайки'''
    await models.UserModel.filter(superlike_count=0).update(superlike_count=1)
    await models.UserModel.filter(free_likes__lt=3).update(free_likes=3)

async def spam_motivation_message(bot: Bot):
    '''Раз в час делает рассылку'''
    list_users = await models.UserModel.filter(Q(ban=False) & Q(tmz__isnull=False))
    for user in list_users:
        if user.spam_ad_ids is None:
            user.spam_ad_ids = []
            await user.save()
        local_time_user = datetime.utcnow() + timedelta(hours=user.tmz)
        if datetime(day=local_time_user.day,            # Если у юзера день 
                    month=local_time_user.month, 
                    year=local_time_user.year,
                    hour=8) <= local_time_user <= datetime(day=local_time_user.day, 
                                                           month=local_time_user.month, 
                                                           year=local_time_user.year,
                                                           hour=22):
            if user.end_registration is False:
                try:
                    await bot.send_message(chat_id=user.tg_id, text="Тект для тех кто не закончил регу")
                except BotBlocked:
                    pass
                continue
            elif user.verification is True:
                your_likes_view = await rowsql_likes(user_id=user.id)
                likes_view = None
                user_view = None
                if len(your_likes_view) > 0:
                    your_likes_id = [i['id'] for i in your_likes_view]
                    while True:
                        '''Ищем просмотры где лайкнули юзера'''
                        if len(your_likes_id) == 0:
                            break
                        view_id = your_likes_id.pop(0)
                        if view_id not in user.spam_ad_ids:
                            likes_view = await models.UserView.get(id=view_id)
                            user.spam_ad_ids.append(likes_view.id)
                            await user.save()
                            break
                query = Q(relation__percent_compatibility__gt=0) & Q(target_user__verification=True) & Q(target_user__ban=False) & Q(like=False) & Q(superlike=False)
                user_views_list = await user.user_view.filter(query).order_by('dislike', 'count_view', '-relation__percent_compatibility')
                if len(user_views_list) > 0:
                    while True:
                        '''Ищем просмотры юзера'''
                        if len(user_views_list) == 0:
                            break
                        user_view_row = user_views_list.pop(0)
                        if user_view_row.id not in user.spam_ad_ids:
                            user_view = user_view_row
                            user.spam_ad_ids.append(user_view_row.id)
                            await user.save()
                            break
                if likes_view is not None:
                    user_view = likes_view
                    text = "<b>Тебя лайкнули! Если тебе нравится этот профиль, поставь лайк в ответ и получи контакт для общения!</b>\n\n"
                elif user_view is not None:
                    text = "<b>Тебе нравится этот профиль? Что если это взаимно? Поставь лайк и возможно это принесет тебе новое знакомство!</b>\n\n"
                else:
                    continue

                user_view.count_view += 1
                await user_view.save()
                target_user = await user_view.target_user
                avatar = await target_user.avatar
                    
                text += await generate_ad_text(target_user=target_user, relation=await user_view.relation)
                if avatar.file_type.lower() in PHOTO_TYPES:
                    try:
                        await bot.send_photo(chat_id=user.tg_id, photo=avatar.file_id, caption=text, reply_markup=await like_keyboard(view_id=user_view.id, superlike_count=user.superlike_count)) 
                    except BotBlocked:
                        pass
                elif avatar.file_type.lower() in VIDEO_TYPES:
                    try:
                        await bot.send_video(chat_id=user.tg_id, video=avatar.file_id, caption=text, reply_markup=await like_keyboard(view_id=user_view.id, superlike_count=user.superlike_count))
                    except BotBlocked:
                        pass


async def scheduler(bot):
    aioschedule.every(1).hours.do(spam_motivation_message, bot)
    aioschedule.every().day.at("12:00").do(update_likes)
    while True:
        await aioschedule.run_pending() 
        await asyncio.sleep(1)