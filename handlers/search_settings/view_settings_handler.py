from datetime import date
from keyboards.inline.inline_keyboards import one_button_keyboard
from loader import dp
from aiogram import types
from models import models
from keyboards.inline.user_settings_keyboards import settings_search_keyboard, gender_keyboard, settings_children_keyboard
from handlers.calculation_relations.relations_handlers import check_settings_gender
from handlers.calculation_relations.recalculation_relations import get_target_user_from_relation, recalculation_age, recalculation_children, recalculation_by_gender
from tortoise.queryset import Q
from aiogram.dispatcher import FSMContext
from .settings_state import SearchSettingsState


    

@dp.message_handler(regexp="^(⚙ Настройки)$")
async def settings_handler(message: types.Message):
    user = await models.UserModel.get(tg_id=message.chat.id)
    if user.end_registration is False:
        return await message.answer("Вы не закончили регистрацию")
    settings: models.UserSearchSettings = await user.search_settings
    text = "⚙️ Настройки\n\n" \
           "Текущий фильтр по подбору партнеров:\n"
    text += f"Пол: "
    if settings.male is True:
        text += "Муж.\n"
    elif settings.male is False:
        text += "Жен.\n"
    elif settings.male is None:
        text += "Неважно\n"
    text += "Муж.\n" if settings.male is True else "Жен.\n"
    settings.min_age = 18 if settings.min_age is None else settings.min_age
    settings.max_age = 99 if settings.max_age is None else settings.max_age
    text += f"Возр. Диапазон: {settings.min_age}-{settings.max_age} лет\n"
    if settings.children is True:
        children_text = "✅"
    elif settings.children is False:
        children_text = "❌"
    else:
        children_text = "Неважно"
    text += f"Наличие детей: {children_text}\n"
    if settings.children:
        settings.children_min_age = 0 if settings.children_min_age is None else settings.children_min_age 
        settings.children_max_age = 18 if settings.children_max_age is None else settings.children_max_age
        text += f"Возр. Диапазон детей: {settings.children_min_age} - {settings.children_max_age} лет\n"
    await message.answer(text=text, reply_markup=await settings_search_keyboard())





