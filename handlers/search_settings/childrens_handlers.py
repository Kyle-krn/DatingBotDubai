import re
from data.config import KEYBOARD_TEXT
from handlers.calculation_relations.recalculation_relations import recalculation_int
from handlers.calculation_relations.relations_handlers import check_children
from handlers.cancel_state_handler import redirect_handler
from keyboards.inline.user_settings_keyboards import settings_children_keyboard
from loader import dp
from aiogram import types
from models import models
from .view_settings_handler import settings_handler
from aiogram.dispatcher import FSMContext
from .settings_state import SearchSettingsState

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'settings_children')
async def settings_children_handler(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer("Выберите один из пунктов", reply_markup=await settings_children_keyboard())


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'set_settings_children')
async def set_settings_children_handler(call: types.CallbackQuery):
    user = await models.UserModel.get(tg_id=call.message.chat.id)
    settings: models.UserSearchSettings = await user.search_settings
    answer = call.data.split(':')[1]
    if answer == 'yes':
        text = "Есть"
        await call.message.edit_text(text=f"Дети у партнера: {text}")
        return await set_children_age_state_handler(call)
    elif answer == 'no':
        text = "Нет"
        value = False
    elif answer == 'none':
        text = "Не важно"
        value = None
    elif answer == 'cancel':
        return await call.message.delete()
        # return await settings_handler(call.message)
    await call.message.edit_text(text=f"Дети у партнера: {text}")
    if settings.children != value:
        settings.children = value
        settings.children_min_age = None
        settings.children_max_age = None
        await settings.save()
        await recalculation_int(user=user,
                            check_func=check_children,
                            attr_name="percent_children")
    # await call.message.delete()
    return await settings_handler(call.message)


async def set_children_age_state_handler(call: types.CallbackQuery):
    await SearchSettingsState.children_age.set()
    await call.message.answer("Введите возраст детей от и до в формате 0-17, если возраст детей не важен, введите 0")


@dp.message_handler(state=SearchSettingsState.children_age)
async def set_value_children_age_hanlder(message: types.Message, state: FSMContext):
    if message.text not in KEYBOARD_TEXT:
        try:
            if message.text.strip() != '0':
                age = message.text.split('-')
                if len(age) != 2:
                    raise IndexError
                min = int(age[0].strip())
                max = int(age[1].strip())
        except Exception as e:
            return await message.answer("Не могу распознать возраст, попробуйте снова")
        
        if message.text.strip() != '0':
            if min <0 or max <0:
                return await message.answer("Возраст не может быть отрицательным")
            if max > 18:
                return await message.answer("Максимальный возраст 17 лет.")
            if min > max:
                return await message.answer("Минимальный возраст не может привышать максимальный возраст.")
        else:
            min = None
            max = None
    else:
        min = None
        max = None
    user = await models.UserModel.get(tg_id=message.chat.id)
    settings: models.UserSearchSettings = await user.search_settings
    settings.children = True
    settings.children_min_age = min
    settings.children_max_age = max
    await settings.save()
    await recalculation_int(user=user,
                            check_func=check_children,
                            attr_name="percent_children")
    await state.finish()
    if message.text in KEYBOARD_TEXT:
        return await redirect_handler(message, message.text)
    else:
        return await settings_handler(message)