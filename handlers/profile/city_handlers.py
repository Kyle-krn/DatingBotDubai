from cProfile import Profile
from typing import Union
from models import models
from aiogram import types
from aiogram.dispatcher import FSMContext
from utils.utils_map import get_location_by_city, get_location_by_lat_long
from loader import dp
from keyboards.inline.user_settings_keyboards import city_answer_keyboard, dubai_answer_keyboard, companion_dubai_keyboard
from keyboards.reply_keyboards.keyboards import geolocation_keyboard, main_keyboard
from .profile_state import ProfileSettingsState
from .dubai_handlers import dubai_handler 
from .views_self_profile_handlers import profile_handler


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == "change_place")
async def city_set_state_handler(call: Union[types.CallbackQuery, types.Message]):
    # await call.message.delete()
    await ProfileSettingsState.city.set()
    state = dp.get_current().current_state()
    if isinstance(call, types.CallbackQuery):
        if call.data.split(':')[0] == "change_place":
            status_user = "old"
            await call.answer()
        else:
            status_user = "new"
    else:
        status_user = "new"
    await state.update_data(status_user=status_user)
    if isinstance(call, types.CallbackQuery):
        await call.message.answer(text="Введите ваш город", reply_markup=await geolocation_keyboard(status_user=status_user))
    else:
        await call.answer(text="Введите ваш город", reply_markup=await geolocation_keyboard(status_user=status_user))

# async def city_set_state_handler_message(message: types.Message):


@dp.message_handler(lambda message: message.text == '🛑 Отмена', state=ProfileSettingsState.city)
async def city_cancel_state_handler(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer("Город не изменен.", reply_markup=await main_keyboard())
    await state.finish()
    return await profile_handler(message)



@dp.message_handler(state=ProfileSettingsState.city)
async def city_handler(message: types.Message, state: FSMContext):
    city = message.text
    msg = await message.answer("Ищем ваш город 🔍")
    city_info, geolocation, tmz= await get_location_by_city(city)
    if not city_info:
        await msg.edit_text("Такой город не найден, попробуйте снова или отправьте геолокацию по кнопке ниже.")
    else:
        state = dp.get_current().current_state()
        await state.update_data(city_info=city_info, geolocation=geolocation, tmz=tmz)
        await msg.edit_text(f"Ваш город {city_info}?", reply_markup=await city_answer_keyboard())



@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'city', state=ProfileSettingsState.city)
async def answer_city_handler(call: types.CallbackQuery, state: FSMContext):
    answer = call.data.split(':')[1]
    if answer == 'yes':
        user_data = await state.get_data()
        city = await models.City.get_or_create(place_name=user_data['city_info'])
        city = city[0]
        # if city.tmz is not None:
        if city.tmz != user_data['tmz']:
            city.tmz = user_data['tmz']
            await city.save()
        
        user = await models.UserModel.get(tg_id=call.message.chat.id)
        user.place = city
        await user.save()
        await call.message.edit_text(text=f"Ваш город: {user.place.place_name}", reply_markup=None)
        await user.save()
        await state.finish()
        # await call.message.delete()
        msg = await call.message.answer("Загрузка ⏳", reply_markup=types.ReplyKeyboardRemove())
        await msg.delete()
        
        old_value = user.dubai
        if not 'Dubai' in city.place_name:
            user.dubai = False
            # user.moving_to_dubai = False
        else:
            user.dubai = True
            user.moving_to_dubai = None
        await user.save()
        if user_data['status_user'] == 'old':
            
            await call.message.answer(text='Успешно!', reply_markup=await main_keyboard())
            await user.save()
            # if old_value != user.dubai:
            #     await recalculation_location(user)
            return await profile_handler(call.message)
        if user_data['status_user'] == 'new':
            if user.dubai is False:
                return await dubai_handler(call.message)
            else:
                return await call.message.answer("Укажите с кем вы заинтересованы в знакомствах? (можно выбрать несколько вариантов)", reply_markup=await companion_dubai_keyboard(user))
    elif answer == 'no':
        await call.message.edit_text(text="Попробуйте снова", reply_markup=None)



@dp.message_handler(content_types=['location'], state=ProfileSettingsState.city)
async def geolocation_handler(message: types.Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude
    city_info, geolocation, tmz = await get_location_by_lat_long(lat=lat, long=lon)
    if not city_info:
        return await message.answer("К сожалению мы не смогли определить ваш город, напиши его текстом.")
    city = await models.City.get_or_create(place_name=city_info)
    city = city[0]
    if city.tmz != tmz:
        city.tmz = tmz
        await city.save()
    user = await models.UserModel.get(tg_id=message.chat.id)
    user.place = city
    await user.save()
    user_data = await state.get_data()
    await state.finish()
    msg = await message.answer("Загрузка ⏳", reply_markup=types.ReplyKeyboardRemove())
    await msg.delete()
    if not 'Dubai' in user.place:
        user.dubai = False
    else:
        user.dubai = True

    await user.save()
    
    if user_data['status_user'] == 'old':
        await message.answer(text='Успешно!', reply_markup=await main_keyboard())
        return await profile_handler(message)

    if user_data['status_user'] == 'new':
        if user.dubai is False:
            return await dubai_handler(message)
        else:
            return await message.answer("Укажите с кем вы заинтересованы в знакомствах? (можно выбрать несколько вариантов)", reply_markup=await companion_dubai_keyboard(user))
    
