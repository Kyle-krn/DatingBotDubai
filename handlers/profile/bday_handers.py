from typing import Union
from data.config import KEYBOARD_TEXT
from handlers.cancel_state_handler import redirect_handler
from keyboards.inline.inline_keyboards import one_button_keyboard
from loader import dp
from aiogram import types
from .profile_state import ProfileSettingsState
from aiogram.dispatcher import FSMContext
from keyboards.inline.user_settings_keyboards import skip_settings_keyboard
from datetime import datetime, date
from models import models
from .hobbies_handlers import set_hobbies_state
from .views_self_profile_handlers import profile_handler
from tortoise.queryset import Q

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'bday')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'change_bday')
async def birthday_handler(call: Union[types.CallbackQuery, types.Message]):
    await ProfileSettingsState.bday.set()
    state = dp.get_current().current_state()
    if isinstance(call, types.Message) or call.data.split(':')[0] == 'bday':
        status_user = "new"
        keyboard = None
        if isinstance(call, types.CallbackQuery):
            user = await models.UserModel.get(tg_id=call.message.chat.id)
            interest_place_user = await user.interest_place_companion.all()
            text_place = ", ".join([i.title_interest for i in interest_place_user])
            await call.message.edit_text(text=f"Вы выбрали: {text_place}", reply_markup=None)
        else:
            user = await models.UserModel.get(tg_id=call.chat.id)
    else:
        await call.answer()
        status_user = "old"
        keyboard = await one_button_keyboard(text="Отмена", callback="cancel_state:")
    await state.update_data(status_user=status_user)
    
    if isinstance(call, types.CallbackQuery):
        await call.message.answer("Укажи свою дату рождения в формате DD.MM.YYYY, например 23.05.1996", reply_markup=keyboard)
    else:
        await call.answer("Укажи свою дату рождения в формате DD.MM.YYYY, например 23.05.1996", reply_markup=keyboard)

@dp.message_handler(state=ProfileSettingsState.bday)
async def input_bday_handler(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data['status_user'] == "new":
        keyboard = None
    elif user_data['status_user'] == "old":
        if message.text in KEYBOARD_TEXT:
            await state.finish()
            return await redirect_handler(message=message, button_text=message.text)
        keyboard = await one_button_keyboard(text="Отмена", callback="cancel_state:")
    try:
        bday = datetime.strptime(message.text, '%d.%m.%Y').date()
    except ValueError:
        return await message.answer("<b>Неверный формат!</b>\n\nУкажи свою дату рождения в формате DD.MM.YYYY, например 23.05.1996", reply_markup=keyboard)
    today = date.today()
    age = int((today - bday).total_seconds() / 60 / 60 / 24 / 365)
    print(age)
    if (18 < age < 100) is False:
        if 18 < age:
            info_text = 'Обращаем ваше внимание: использование сервиса запрещено лицам, моложе 18 лет!'
        elif age < 100:
            info_text = ''
        return await message.answer(f"{info_text} Возможно, вы ошиблись! Укажите свою дату рождения в формате DD.MM.YYYY, например 23.07.1996", reply_markup=keyboard)
    
    
    user = await models.UserModel.get(tg_id=message.chat.id)
    user.birthday = bday
    await user.save()
    await state.finish()

    if user_data['status_user'] == 'new':
        return await set_hobbies_state(message)
    else:
        return await profile_handler(message)
    
