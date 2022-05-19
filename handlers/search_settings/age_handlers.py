
from datetime import date
from data.config import KEYBOARD_TEXT
# from handlers.calculation_relations.recalculation_relations import recalculation_int
from utils.calculation_relations.recalculations import recalculation_int
# from handlers.calculation_relations.relations_handlers import check_age
from utils.calculation_relations.check_relations import check_age
from handlers.cancel_state_handler import redirect_handler
from handlers.search_settings.view_settings_handler import settings_handler
from keyboards.inline.inline_keyboards import one_button_keyboard
from loader import dp
from models import models
from aiogram import types
from .settings_state import SearchSettingsState
from aiogram.dispatcher import FSMContext



@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'settings_age')
async def partner_gender_handler(call: types.CallbackQuery):
    await SearchSettingsState.age.set()
    await call.answer()
    await call.message.answer("Введите возраст от и до в формате 18-30", reply_markup=await one_button_keyboard(text="Назад", callback="cancel_state_settings"))



@dp.message_handler(state=SearchSettingsState.age)
async def set_partner_gender_handler(message: types.Message, state: FSMContext):
    if message.text in KEYBOARD_TEXT:
        await state.finish()
        return await redirect_handler(message, message.text)
    try:
        age = message.text.split('-')
        if len(age) != 2:
            raise IndexError
        min = int(age[0].strip())
        max = int(age[1].strip())
    except Exception as e:
        return await message.answer("Не могу распознать возраст, попробуйте снова", reply_markup=await one_button_keyboard(text="Назад", callback="cancel_state_settings"))
    if min <0 or max <0:
        return await message.answer("Возраст не может быть отрицательным", reply_markup=await one_button_keyboard(text="Назад", callback="cancel_state_settings"))
    if min < 18:
        return await message.answer("Минимальный возраст 18 лет.", reply_markup=await one_button_keyboard(text="Назад", callback="cancel_state_settings"))
    if min > max:
        return await message.answer("Минимальный возраст не может привышать максимальный возраст.", reply_markup=await one_button_keyboard(text="Назад", callback="cancel_state_settings"))
    user = await models.UserModel.get(tg_id=message.chat.id)
    settings: models.UserSearchSettings = await user.search_settings
    if settings.min_age != min or settings.max_age != max: 
        settings.min_age = min
        settings.max_age = max
        await settings.save()
        today = date.today()
        user_age = int((today - user.birthday).total_seconds() / 60 / 60 / 24 / 365)
        await recalculation_int(user=user, check_func=check_age, attr_name='percent_age')
    await state.finish()
    return await settings_handler(message)