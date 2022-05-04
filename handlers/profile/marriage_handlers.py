from loader import dp
from aiogram import types
from keyboards.inline.user_settings_keyboards import marital_status_keyboard, children_keyboard
from models import models

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'marriage')
async def marriage_handler(call: types.CallbackQuery):
    await call.message.edit_text(text='Ваше семейное положение?', reply_markup=await marital_status_keyboard())




@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'ms')
async def mar_status_handler(call: types.CallbackQuery):
    status = call.data.split(':')[1]
    await call.answer(f"Ваше семейное положение: {status}")
    user = await models.UserModel.get(tg_id=call.message.chat.id)
    user.marital_status = status
    await user.save()
    await call.message.edit_text(text="У вас есть дети? Информация будет использоваться для поиска более подходящих вам знакомств.", 
                                 reply_markup=await children_keyboard())