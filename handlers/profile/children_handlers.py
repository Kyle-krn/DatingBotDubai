from loader import dp
from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.inline.user_settings_keyboards import purp_keyboard
from models import models
from .profile_state import ProfileSettingsState


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'children')
async def children_handler(call: types.CallbackQuery):
    answer = call.data.split(':')[1]
    user = await models.UserModel.get(tg_id=call.message.chat.id)
    user.children = True
    await user.save()
    await ProfileSettingsState.children.set()
    text = "Сколько лет вашим детям (если не хотите отвечать проставьте 0).\n"  \
            "Укажите количество лет для каждого ребенка через запятую."  \
            "Информация будет использоваться для поиска более подходящих вам знакомств."
    await call.message.edit_text(text=text)


@dp.message_handler(state=ProfileSettingsState.children)
async def children_state_handler(message: types.Message, state: FSMContext):
    user = await models.UserModel.get(tg_id=message.chat.id)
    if message.text.isdigit() and int(message.text) == 0:
        pass
    else:
        children_list = [i.strip() for i in message.text.split(',')]
        
        try:
            children_list = [int(i) for i in children_list]
        except (ValueError, TypeError):
            text = "Сколько лет вашим детям (если не хотите отвечать проставьте 0).\n"  \
               "Укажите количество лет для каждого ребенка через запятую."  \
               "Информация будет использоваться для поиска более подходящих вам знакомств."
            return await message.answer(text=text)
        
        
        user.children_age = children_list
        await user.save()
    await state.finish()
    await message.answer('Выберите цели знакомства', reply_markup=await purp_keyboard(await user.purp_dating.all()))

