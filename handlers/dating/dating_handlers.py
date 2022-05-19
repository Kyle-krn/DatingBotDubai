import re
from data.config import PHOTO_TYPES, VIDEO_TYPES
from loader import dp, bot
from aiogram import types
from models import models
from datetime import datetime, date
from tortoise.queryset import Q
from keyboards.inline.inline_keyboards import like_keyboard, one_button_keyboard
from utils.text_for_ad import generate_ad_text
from utils.zodiak import zodiac_sign
import redis
import json
from handlers.view_relations.views_handlers import view_your_likes_handler
import tortoise
from aiogram.utils.exceptions import BotBlocked

redis_cash_1 = redis.Redis(db=1)

@dp.message_handler(commands=['dating'])
@dp.message_handler(regexp="^(👥 Найти пару)$")
async def search_dating(message: types.Message, last_view_id: int = None):
    user = await models.UserModel.get(tg_id=message.chat.id)
    if user.end_registration is False:
        return await message.answer("Вы не закончили регистрацию")
    elif user.verification is False:
        return await message.answer("Ваш профиль еще не верифицирован")
    queryset_cache = redis_cash_1.get(str(message.chat.id))
    
    if queryset_cache is None or len(json.loads(queryset_cache)) == 0:
        query = Q(relation__percent_compatibility__gt=0) & Q(target_user__verification=True) & Q(target_user__ban=False) & Q(like=False) & Q(superlike=False)
        user_view = user.user_view.filter(query).order_by('dislike', 'count_view', '-relation__percent_compatibility')        #.limit(1)
        if last_view_id:
            user_view = user_view.exclude(id=last_view_id)
        target_users_list = await user_view
        if len(target_users_list) == 0:
            return await message.answer("К сожалению подходящих пар не найдено.")
        user_view = target_users_list.pop(0)
        redis_cash_1.set(str(message.chat.id), json.dumps([v.id for v in target_users_list]), 5*60)
    else:
        queryset_cache = json.loads(queryset_cache)
        try:
            user_view = await models.UserView.get(id = queryset_cache.pop(0))
        except tortoise.exceptions.DoesNotExist:
            pass
        ttl = redis_cash_1.ttl(str(message.chat.id))
        if ttl > 0:
            redis_cash_1.set(str(message.chat.id), json.dumps(queryset_cache), ttl)

    target_user = await user_view.target_user
    avatar = await target_user.avatar
    if target_user.verification == False or avatar.file_type is None:
        return await search_dating(message)
    
    user_view.count_view += 1
    await user_view.save()
    
    

    text = await generate_ad_text(target_user=target_user, relation=await user_view.relation)
    if avatar.file_type is None:
        pass
    elif avatar.file_type.lower() in PHOTO_TYPES:
        await message.answer_photo(photo=avatar.file_id, caption=text, reply_markup=await like_keyboard(view_id=user_view.id, superlike_count=user.superlike_count)) 
    elif avatar.file_type.lower() in VIDEO_TYPES:
        await message.answer_video(video=avatar.file_id, caption=text, reply_markup=await like_keyboard(view_id=user_view.id, superlike_count=user.superlike_count))
    


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'reaction')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'y_like_reaction')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'single_reaction')
async def reaction_ad_handler(call: types.CallbackQuery):
    command = call.data.split(':')[1]
    view_id = call.data.split(':')[2]
    if call.data.split(':')[0] == 'y_like_reaction':
        offset = int(call.data.split(':')[3])
    view = await models.UserView.get(id=view_id)
    user = await view.user
    target_user = await view.target_user
    reverse_view = await models.UserView.get(Q(user=target_user) & Q(target_user=user))
    if view.like or view.superlike:
        await call.message.delete()
        return await call.answer("Вы уже реагировали на данное объявление.")        
    # user = await models.UserModel.get(tg_id=call.message.chat.id)

    if command == "like":
        text = "LIKE 👍\n\n"
        if not user.end_premium:
            if user.free_likes <= 0:
                return await call.message.answer(text="У вас закончились лайки на сегодня, вы можете купить Gold статус и ставить неограниченное число лайков.",
                                                 reply_markup=await one_button_keyboard(text="Купить Gold на 1 месяц", 
                                                                                        callback="buy:gold:1"))
            user.free_likes -= 1
            await user.save()
        view.like = True
        if view.like and reverse_view.like:
            await call.message.delete()
            await view.save()
            return await mutal_like_func(message=call.message,
                                         user=user,
                                         target_user=target_user,
                                         relation=await view.relation,)
        else:
            if target_user.end_premium is None:
                await null_premium_message(chat_id=target_user.tg_id)
    elif command == "superlike":
        if user.superlike_count <= 0:
            return await call.message.answer("У вас нет суперлайков.",reply_markup=await one_button_keyboard(text="Купить 10 суперлайков", callback="buy:likes:10"))
        else:
            text = "SUPERLIKE ⭐\n\n"
            view.like = True
            view.superlike = True
            if view.like and reverse_view.like:
                await call.message.delete()
                await view.save()
                return await mutal_like_func(message = call.message,
                                             user=user,
                                             target_user=target_user,
                                             relation=await view.relation)

            start_text_msg = f"Пользователь {user.name} отправил вам суперлайк!\n\n"
            end_text_msg = f"\n\nХотите с ним познакомиться? Пишите: @{user.tg_username}"
            if user.tg_username is None:
                end_text_msg = "\n\nИзвините аккаунт пользователя скрыт, возможно он напишет вам сам"
                await null_tg_username_answer(chat_id=user.tg_id)
           
            text_msg = start_text_msg + await generate_ad_text(target_user=target_user, relation=await view.relation) + end_text_msg
            avatar_tar = await target_user.avatar
            avatar_user = await user.avatar
            keyboard = await like_keyboard(view_id=reverse_view.id, superlike_count=target_user.superlike_count, callback="single_reaction")
            if avatar_user.file_type.lower() in PHOTO_TYPES:
                try:
                    await bot.send_photo(chat_id=target_user.tg_id, photo=avatar_user.file_id, caption=text_msg, reply_markup=keyboard) 
                except BotBlocked:
                    pass
            elif avatar_user.file_type.lower() in VIDEO_TYPES:
                try:
                    await bot.send_video(chat_id=target_user.tg_id, video=avatar_tar.file_id, caption=text_msg, reply_markup=keyboard)
                except BotBlocked:
                    pass
            user.superlike_count -= 1
            await user.save()

    elif command == "dislike":
        view.dislike = True
        text = "DISLIKE 👎 \n\n"

    await view.save()
    caption = call.message.caption
    caption = text+caption
    await call.message.edit_caption(caption=caption)
    if call.data.split(':')[0] != 'single_reaction':
        if view.superlike is False:
            if call.data.split(':')[0] == 'reaction':
                return await search_dating(call.message, last_view_id=view_id)
            else:
                call.data = f"your_likes:{offset+1}"
                return await view_your_likes_handler(call, last_view_id=int(view_id))
        else:
            return await call.message.answer(f"{target_user.name} получил ваш контакт!")
        



async def mutal_like_func(message: types.Message, 
                          user: models.UserModel,
                          target_user: models.UserModel, 
                          relation: models.UsersRelations):
    avatar_user = await user.avatar
    avatar_tar = await target_user.avatar
    start_text = "У вас новая пара!\n\n"
    end_text = "\n\nПора познакомиться, пишите: "
    
    text = start_text + await generate_ad_text(target_user=target_user, relation=await relation)
    
    if target_user.tg_username is None:
        text += "\n\nИзвините аккаунт пользователя скрыт, возможно он напишет вам сам"
        await null_tg_username_answer(chat_id=target_user.tg_id)
    else:
        text += end_text + f"@{target_user.tg_username}"
    if avatar_tar.file_type.lower() in PHOTO_TYPES:
        await message.answer_photo(photo=avatar_tar.file_id, caption=text) 
    elif avatar_tar.file_type.lower() in VIDEO_TYPES:
        await message.answer_video(video=avatar_tar.file_id, caption=text)

    text = start_text + await generate_ad_text(target_user=user, relation=await relation)
    if user.tg_username is None:
        text += "\n\nИзвините аккаунт пользователя скрыт, возможно он напишет вам сам"
        await null_tg_username_answer(chat_id=user.tg_id)
    else:
        text += end_text + f"@{user.tg_username}"

    if avatar_user.file_type.lower() in PHOTO_TYPES:
        try:
            await bot.send_photo(chat_id=target_user.tg_id, photo=avatar_user.file_id, caption=text) 
        except BotBlocked:
            pass
    elif avatar_user.file_type.lower() in VIDEO_TYPES:
        try:
            await bot.send_video(chat_id=target_user.tg_id, video=avatar_user.file_id, caption=text)
        except BotBlocked:
            pass
    await models.MutualLike.create(user=user, target_user=target_user)


async def null_tg_username_answer(chat_id: int):
    text = "Пользователю [Имя] не пришел ваш контакт, добавьте [@имя бота] в исключения, "  \
           "для этого пройдите в меню настройки пересылки сообщений для Telegram: "  \
           "Настройки -> Конфиденциальность -> Пересылка сообщений"
    try:
        await bot.send_message(chat_id=chat_id, text=text)
    except BotBlocked:
        pass


async def null_premium_message(chat_id: int):
    text = "Тебя лайкнули, чтобы видеть профили, которым ты понравился подключи тариф Gold"
    try:
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=await one_button_keyboard(text="Подключить тариф Gold", callback="buy:gold:1"))
    except BotBlocked:
        pass