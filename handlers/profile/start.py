from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from models.models import UserModel
from loader import dp
from keyboards.inline.user_settings_keyboards import gender_keyboard
from handlers.group.new_reg_user_handlers import send_new_registration_in_chanel




@dp.message_handler(commands=['user'])
async def test_group(message: types.Message):
    # user = await UserModel.get_or_none(id=49)
    # user = await UserModel.get_or_none(id=58)
    for user in await UserModel.all():
        await send_new_registration_in_chanel(user)


@dp.message_handler(commands=['test'])
async def test_group(message: types.Message):
    user = await UserModel.get_or_none(id=44)
    print(await user.user_view.filter(relation__percent_compatibility__gt=0))
    # user = await UserModel.get_or_none(id=58)
    # for user in await UserModel.all():
    #     await send_new_registration_in_chanel(user)

@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    user = await UserModel.get_or_none(tg_id=message.chat.id)
    # await send_new_registration_in_chanel(user)
    if user:
        await user.delete()
        user = None
    if not user:
        user = await UserModel.create(tg_id=message.chat.id,
                                      tg_username=message.chat.username,
                                      name=message.chat.full_name)
        await message.answer(f"Укажите Ваш пол:", reply_markup=await gender_keyboard())
