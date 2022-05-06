from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from models.models import UserModel
from loader import dp
from keyboards.inline.user_settings_keyboards import gender_keyboard
from handlers.group.new_reg_user_handlers import send_new_registration_in_chanel, calculation_new_user
from handlers.calculation_relations.relations_handlers import check_settings_gender



@dp.message_handler(commands=['user'])
async def test_group(message: types.Message):

    for user in await UserModel.all():
        await send_new_registration_in_chanel(user)


@dp.message_handler(commands=['test'])
async def test_group(message: types.Message):
    user = await UserModel.get_or_none(id=123)
    settings = await user.search_settings

    tar_user = await UserModel.get_or_none(id=127)
    tar_settings = await user.search_settings
    
    print(f"{user}: {user.male} -> {settings.male}")
    print(f"{tar_user}: {tar_user.male} -> {tar_settings.male}")
    x = await check_settings_gender(user, tar_user)
    print(x)
    x = await check_settings_gender(tar_user, user)
    print(x)
