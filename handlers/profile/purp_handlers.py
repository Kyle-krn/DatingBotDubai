from loader import dp
from models import models
from aiogram import types
from keyboards.inline.user_settings_keyboards import purp_keyboard

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'purp')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'skip_children')
async def purp_handler(call: types.CallbackQuery):
    user = await models.UserModel.get(tg_id=call.message.chat.id)
    if call.data.split(':')[0] == 'purp':
        purp_id = int(call.data.split(':')[1]) 
        purp = await models.PurposeOfDating.get(id=purp_id)
        
        if purp in await user.purp_dating.all():
            await user.purp_dating.remove(purp)
        else:
            await user.purp_dating.add(purp)
    if call.data.split(':')[0] == 'skip_children':
        if call.data.split(':')[1] == 'no':
            user.children = False
            await call.answer("Вы выбрали: Нет детей")
        else:
            user.children = None
            await call.answer("Вы выбрали: Не скажу")
        await user.save()
    await call.message.edit_text('Выберите цели знакомства', reply_markup=await purp_keyboard(await user.purp_dating.all()))


