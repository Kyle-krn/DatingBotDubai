import asyncio
import aioschedule
from datetime import datetime, timedelta
from data.config import PHOTO_TYPES, VIDEO_TYPES
from keyboards.inline.inline_keyboards import like_keyboard, one_button_keyboard
from models import models
from aiogram import Bot
from tortoise.queryset import Q
from models.db_query import calculation_users
from utils.text_for_ad import generate_ad_text
from aiogram.utils.exceptions import BotBlocked


async def update_likes():
    '''Раз в день добавляет лайки и суперлайки'''
    await models.UserModel.filter(superlike_count=0).update(superlike_count=1)
    await models.UserModel.filter(free_likes__lt=3).update(free_likes=3)

async def spam_motivation_message(bot: Bot):
    '''Раз в час делает рассылку'''
    list_users = await models.UserModel.filter(Q(ban=False) & Q(place_id__isnull=False))
    for user in list_users:
        if user.spam_ad_ids is None:
            user.spam_ad_ids = []
            await user.save()
        tmz = (await user.place).tmz
        # if user.id == 7:
        #     tmz = -5
        local_time_user = datetime.utcnow() + timedelta(hours=tmz)
        if datetime(day=local_time_user.day,            # Если у юзера день 
                    month=local_time_user.month, 
                    year=local_time_user.year,
                    hour=10) <= local_time_user <= datetime(day=local_time_user.day, 
                                                           month=local_time_user.month, 
                                                           year=local_time_user.year,
                                                           hour=22):
            avatar = await user.avatar
            
            if user.end_registration is False:
                try:
                    await bot.send_message(chat_id=user.tg_id, text="Мы заметили, что вы не закончили регистрацию! Пройдите регистрацию полностью, чтобы начать знакомиться!",
                                           reply_markup=await one_button_keyboard(text="Закончить регистрацию", callback="end_registration_user:"))
                except BotBlocked:
                    pass
                continue
            elif avatar.file_id is None:
                    text =  "Мы заметили, что у тебя все еще нет аватарки! \n"   \
                       "Без фотографии профиля ты не будешь появляться в ленте других пользователей"  \
                       ", не будешь получать лайки и ни с кем не познакомишься :("  \
                       "Пожалуйста установите фотографию профиля по кнопке добавить фото"
                    await bot.send_message(chat_id=user.tg_id, text=text, reply_markup=await one_button_keyboard(text="Добавить фото", callback="change_ava:"))
                    continue
            elif user.verification is True:
                users_like_you = await calculation_users(user_id=user.id, like_catalog=True)
                likes_view = None
                user_view = None
                if len(users_like_you) > 0:
                    while len(users_like_you) > 0:
                        '''Ищем просмотры где лайкнули юзера'''
                        target_user_row = users_like_you.pop(0)
                        if target_user_row['target_id'] not in user.spam_ad_ids:
                            target_user = await models.UserModel.get(id=target_user_row['target_id'])
                            likes_view = await models.UserView.get_or_create(user=user, target_user=target_user)
                            likes_view = likes_view[0]
                            user.spam_ad_ids.append(target_user_row['target_id'])
                            await user.save()
                            await send_motivation(user=user, user_view=likes_view, likes=True, general_percent=target_user_row['general_percent'], bot=bot)
                            break
                    if likes_view:
                        continue
                users_ralation = await calculation_users(user_id=user.id)
                if len(users_ralation ) > 0:
                    while len(users_ralation)  > 0:
                        '''Ищем просмотры юзера'''
                        target_user_row = users_ralation.pop(0)
                        if target_user_row['target_id'] not in user.spam_ad_ids:
                            target_user = await models.UserModel.get(id=target_user_row['target_id'])
                            user_view = await models.UserView.get_or_create(user=user, target_user=target_user)
                            user_view = user_view[0]
                            user.spam_ad_ids.append(target_user_row['target_id'])
                            await user.save()
                            await send_motivation(user=user, user_view=user_view, likes=False, general_percent=target_user_row['general_percent'], bot=bot)
                            break
                    continue
                

async def send_motivation(user: models.UserModel, 
                          user_view: models.UserView, 
                          general_percent: int, 
                          likes: bool, bot):
    text = "<b>Тебя лайкнули! Если тебе нравится этот профиль, поставь лайк в ответ и получи контакт для общения!</b>\n\n" if likes is True \
           else "<b>Тебе нравится этот профиль? Что если это взаимно? Поставь лайк и возможно это принесет тебе новое знакомство!</b>\n\n"
    user_view.count_view += 1
    await user_view.save()
    target_user = await user_view.target_user
    avatar = await target_user.avatar
        
    text += await generate_ad_text(target_user=target_user, general_percent=general_percent)
    if avatar.file_type.lower() in PHOTO_TYPES:
        try:
            await bot.send_photo(chat_id=user.tg_id, photo=avatar.file_id, caption=text, reply_markup=await like_keyboard(view_id=user_view.id, 
                                                                                                                            superlike_count=user.superlike_count,
                                                                                                                            general_percent=general_percent,
                                                                                                                            callback="single_reaction")) 
        except BotBlocked:                                                                      
            pass
    elif avatar.file_type.lower() in VIDEO_TYPES:
        try:
            await bot.send_video(chat_id=user.tg_id, video=avatar.file_id, caption=text, reply_markup=await like_keyboard(view_id=user_view.id, 
                                                                                                                          superlike_count=user.superlike_count,
                                                                                                                           general_percent=general_percent,
                                                                                                                           callback="single_reaction"))
        except BotBlocked:
            pass

async def scheduler(bot):
    aioschedule.every(1).hours.do(spam_motivation_message, bot)
    aioschedule.every().day.at("12:00").do(update_likes)
    while True:
        await aioschedule.run_pending() 
        await asyncio.sleep(1)