from typing import Union
from datetime import datetime
from typing import Any, List
from data.config import PHOTO_TYPES, VIDEO_TYPES
from loader import dp
from aiogram import types
from models import models
from keyboards.inline.inline_keyboards import one_button_keyboard, view_relation_keyboard
from tortoise.queryset import Q
from keyboards.inline.inline_keyboards import like_keyboard, mutal_likes_keyboard

import redis
import json
from utils.text_for_ad import generate_ad_text
from models.db_query import calculation_users
from utils.zodiak import zodiac_sign
# from models.db_query import rowsql_likes
redis_cash_2 = redis.Redis(db=2)

@dp.message_handler(commands=['likes'])
@dp.message_handler(regexp="^(💑 Симпатии)$")
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'back_likes')
async def view_relations_handler(message: Union[types.CallbackQuery, types.Message]):
    text = '<b>"Тебя лайкнули"</b> - когда пользователи видят твою анкету ' \
           'и нажимают лайк, они попадают в эту вкладку.\n\n' \
           '<b>"Взаимные лайки"</b> - когда пользователь поставил лайк тебе, ' \
           'а ты поставил лайк ему, у вас образуется взаимный лайк. ' \
           'К взаимным лайкам всегда можно перейти через эту вкладку. ' \
           'Мы отправим твой контакт в случае взаимного лайка 💑\n\n' \
           'Проверь, заполнено ли поле Username в настройках профиля ' \
           'Telegram или добавь @zodier_bot в исключения. Для этого пройди ' \
           'в меню настройки пересылки сообщений для Telegram: ' \
           '<b>Настройки -> Конфиденциальность -> Пересылка сообщений.</b>'
    if isinstance(message, types.CallbackQuery):
        tg_id = message.message.chat.id
    else:
        tg_id = message.chat.id
    user = await models.UserModel.get(tg_id=tg_id)
    if user.end_registration is False:
        return await message.answer("Вы не закончили регистрацию")
    elif user.verification is False:
        avatar = await user.avatar
        if avatar.file_id is None:
            return await message.answer("Чтобы начать знакомиться добавьте ваше фото!", reply_markup=await one_button_keyboard(text="Добавить фото", 
                                                                                                                               callback="change_ava:"))
        else:
            return await message.answer("Мы проверяем ваше фото, когда проверка закончится мы Вам сообщим и вы сможете начать знакомиться!")
    
    count_users_like_you = await calculation_users(user_id=user.id, like_catalog=True, count=True)
    count_users_like_you = count_users_like_you[0]['count']
    query = Q(Q(user=user) | Q(target_user=user)) & Q(Q(user__verification=True) & Q(target_user__verification=True))
    count_mutal_like = await models.MutualLike.filter(query).count()
    kwargs = {
                "text": text,
                "reply_markup": await view_relation_keyboard(count_your_like=count_users_like_you, 
                                                             count_mutal_like=count_mutal_like)
    }
    if isinstance(message, types.CallbackQuery):
        await message.message.delete()
        return await message.message.answer(**kwargs)
    else:
        return await message.answer(**kwargs)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == "your_likes")
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == "offset_your_likes")
async def view_your_likes_handler(call: types.CallbackQuery, last_view_id: int = None):
    user = await models.UserModel.get(tg_id=call.message.chat.id)
    if user.end_premium is None:
        return await call.message.answer("У вас нет активного Gold статуса.", 
                                         reply_markup=await one_button_keyboard(text="Купить Gold статус", 
                                                                                callback="buy:gold:1"))
    users_like_you = await calculation_users(user_id=user.id, like_catalog=True)
    if len(users_like_you) == 0:
        return
    count_your_likes = len(users_like_you)

    offset = int(call.data.split(':')[1])
    if offset >= count_your_likes:
        offset = 0
    if offset < 0:
        offset = count_your_likes - 1
    target_user_row = users_like_you[offset:][0]
    target_user = await models.UserModel.get(id=target_user_row['target_id'])
    user_view = await models.UserView.get_or_create(user=user, target_user=target_user)
    user_view = user_view[0]
    # target_user = await user_view.target_user
    avatar = await target_user.avatar
    if target_user.verification == False or avatar.file_id is None:
        offset += 1
        call.data = f"your_likes:{offset}"
        return await view_your_likes_handler(call)

    text = await generate_ad_text(target_user=target_user, general_percent=target_user_row['general_percent'])

    keyboard = await like_keyboard(callback='y_like_reaction',
                                   view_id=user_view.id, 
                                   superlike_count=user.superlike_count,
                                   offset=offset,
                                   general_percent=target_user_row['general_percent'])

    if call.data.split(':')[0] == 'offset_your_likes':
        await call.message.delete()
    if avatar.file_type.lower() in PHOTO_TYPES:
        await call.message.answer_photo(photo=avatar.file_id, caption=text, reply_markup=keyboard) 
    elif avatar.file_type.lower() in VIDEO_TYPES:
        await call.message.answer_video(video=avatar.file_id, caption=text, reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == "mutal_likes")
async def mutal_likes_handler(call: types.CallbackQuery):
    user = await models.UserModel.get(tg_id=call.message.chat.id)
    offset = int(call.data.split(':')[1])
    query = Q(Q(user=user) | Q(target_user=user)) & Q(Q(user__verification=True) & Q(target_user__verification=True))
    count_mutal_like = await models.MutualLike.filter(query).count()
    if offset >= count_mutal_like:
        offset = 0
    if offset < 0:
        offset = count_mutal_like - 1
    mutal_like = await models.MutualLike.filter(query).order_by('-created_at').offset(offset).limit(1)    
    if len(mutal_like) == 0:
        return 
    print(mutal_like)
    mutal_like = mutal_like[0]
    if mutal_like.target_user_id == user.id:
        target_user = await mutal_like.user
    else:
        target_user = await mutal_like.target_user
    avatar = await target_user.avatar
    relation = await calculation_users(user_id=user.id, target_user_id=target_user.id)
    if len(relation) == 0:
        general_percent = 0
    else:
        general_percent = relation['general_percent']
    text = await generate_ad_text(target_user=target_user, general_percent=general_percent)
    end_text = "\n\nПора познакомиться, пишите: "
    await call.message.delete()
    if target_user.tg_username is None:
        text += "\n\nИзвините аккаунт пользователя скрыт, возможно он напишет вам сам"
    else:
        text += end_text + f"@{target_user.tg_username}"
    if avatar.file_type.lower() in PHOTO_TYPES:
        await call.message.answer_photo(photo=avatar.file_id, caption=text, reply_markup=await mutal_likes_keyboard(offset=offset)) 
    elif avatar.file_type.lower() in VIDEO_TYPES:
        await call.message.answer_video(video=avatar.file_id, caption=text, reply_markup=await mutal_likes_keyboard(offset=offset))