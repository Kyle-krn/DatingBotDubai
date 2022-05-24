from data.config import KEYBOARD_TEXT
from handlers.cancel_state_handler import redirect_handler
from loader import dp
from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.inline.user_settings_keyboards import purp_keyboard, children_keyboard
from models import models
from .profile_state import ProfileSettingsState
from .purp_handlers import purp_handler
from tortoise.queryset import Q
from .views_self_profile_handlers import profile_handler


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'change_children')
async def children_handler(call: types.CallbackQuery):
    text = "У вас есть дети? Информация будет использоваться для поиска более подходящих вам знакомств."
    if isinstance(call, types.CallbackQuery) and call.data.split(':')[0] == 'change_children':
        await call.message.delete()
        keyboard = await children_keyboard(prefix_callback="c_")
        return await call.message.answer(text=text, 
                                         reply_markup=keyboard)
    else:
        keyboard = await children_keyboard()
        if isinstance(call, types.CallbackQuery):
            return await call.message.edit_text(text=text, 
                                            reply_markup=keyboard)
        else:
            return await call.edit_text(text=text, 
                                        reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'add_children')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'c_add_children')
async def childrens_age_handler(call: types.CallbackQuery):
    user = await models.UserModel.get(tg_id=call.message.chat.id)
    old_value_children = user.children
    old_value_children_age = user.children_age
    user.children = True
    await user.save()
    await ProfileSettingsState.children.set()
    state = dp.get_current().current_state()
    if call.data.split(':')[0] == "c_add_children":
        status_user = "old"
    else:
        status_user = "new"
    await state.update_data(status_user=status_user, 
                            old_value_children=old_value_children,
                            old_value_children_age=old_value_children_age)
    await call.message.edit_text("Вы выбрали: Есть дети.")
    text = "Сколько лет вашим детям (если не хотите отвечать проставьте 0).\n"  \
            "Укажите количество лет для каждого ребенка через запятую."  \
            "Информация будет использоваться для поиска более подходящих вам знакомств."
    await call.message.answer(text=text)


@dp.message_handler(state=ProfileSettingsState.children)
async def children_state_handler(message: types.Message, state: FSMContext):
    user = await models.UserModel.get(tg_id=message.chat.id)
    user_data = await state.get_data()
    if (message.text.isdigit() and int(message.text) == 0) or (message.text in KEYBOARD_TEXT):
        user.children_age = []
    else:
        
        children_list = [i.strip() for i in message.text.split(',')]
        try:
            children_list = [int(i) for i in children_list if 0 < int(i)]
        except (ValueError, TypeError):
            text = "Сколько лет вашим детям (если не хотите отвечать проставьте 0).\n"  \
               "Укажите количество лет для каждого ребенка через запятую."  \
               "Информация будет использоваться для поиска более подходящих вам знакомств."
            return await message.answer(text=text)
        user.children_age = children_list
        await user.save()
    await state.finish()
    if user_data['status_user'] == 'new':
        return await purp_handler(message, change=False)
    else:
        if message.text in KEYBOARD_TEXT:
            return await redirect_handler(message, message.text)
        else:
            return await profile_handler(message)
        


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'skip_children')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'c_skip_children')
async def skip_children_hanlder(call: types.CallbackQuery):
    user = await models.UserModel.get(tg_id=call.message.chat.id)
    if call.data.split(':')[1] == 'no':
        user.children = False
        user.children_age = []
        await call.message.edit_text(text="Вы выбрали: Нет детей", reply_markup=None)
    else:
        user.children = None
        user.children_age = []
        await call.message.edit_text("Вы выбрали: Не скажу", reply_markup=None)
    await user.save()
    if call.data.split(':')[0] == 'skip_children':
        return await purp_handler(call, change=False)
    else:
        return await profile_handler(call.message)



