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
    user = await UserModel.get_or_none(id=123)
    settings = await user.search_settings

    tar_user = await UserModel.get_or_none(id=128)
    tar_settings = await tar_user.search_settings
    year_now = datetime.now().year
    old_user = year_now - user.birthday.year

    old_tar = year_now - tar_user.birthday.year
    x = await check_age(old_user=old_user, user=user, target_user=tar_user)
    x = await check_age(old_user=old_tar, user=tar_user, target_user=user)
