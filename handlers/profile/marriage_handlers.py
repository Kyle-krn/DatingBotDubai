from typing import Union
from loader import dp
from aiogram import types
from keyboards.inline.user_settings_keyboards import marital_status_keyboard, children_keyboard
from models import models
from .views_self_profile_handlers import profile_handler

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'marriage')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'change_marriage')
async def marriage_handler(call: Union[types.CallbackQuery, types.Message]):
    if isinstance(call, types.CallbackQuery):
        tg_id = call.message.chat.id
    else:
        tg_id = call.chat.id
    user = await models.UserModel.get(tg_id=tg_id)
    if isinstance(call, types.CallbackQuery) and call.data.split(':')[0] == 'change_marriage':
        keyboard = await marital_status_keyboard(user_marital_status_id=user.marital_status_id, callback="c_ms")
        # await call.message.delete()
        await call.answer()
        await call.message.answer(text='Ваше семейное положение?', reply_markup=keyboard)
    else:
        keyboard = await marital_status_keyboard(user_marital_status_id=user.marital_status_id)
        hobbies = await user.hobbies.all()
        hobbies = [i.title_hobbie for i in hobbies]
        if len(hobbies) == 0:
            text = "Вы не добавили увлечения."
        else:
            text = "Ваши увлечения: " + ", ".join(hobbies)
        if isinstance(call, types.CallbackQuery):
            await call.message.edit_text(text=text, reply_markup=None)
            await call.message.answer(text='Ваше семейное положение?', reply_markup=keyboard)
        else:
            await call.answer(text='Ваше семейное положение?', reply_markup=keyboard)



@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'ms')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'c_ms')
async def mar_status_handler(call: types.CallbackQuery):
    status_id = int(call.data.split(':')[1])
    status = await models.MaritalStatus.get(id=status_id)
    await call.answer(f"Ваше семейное положение: {status.title_status}")
    user = await models.UserModel.get(tg_id=call.message.chat.id)
    user.marital_status = status
    await user.save()
    await call.message.edit_text(text=f"Ваше семейное положение: {status.title_status}")
    if call.data.split(':')[0] == 'ms':
        await call.message.answer(text="У вас есть дети? Информация будет использоваться для поиска более подходящих вам знакомств.", 
                                    reply_markup=await children_keyboard())
    else:
        # await call.message.delete()
        return await profile_handler(call.message)