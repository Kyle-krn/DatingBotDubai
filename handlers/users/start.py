from fcntl import FD_CLOEXEC
from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from models.models import UserModel
from loader import dp
from keyboards.inline.user_settings_keyboards import gender_keyboard
from keyboards.reply_keyboards.keyboards import geolocation_keyboard


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    user = await UserModel.get_or_none(tg_id=message.chat.id)
    if user:
        await user.delete()
        user = None

    if not user:
        user = await UserModel.create(tg_id=message.chat.id,
                                      tg_username=message.chat.username)
        # await Profile.create(user=user)
        await message.answer(f"Укажите Ваш пол:", reply_markup=await gender_keyboard())


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'gender')
async def gender_handler(call: types.CallbackQuery):
    user = await UserModel.get(tg_id=call.message.chat.id)
    gender = call.data.split(':')[1]
    if gender == 'male':
        user.male = True
    else:
        user.male = False
    await user.save()
    await call.message.delete()
    await call.message.answer(text="Введите ваш город", reply_markup=await geolocation_keyboard())
