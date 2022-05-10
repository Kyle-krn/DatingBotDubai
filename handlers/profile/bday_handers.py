from handlers.calculation_relations.relations_handlers import check_age
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
from handlers.calculation_relations.recalculation_relations import recalculation_int
from tortoise.queryset import Q

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'bday')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'change_bday')
async def birthday_handler(call: types.CallbackQuery):
    await ProfileSettingsState.bday.set()
    state = dp.get_current().current_state()
    if call.data.split(':')[0] == 'bday':
        status_user = "new"
        keyboard = None
    else:
        status_user = "old"
        keyboard = await one_button_keyboard(text="Отмена", callback="cancel_state:")
    await state.update_data(status_user=status_user)
    await call.message.delete()
    await call.message.answer("Укажи свою дату рождения в формате DD.MM.YYYY, например 23.05.1996", reply_markup=keyboard)


@dp.message_handler(state=ProfileSettingsState.bday)
async def input_bday_handler(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data['status_user'] == "new":
        keyboard = None
    elif user_data['status_user'] == "old":
        keyboard = await one_button_keyboard(text="Отмена", callback="cancel_state:")
    try:
        bday = datetime.strptime(message.text, '%d.%m.%Y').date()
    except ValueError:
        return await message.answer("<b>Не верный формат!</b>\n\nУкажи свою дату рождения в формате DD.MM.YYYY, например 23.05.1996", reply_markup=keyboard)
    today = date.today()
    age = int((today - bday).total_seconds() / 60 / 60 / 24 / 365)
    if (18 < age < 100) is False:
        return await message.answer("Обращаем ваше внимание: использование сервиса Zodier запрещено лицам, моложе 18 лет! Возможно, вы ошиблись! Укажите свою дату рождения в формате DD.MM.YYYY, например 23.07.1996", reply_markup=keyboard)
    
    
    user = await models.UserModel.get(tg_id=message.chat.id)
    

    old_age = int((today - user.birthday).total_seconds() / 60 / 60 / 24 / 365) if user.birthday else None
    user.birthday = bday
    await user.save()
    await state.finish()

    if user_data['status_user'] == 'new':
        return await set_hobbies_state(message)
    else:
        if old_age != age:
            await recalculation_int(user=user, check_func=check_age, attr_name='percent_age')
        return await profile_handler(message)
    
