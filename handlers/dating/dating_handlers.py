from data.config import PHOTO_TYPES, VIDEO_TYPES
from loader import dp, bot
from aiogram import types
from models import models
from keyboards.inline.inline_keyboards import like_keyboard, one_button_keyboard
from utils.text_for_ad import generate_ad_text
import redis
import json
from handlers.view_relations.views_handlers import view_your_likes_handler
from aiogram.utils.exceptions import BotBlocked
from models.db_query import calculation_users


redis_cash_1 = redis.Redis(db=1)


@dp.message_handler(commands=['dating'])
@dp.message_handler(regexp="^(👥 Найти пару)$")
async def search_dating(message: types.Message, last_user_id: int = None):
    user = await models.UserModel.get(tg_id=message.chat.id)
    if user.end_registration is False:
        return await message.answer("Вы не закончили регистрацию")

    queryset_cache = redis_cash_1.get(str(message.chat.id))
    if queryset_cache is None or len(json.loads(queryset_cache)) == 0:
        msg = await message.answer("⌛ <b>Идет загрузка, это может занять какое то время</b>")
        target_ids = await calculation_users(user_id=user.id)
        target_ids = [i for i in target_ids if i['target_id'] != last_user_id]
        await msg.delete()
        if len(target_ids) == 0:
            return await message.answer("К сожалению подходящих пар не найдено.")
        now_target = target_ids.pop(0)
        target_user = await models.UserModel.get(id=now_target['target_id'])
        user_view = await models.UserView.get_or_create(user=user, target_user=target_user)
        if len(target_ids) > 0:
            redis_cash_1.set(str(message.chat.id), json.dumps(target_ids), 10*60)
    else:
        target_ids = json.loads(queryset_cache)
        now_target = target_ids.pop(0)
        
        ttl = redis_cash_1.ttl(str(message.chat.id))
        redis_cash_1.set(str(message.chat.id), json.dumps(target_ids), ttl)
        now_target = await calculation_users(user_id=user.id, target_user_id=now_target['target_id'])
        if len(now_target) == 0:
            return await search_dating(message)
        now_target = now_target[0]
        target_user = await models.UserModel.get(id=now_target['target_id'])
        user_view = await models.UserView.get_or_create(user=user, target_user=target_user)

    target_avatar = await target_user.avatar
    if target_avatar.file_type is None or target_avatar.file_id is None:
        return await search_dating(message, last_user_id=target_user.id)
    user_view = user_view[0]
    user_view.count_view += 1
    await user_view.save()
    text = await generate_ad_text(target_user=target_user, general_percent=now_target['general_percent'])
    if target_avatar.file_type.lower() in PHOTO_TYPES:
        await message.answer_photo(photo=target_avatar.file_id, caption=text, reply_markup=await like_keyboard(view_id=user_view.id, 
                                                                                                               superlike_count=user.superlike_count,
                                                                                                               general_percent=now_target['general_percent'])) 
    elif target_avatar.file_type.lower() in VIDEO_TYPES:
        await message.answer_video(video=target_avatar.file_id, caption=text, reply_markup=await like_keyboard(view_id=user_view.id, 
                                                                                                               superlike_count=user.superlike_count,
                                                                                                               general_percent=now_target['general_percent']))
    


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'reaction')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'y_like_reaction')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'single_reaction')
async def reaction_ad_handler(call: types.CallbackQuery):
    command = call.data.split(':')[1]
    view_id = call.data.split(':')[2]
    general_percent = int(call.data.split(':')[4])
    if call.data.split(':')[0] == 'y_like_reaction':
        offset = int(call.data.split(':')[3])
    view = await models.UserView.get(id=view_id)
    user = await view.user
    avatar_user = await user.avatar
    if avatar_user.file_id is None:
        return await call.message.answer("Чтобы начать знакомиться добавьте ваше фото!", reply_markup=await one_button_keyboard(text="Добавить фото", 
                                                                                                                                callback="change_ava:"))
    elif user.verification is False:
        return await call.message.answer("Мы проверяем ваше фото, когда проверка закончится мы Вам сообщим и вы сможете начать знакомиться!")
    
    target_user = await view.target_user
    reverse_view = await models.UserView.get_or_none(user=target_user, target_user=user)
    if view.like or view.superlike:
        await call.message.delete()
        return await call.answer("Вы уже реагировали на данное объявление.")        
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
        if view.like and reverse_view is not None and reverse_view.like is True:
            await call.message.delete()
            await view.save()
            return await mutal_like_func(message=call.message,
                                         user=user,
                                         target_user=target_user,
                                         general_percent=general_percent)
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
            if view.like and reverse_view is not None and reverse_view.like is True:
                await call.message.delete()
                await view.save()
                return await mutal_like_func(message = call.message,
                                             user=user,
                                             target_user=target_user,
                                             general_percent=general_percent)

            start_text_msg = f"Пользователь {user.name} отправил вам суперлайк!\n\n"
            end_text_msg = f"\n\nХотите с ним познакомиться? Пишите: @{user.tg_username}"
            if user.tg_username is None:
                end_text_msg = "\n\nИзвините аккаунт пользователя скрыт, возможно он напишет вам сам"
                await null_tg_username_answer(chat_id=user.tg_id)
           
            text_msg = start_text_msg + await generate_ad_text(target_user=target_user, general_percent=general_percent) + end_text_msg
            avatar_tar = await target_user.avatar
            
            if not reverse_view:
                reverse_view = await models.UserView.create(user=target_user, target_user=user)
            keyboard = await like_keyboard(view_id=reverse_view.id, superlike_count=target_user.superlike_count, callback="single_reaction", general_percent=general_percent)
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
        if view.superlike is True:
            await call.message.answer(f"{target_user.name} получил ваш контакт!")
        if call.data.split(':')[0] == 'reaction':
            return await search_dating(call.message, last_user_id=target_user.id)
        else:
            call.data = f"your_likes:{offset+1}"
            return await view_your_likes_handler(call, last_user_id=target_user.id)
        # else:
            # return await call.message.answer(f"{target_user.name} получил ваш контакт!")
            



async def mutal_like_func(message: types.Message, 
                          user: models.UserModel,
                          target_user: models.UserModel,
                          general_percent: int):
    avatar_user = await user.avatar
    avatar_tar = await target_user.avatar
    start_text = "У вас новая пара!\n\n"
    end_text = "\n\nПора познакомиться, пишите: "
    
    text = start_text + await generate_ad_text(target_user=target_user, general_percent=general_percent)
    
    if target_user.tg_username is None:
        text += "\n\nИзвините аккаунт пользователя скрыт, возможно он напишет вам сам"
        await null_tg_username_answer(chat_id=target_user.tg_id)
    else:
        text += end_text + f"@{target_user.tg_username}"
    if avatar_tar.file_type.lower() in PHOTO_TYPES:
        await message.answer_photo(photo=avatar_tar.file_id, caption=text) 
    elif avatar_tar.file_type.lower() in VIDEO_TYPES:
        await message.answer_video(video=avatar_tar.file_id, caption=text)

    text = start_text + await generate_ad_text(target_user=user, general_percent=general_percent)
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