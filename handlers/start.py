from aiogram.dispatcher.filters.builtin import CommandStart
from models import models
from loader import dp
from keyboards.inline.user_settings_keyboards import gender_keyboard
from aiogram import types
from keyboards.reply_keyboards.keyboards import main_keyboard
@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    user = await models.UserModel.get_or_none(tg_id=message.chat.id)
    # await send_new_registration_in_chanel(user)
    # if user:
    #     await user.delete()
    #     user = None
    if not user:
        user = await models.UserModel.create(tg_id=message.chat.id,
                                      tg_username=message.chat.username,
                                      name=message.chat.full_name)
        await models.UserSearchSettings.create(user=user)
        await models.AvatarModel.create(user=user)
        await message.answer(f"Укажите Ваш пол:", reply_markup=await gender_keyboard())
    elif user and user.end_registration is True:
        return await message.answer("Добро пожаловать!", reply_markup=await main_keyboard())
        