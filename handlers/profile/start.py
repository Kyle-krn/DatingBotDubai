from datetime import datetime
from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from models.models import UserModel
from loader import dp
from keyboards.inline.user_settings_keyboards import gender_keyboard
from handlers.group.new_reg_user_handlers import send_new_registration_in_chanel, calculation_new_user
from handlers.calculation_relations.relations_handlers import check_settings_gender, check_age



@dp.message_handler(commands=['user'])
async def test_group(message: types.Message):

    for user in await UserModel.all():
        await send_new_registration_in_chanel(user)


@dp.message_handler(commands=['test'])
async def test_group(message: types.Message):
    await message.answer(text='<a href="tg://resolve?domain=examplebot&startgroup=true">Telegram</a>')
