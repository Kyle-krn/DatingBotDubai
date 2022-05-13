from loader import dp
from models import models
from aiogram import types
from keyboards.inline.user_settings_keyboards import purp_keyboard
from handlers.calculation_relations.recalculation_relations import recalculation_purp
from tortoise.queryset import Q
from .views_self_profile_handlers import profile_handler
from aiogram import exceptions

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'change_purp')
async def purp_handler(call: types.CallbackQuery, change: bool = None):
    if isinstance(call, types.Message):
        user = await models.UserModel.get(tg_id=call.chat.id)
    else:
        await call.answer()
        user = await models.UserModel.get(tg_id=call.message.chat.id)
    text = 'Выберите цели знакомства'
    callback_for_next = 'send_ava'
    callback_for_purp = "purp"
    if change is False:
        pass
    elif change is True or call.data.split(':')[0] == 'change_purp':
        callback_for_next = "change_purp_quit"
        callback_for_purp = "change_val_purp"
    keyboard = await purp_keyboard(user_purp=await user.purp_dating.all(), 
                                   callback_for_purp=callback_for_purp, 
                                   callback_for_next=callback_for_next)
    if isinstance(call, types.Message):
        return await call.answer(text, reply_markup=keyboard)
    return await call.message.answer(text, reply_markup=keyboard)



@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'purp')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'change_val_purp')
async def change_purp_handler(call: types.CallbackQuery):
    user = await models.UserModel.get(tg_id=call.message.chat.id)
    purp_id = int(call.data.split(':')[1]) 
    purp = await models.PurposeOfDating.get(id=purp_id)
    if purp in await user.purp_dating.all():
        await user.purp_dating.remove(purp)
    else:
        await user.purp_dating.add(purp)
    change = False
    if call.data.split(':')[0] == "change_val_purp":
        change = True
    try:
        await call.message.delete()
    except exceptions.MessageToDeleteNotFound:
        pass
    return await purp_handler(call, change)



@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'change_purp_quit')
async def change_purp_quit_handler(call: types.CallbackQuery):
    user = await models.UserModel.get(tg_id=call.message.chat.id)
    await recalculation_purp(user)
    user_purp = await user.purp_dating.all()
    user_purp = [i.title_purp for i in user_purp]
    user_purp = ", ".join(user_purp)
    await call.message.edit_text(text=f"Ваши цели знакомства: {user_purp}")
    # await call.message.delete()
    return await profile_handler(call.message)



