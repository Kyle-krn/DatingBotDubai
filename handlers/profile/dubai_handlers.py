from typing import Union
from handlers.search_settings.view_settings_handler import settings_handler
from loader import dp
from models import models
from aiogram import types
from keyboards.inline.user_settings_keyboards import companion_dubai_keyboard, dubai_answer_keyboard
from .views_self_profile_handlers import profile_handler
from tortoise.queryset import Q

# @dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'remove_dubai')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'change_remove_dubai')
async def dubai_handler(call: Union[types.CallbackQuery, types.Message]):
    if isinstance(call, types.Message):
        return await call.answer("Планируете переезд в Дубаи?", reply_markup=await dubai_answer_keyboard())
    else:
        # await call.message.delete()
        await call.answer()
        user = await models.UserModel.get(tg_id=call.message.chat.id)
        return await call.message.answer(text = "Планируете переезд в Дубаи?", 
                                         reply_markup=await dubai_answer_keyboard(remove_in_dubai=user.moving_to_dubai, 
                                                                                  callback="c_remove_dubai"))

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'remove_dubai')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'c_remove_dubai')
async def remove_dubai_handler(call: types.CallbackQuery):
    user = await models.UserModel.get(tg_id=call.message.chat.id)
    old_value = user.moving_to_dubai
    answer = call.data.split(':')[1]
    if answer == 'yes':
        user.moving_to_dubai = True
        await call.message.edit_text(text="Вы выбрали: Планирую переезд в Дубаи", reply_markup=None)
    elif answer == 'no':
        user.moving_to_dubai = False
        await call.message.edit_text(text="Вы выбрали: Не планирую переезд в Дубаи", reply_markup=None)
        # await call.answer("Не планируете переезд в Дубаи")
    await user.save()
    if call.data.split(":")[0] == "remove_dubai":
        return await settings_companion_place_hanlder(call)
    else:
        # await call.message.delete()
        return await profile_handler(call.message)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'settings_companion_dubai')
async def settings_companion_place_hanlder(call: types.CallbackQuery):
    prefix = ''
    if isinstance(call, types.CallbackQuery):
        user = await models.UserModel.get(tg_id=call.message.chat.id)
        if call.data.split(':')[0] == 'settings_companion_dubai':
            prefix = "c_"
            await call.answer()
        return await call.message.answer("Укажите с кем вы заинтересованы в знакомствах? (можно выбрать несколько вариантов)", reply_markup=await companion_dubai_keyboard(user, prefix))
    else:
        user = await models.UserModel.get(tg_id=call.chat.id)
        return await call.answer("Укажите с кем вы заинтересованы в знакомствах? (можно выбрать несколько вариантов)", reply_markup=await companion_dubai_keyboard(user, prefix))

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'companion_dubai')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'c_companion_dubai')
async def add_companion_dubai_interest(call: types.CallbackQuery):
    user = await models.UserModel.get(tg_id=call.message.chat.id)
    user_interest = await user.interest_place_companion.all()
    interest_id = call.data.split(':')[1]
    selected_interest = await models.DatingInterestPlace.get(id=interest_id)
    if selected_interest in user_interest:
        await user.interest_place_companion.remove(selected_interest)
    else:
        await user.interest_place_companion.add(selected_interest)
    prefix = '' if call.data.split(':')[0] == 'companion_dubai' else 'c_'
    await call.message.edit_text("Укажите с кем вы заинтересованы в знакомствах? (можно выбрать несколько вариантов)", reply_markup=await companion_dubai_keyboard(user, prefix))


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'back_settings')
async def back_settings_handler(call: types.CallbackQuery):
    # await call.message.delete()
    user = await models.UserModel.get(tg_id=call.message.chat.id)
    interest_place_user = await user.interest_place_companion.all()
    text_place = ", ".join([i.title_interest for i in interest_place_user])
    await call.message.edit_text(text=f"Вы выбрали: {text_place}", reply_markup=None)
    return await settings_handler(call.message)