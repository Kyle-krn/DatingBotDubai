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

redis_cash_1 = redis.Redis(db=1)

@dp.message_handler(commands=['dating'])
@dp.message_handler(regexp="^(👥 Найти пару)$")
async def search_dating(message: types.Message, last_view_id: int = None):
    # photo_types = ('jpeg', 'jpg', "webm", "png")
    # video_types = ("mp4", "avi")
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

    user_view.count_view += 1
    await user_view.save()
    target_user = await user_view.target_user
    avatar = await target_user.avatar
    

    text = await generate_ad_text(target_user=target_user, relation=await user_view.relation)

    if avatar.file_type.lower() in PHOTO_TYPES:
        await message.answer_photo(photo=avatar.file_id, caption=text, reply_markup=await like_keyboard(view_id=user_view.id, superlike_count=user.superlike_count)) 
    elif avatar.file_type.lower() in VIDEO_TYPES:
        await message.answer_video(video=avatar.file_id, caption=text, reply_markup=await like_keyboard(view_id=user_view.id, superlike_count=user.superlike_count))
    


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'reaction')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'y_like_reaction')
async def reaction_ad_handler(call: types.CallbackQuery):
    view_id = call.data.split(':')[2]
    view = await models.UserView.get(id=view_id)
    user = await view.user
    target_user = await view.target_user
    reverse_view = await models.UserView.get(Q(user=target_user) & Q(target_user=user))
    if view.like or view.superlike:
        await call.message.delete()
        return await call.answer("Вы уже реагировали на данное объявление.")        
    user = await models.UserModel.get(tg_id=call.message.chat.id)
    command = call.data.split(':')[1]
    # print(call.data)
    if command == "like":
        text = "LIKE 👍\n\n"
        if not user.end_premium:
            if user.free_likes <= 0:
                return await call.message.answer("У вас закончились лайки на сегодня, вы можете купить Gold статус и ставить неограниченное число лайков.",
                                                  reply_markup=await one_button_keyboard(text="Купить Gold на 1 месяц", callback="buy:gold:1"))
            user.free_likes -= 1
            await user.save()
        view.like = True
        if view.like and reverse_view.like:
            await mutal_like_func(message = call.message,
                                 user=user,
                                 target_user=target_user,
                                 relation=await view.relation,)
    elif command == "superlike":
        if user.superlike_count <= 0:
            return await call.message.answer("У вас нет суперлайков.",reply_markup=await one_button_keyboard(text="Купить 10 суперлайков", callback="buy:likes:10"))
        else:
            text = "SUPERLIKE ⭐\n\n"
            view.like = True
            view.superlike = True
            text_1 = f"Пользователь @{user.tg_username} отправил вам суперлайк!\n\n"
            text_msg = text_1 + await generate_ad_text(target_user=target_user, relation=await view.relation)
            avatar_tar = await target_user.avatar
            avatar_user = await user.avatar
            if avatar_user.file_type.lower() in PHOTO_TYPES:
                await bot.send_photo(chat_id=target_user.tg_id, photo=avatar_user.file_id, caption=text_msg) 
            elif avatar_user.file_type.lower() in VIDEO_TYPES:
                await bot.send_video(chat_id=target_user.tg_id, video=avatar_tar.file_id, caption=text_msg)

            # await bot.send_message(chat_id=target_user.tg_id, text=text_msg)
            user.superlike_count -= 1
            await user.save()

    elif command == "dislike":
        view.dislike = True
        text = "DISLIKE 👎 \n\n"
    await view.save()
    caption = call.message.caption
    caption = text+caption
    await call.message.edit_caption(caption=caption)
    if call.data.split(':')[0] == 'reaction':
        # if call.message.photo:
        
        return await search_dating(call.message, last_view_id=view_id)
    else:
        return await view_your_likes_handler(call, last_view_id=view_id)


async def mutal_like_func(message: types.Message, 
                          user: models.UserModel,
                          target_user: models.UserModel, 
                          relation: models.UsersRelations):
    
    avatar_user = await user.avatar
    avatar_tar = await target_user.avatar
    text_1 = "У вас новая пара!\n\n"
    text = text_1 + await generate_ad_text(target_user=target_user, relation=await relation)
    
    
    if avatar_tar.file_type.lower() in PHOTO_TYPES:
        await message.answer_photo(photo=avatar_tar.file_id, caption=text) 
    elif avatar_tar.file_type.lower() in VIDEO_TYPES:
        await message.answer_video(video=avatar_tar.file_id, caption=text)
        
    
    
    text = text_1 + await generate_ad_text(target_user=user, relation=await relation)
    # await bot.send_message(chat_id=target_user.tg_id, text=text)
    
    if avatar_user.file_type.lower() in PHOTO_TYPES:
        await bot.send_photo(chat_id=target_user.tg_id, photo=avatar_user.file_id, caption=text) 
    elif avatar_user.file_type.lower() in VIDEO_TYPES:
        await bot.send_video(chat_id=target_user.tg_id, video=avatar_user.file_id, caption=text)

    await models.MutualLike.create(user=user, target_user=target_user)

    