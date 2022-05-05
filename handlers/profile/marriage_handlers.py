from loader import dp
from aiogram import types
from keyboards.inline.user_settings_keyboards import marital_status_keyboard, children_keyboard
from models import models
from .views_self_profile_handlers import profile_handler

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'marriage')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'change_marriage')
async def marriage_handler(call: types.CallbackQuery):
    user = await models.UserModel.get(tg_id=call.message.chat.id)
    martial_status = user.marital_status
    if not user.marital_status:
        martial_status = ''
    if call.data.split(':')[0] == 'change_marriage':
        keyboard = await marital_status_keyboard(user_martial_status=martial_status, callback="c_ms")
    else:
        keyboard = await marital_status_keyboard(user_martial_status=martial_status)
    
    if call.data.split(':')[0] == 'change_marriage':
        await call.message.delete()
        await call.message.answer(text='Ваше семейное положение?', reply_markup=keyboard)
    else:
        await call.message.edit_text(text='Ваше семейное положение?', reply_markup=keyboard)




@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'ms')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'c_ms')
async def mar_status_handler(call: types.CallbackQuery):
    status = call.data.split(':')[1]
    await call.answer(f"Ваше семейное положение: {status}")
    user = await models.UserModel.get(tg_id=call.message.chat.id)
    user.marital_status = status
    await user.save()
    if call.data.split(':')[0] == 'ms':
        await call.message.edit_text(text="У вас есть дети? Информация будет использоваться для поиска более подходящих вам знакомств.", 
                                    reply_markup=await children_keyboard())
    else:
        await call.message  .delete()
        return await profile_handler(call.message)