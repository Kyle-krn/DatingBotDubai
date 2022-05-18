from ctypes import Union
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

from utils.zodiak import zodiac_sign
from models.row_user_likes import rowsql_likes
redis_cash_2 = redis.Redis(db=2)

@dp.message_handler(commands=['likes'])
@dp.message_handler(regexp="^(💑 Симпатии)$")
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'back_likes')
async def view_relations_handler(message: types.Message):
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
        return await message.answer("Ваш профиль еще не верифицирован.")
    query = Q(Q(user=user) | Q(target_user=user)) & Q(Q(user__verification=True) & Q(target_user__verification=True))
    count_mutal_like = await models.MutualLike.filter(query).count()
    your_likes = await rowsql_likes(user.id)
    # print(x)
    if isinstance(message, types.CallbackQuery):
        await message.message.delete()
        return await message.message.answer(text, reply_markup=await view_relation_keyboard(count_your_like=len(your_likes), count_mutal_like=count_mutal_like))
    else:
        return await message.answer(text, reply_markup=await view_relation_keyboard(count_your_like=len(your_likes), count_mutal_like=count_mutal_like))


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == "your_likes")
async def view_your_likes_handler(call: types.CallbackQuery, last_view_id: int = None):
    user = await models.UserModel.get(tg_id=call.message.chat.id)
    if user.end_premium is None:
        return await call.message.answer("У вас нет активного Gold статуса.", 
                                         reply_markup=await one_button_keyboard(text="Купить Gold статус", 
                                                                                callback="buy:gold:1"))
    queryset_cache = redis_cash_2.get(str(call.message.chat.id))
    if queryset_cache is None or len(json.loads(queryset_cache)) == 0:
        your_likes = [i['id'] for i in await rowsql_likes(user.id)]
        if len(your_likes) == 0:
            return await call.message.answer("Нет новых лайков.")
        user_view = await models.UserView.get(id=your_likes.pop(0))
        # user_view: models.UserView = user_views.pop(0)
        redis_cash_2.set(str(call.message.chat.id), json.dumps(your_likes), 5*60)
    else:
        queryset_cache: List[models.UserView.id] = json.loads(queryset_cache)
        user_view = await models.UserView.get(id = queryset_cache.pop(0))
        ttl = redis_cash_2.ttl(str(call.message.chat.id))
        if ttl > 0:
                redis_cash_2.set(str(call.message.chat.id), json.dumps(queryset_cache), ttl)
    await user_view.save()
    await call.message.delete()
    target_user = await user_view.target_user
    avatar = await target_user.avatar
    if target_user.verification == False or avatar.file_id is None:
        return await view_your_likes_handler(call)
    text = await generate_ad_text(target_user=target_user, relation=await user_view.relation)

    if avatar.file_type.lower() in PHOTO_TYPES:
        await call.message.answer_photo(photo=avatar.file_id, caption=text, reply_markup=await like_keyboard(callback='y_like_reaction', view_id=user_view.id, superlike_count=user.superlike_count)) 
    elif avatar.file_type.lower() in VIDEO_TYPES:
        await call.message.answer_video(video=avatar.file_id, caption=text, reply_markup=await like_keyboard(callback='y_like_reaction', view_id=user_view.id, superlike_count=user.superlike_count))


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == "mutal_likes")
async def mutal_likes_handler(call: types.CallbackQuery):
    user = await models.UserModel.get(tg_id=call.message.chat.id)
    offset = int(call.data.split(':')[1])
    query = Q(Q(user=user) | Q(target_user=user)) & Q(Q(user__verification=True) & Q(target_user__verification=True))
    count_mutal_like = await models.MutualLike.filter(query).count()
    print(count_mutal_like)
    if offset >= count_mutal_like:
        offset = 0
    if offset < 0:
        offset = count_mutal_like - 1
    mutal_like = await models.MutualLike.filter(query).order_by('-created_at').offset(offset).limit(1)    
    if len(mutal_like) == 0:
        return await call.answer("У вас нет взаимных лайков.")
    mutal_like = mutal_like[0]
    if mutal_like.target_user_id == user.id:
        target_user = await mutal_like.user
    else:
        target_user = await mutal_like.target_user
    avatar = await target_user.avatar
    relation = await models.UsersRelations.get_or_none(Q(user=user) & Q(target_user=target_user))
    if not relation:
        relation = await models.UsersRelations.get_or_none(Q(target_user=user) & Q(user=target_user))

    text = await generate_ad_text(target_user=target_user, relation=await relation)
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





    # avatar = await target_user.avatar
    
    # zodiak = await zodiac_sign(target_user.birthday)

    # year = datetime.now().year
    # text = f"{target_user.name}, {year-target_user.birthday.year}\n"  \
    #        f"@{target_user.tg_username}\n"  \
    #        f"{zodiak}\n" \
    #        f"🗺️ {target_user.place}\n" \
    #        f"👫 {target_user.marital_status}\n"  \
    #        f"Дети: "
    # if target_user.children is True:
    #     text += "Есть\n"
    # elif target_user.children is False:
    #     text += "Нет\n"
    # elif target_user.children is None:
    #     text += "Не скажу\n"
    # if target_user.children_age != []:
    #     text += "Возраст детей: " + ", ".join([str(i)+" г." for i in target_user.children_age]) + "\n"
    # target_hobbies = await target_user.hobbies.all()
    # if target_hobbies:
    #     text += "Увлечения: " + ", ".join([i.title_hobbie for i in target_hobbies]) + "\n"

    # relation = await models.UsersRelations.get_or_none(Q(user=user) & Q(target_user=target_user))
    # if not relation:
    #     relation = await models.UsersRelations.get_or_none(Q(target_user=user) & Q(user=target_user))

    # text += f"Процент совместимости: {relation.percent_compatibility}%"

    # # photo_types = ('jpeg', 'jpg', "webm", "png")
    # # video_types = ("mp4", "avi")
    # await call.message.delete()
    # if avatar.file_type.lower() in PHOTO_TYPES:
    #     await call.message.answer_photo(photo=avatar.file_id, caption=text, reply_markup=await mutal_likes_keyboard(offset=offset)) 
    # elif avatar.file_type.lower() in VIDEO_TYPES:
    #     await call.message.answer_video(video=avatar.file_id, caption=text, reply_markup=await mutal_likes_keyboard(offset=offset))

