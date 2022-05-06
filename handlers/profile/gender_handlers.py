from .profile_state import ProfileSettingsState
from loader import dp
from aiogram import types
from models import models
from keyboards.reply_keyboards.keyboards import geolocation_keyboard
from .city_handlers import city_set_state_handler

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'gender')
async def gender_handler(call: types.CallbackQuery):
    try:
        user = await models.UserModel.get(tg_id=call.message.chat.id)
    except Exception:
        print("Пошел нахуй отправлено")
        print(call.message.chat.id)
        print(call.message.chat.username)
        await call.message.answer("Иди нахуй, хватит трогать тестового бота.")
    gender = call.data.split(':')[1]
    if gender == 'male':
        user.male = True
        await call.answer("Вы выбрали: Мужчина")
    else:
        user.male = False
        await call.answer("Вы выбрали: Женщина")
    await user.save()
    await city_set_state_handler(call)
    # await call.message.delete()
    # await ProfileSettingsState.city.set()
    # await call.message.answer(text="Введите ваш город", reply_markup=await geolocation_keyboard())