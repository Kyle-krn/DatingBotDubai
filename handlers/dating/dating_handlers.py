import re
from loader import dp, bot
from aiogram import types
from models import models
from datetime import datetime, date
from tortoise.queryset import Q
from keyboards.inline.inline_keyboards import like_keyboard
from utils.zodiak import zodiac_sign
import redis
import json
from handlers.view_relations.views_handlers import view_your_likes_handler
import tortoise
r = redis.Redis()

@dp.message_handler(commands=['dating'])
async def search_dating(message: types.Message, last_view_id: int = None):
    photo_types = ('jpeg', 'jpg', "webm", "png")
    video_types = ("mp4", "avi")

    user = await models.UserModel.get(tg_id=message.chat.id)
    queryset_cache = r.get(str(message.chat.id))
    
    if queryset_cache is None or len(json.loads(queryset_cache)) == 0:
        query = Q(relation__percent_compatibility__gt=0) & Q(target_user__verification=True) & Q(like=False) & Q(superlike=False)
        user_view = user.user_view.filter(query).order_by('dislike', 'count_view', '-relation__percent_compatibility')        #.limit(1)
        if last_view_id:
            user_view = user_view.exclude(id=last_view_id)
        target_users_list = await user_view
        if len(target_users_list) == 0:
            return await message.answer("К сожалению подходящих пар не найдено.")
        user_view = target_users_list.pop(0)
        r.set(str(message.chat.id), json.dumps([v.id for v in target_users_list]), 5*60)
    else:
        queryset_cache = json.loads(queryset_cache)
        try:
            user_view = await models.UserView.get(id = queryset_cache.pop(0))
        except tortoise.exceptions.DoesNotExist:
            pass
        ttl = r.ttl(str(message.chat.id))
        if ttl > 0:
            r.set(str(message.chat.id), json.dumps(queryset_cache), ttl)

    user_view.count_view += 1
    await user_view.save()
    target_user = await user_view.target_user
    avatar = await target_user.avatar
    
    zodiak = await zodiac_sign(target_user.birthday)

    year = datetime.now().year
    text = f"{target_user.name}, {year-target_user.birthday.year}\n"  \
           f"{zodiak}\n" \
           f"🗺️ {target_user.place}\n" \
           f"👫 {target_user.marital_status}\n"  \
           f"Дети: "
    if target_user.children is True:
        text += "Есть\n"
    elif target_user.children is False:
        text += "Нет\n"
    elif target_user.children is None:
        text += "Не скажу\n"
    if target_user.children_age != []:
        text += "Возраст детей: " + ", ".join([str(i)+" г." for i in target_user.children_age]) + "\n"
    target_hobbies = await target_user.hobbies.all()
    if target_hobbies:
        text += "Увлечения: " + ", ".join([i.title_hobbie for i in target_hobbies]) + "\n"
    relation = await user_view.relation
    text += f"Процент совместимости: {relation.percent_compatibility}%"
    
    if avatar.file_type.lower() in photo_types:
        await message.answer_photo(photo=avatar.file_id, caption=text, reply_markup=await like_keyboard(view_id=user_view.id, superlike_count=user.superlike_count)) 
    elif avatar.file_type.lower() in video_types:
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
    if command == "like":
        view.like = True
        if view.like and reverse_view.like:
            await call.message.answer(f"У вас новая пара с @{target_user.tg_username}!")
            await bot.send_message(chat_id=target_user.tg_id, text=f"У вас новая пара с @{user.tg_username}!")
            await models.MutualLike.create(user=user, target_user=target_user)
    elif command == "superlike":
        if user.superlike_count <= 0:
            await call.message.answer("У вас нет суперлайков.")
        else:
            view.like = True
            view.superlike = True
            await bot.send_message(chat_id=target_user.tg_id, text=f"Пользователь @{user.tg_username} отправил вам суперлайк!")
            user.superlike_count -= 1
            await user.save()

    elif command == "dislike":
        view.dislike = True
        await bot.send_message(chat_id=target_user.tg_id, text=f"У вас новая пара с @{user.tg_username}!")
    await view.save()
    await call.message.delete()
    if call.data.split(':')[0] == 'reaction':
        return await search_dating(call.message, last_view_id=view_id)
    else:
        return await view_your_likes_handler(call, last_view_id=view_id)
