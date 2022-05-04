from loader import dp
from models import models
from aiogram import types
from keyboards.inline.user_settings_keyboards import companion_dubai_keyboard

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'remove_dubai')
async def remove_dubai_handler(call: types.CallbackQuery):
    user = await models.UserModel.get(tg_id=call.message.chat.id)
    answer = call.data.split(':')[1]
    if answer == 'yes':
        user.moving_to_dubai = True
        await call.answer("Планируете переезд в Дубаи")
    elif answer == 'no':
        user.moving_to_dubai = False
        await call.answer("Не планируете переезд в Дубаи")
    await user.save()
    await call.message.edit_text("Укажите с кем вы заинтересованы в знакомствах?", reply_markup=await companion_dubai_keyboard(user))


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'companion_dubai')
async def add_companion_dubai_interest(call: types.CallbackQuery):
    user = await models.UserModel.get(tg_id=call.message.chat.id)
    user_interest = await user.interest_place_companion.all()
    interest_id = call.data.split(':')[1]
    selected_interest = await models.DatingInterestPlace.get(id=interest_id)
    if selected_interest in user_interest:
        await user.interest_place_companion.remove(selected_interest)
    else:
        await user.interest_place_companion.add(selected_interest)
    await call.message.edit_text("Укажите с кем вы заинтересованы в знакомствах?", reply_markup=await companion_dubai_keyboard(user))

