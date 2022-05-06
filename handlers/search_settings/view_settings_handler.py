from datetime import date
from loader import dp
from aiogram import types
from models import models
from keyboards.inline.user_settings_keyboards import settings_search_keyboard, gender_keyboard, settings_children_keyboard
from handlers.calculation_relations.relations_handlers import check_settings_gender
from handlers.calculation_relations.recalculation_relations import get_target_user_from_relation, recalculation_age, recalculation_children
from tortoise.queryset import Q
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
class SearchSettingsState(StatesGroup):
    age = State()
    children_age = State()
    
@dp.message_handler(regexp="^(⚙ Настройки)$")
async def settings_handler(message: types.Message):
    user = await models.UserModel.get(tg_id=message.chat.id)
    settings: models.UserSearchSettings = await user.search_settings
    text = "⚙️ Настройки\n\n" \
           "Текущий фильтр по подбору партнеров:\n"
    text += f"Пол: "
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


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'settings_gender')
async def partner_gender_handler(call: types.CallbackQuery):
    await call.message.edit_text("Выберите пол партнера", reply_markup=await gender_keyboard("partner_gender"))


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'partner_gender')
async def set_partner_gender_handler(call: types.CallbackQuery):
    user = await models.UserModel.get(tg_id=call.message.chat.id)
    settings: models.UserSearchSettings = await user.search_settings
    gender = call.data.split(':')[1]
    if gender == 'male':
        male = True
    else:
        male = False
    if settings.male != male:
        settings.male = male
        await settings.save()
        await recalculation_by_gender(user)
    await call.message.delete()
    return await settings_handler(call.message)


async def recalculation_by_gender(user: types.CallbackQuery):
    relations = await models.UsersRelations.filter(Q(user=user) | Q(target_user=user))
    for relation in relations:
        target_user = await get_target_user_from_relation(user=user, relation=relation)
        result_gender_check = await check_settings_gender(user=user, target_user=target_user)

        if relation.result_gender_check is True and result_gender_check is False:
            relation.percent_compatibility = 0
            relation.result_gender_check = False
            await relation.save()
        
        elif relation.result_gender_check is False and result_gender_check is True:
            relation.result_gender_check = True
            if relation.result_distance_check and relation.result_purp_check:
                new_percent = 30 + relation.percent_age + relation.percent_children + relation.percent_hobbies
                if new_percent > 0:
                    relation.percent_compatibility = new_percent
                    await models.UserView.get_or_create(user=user, target_user=target_user, relation=relation)
                    await models.UserView.get_or_create(user=target_user, target_user=user, relation=relation)
                else:
                    relation.percent_compatibility = 0
                # await relation.save()
            await relation.save()
        


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'settings_age')
async def partner_gender_handler(call: types.CallbackQuery):
    await SearchSettingsState.age.set()
    await call.message.edit_text("Введите возраст от и до в формате 18-30")


@dp.message_handler(state=SearchSettingsState.age)
async def set_partner_gender_handler(message: types.Message, state: FSMContext):
    try:
        age = message.text.split('-')
        if len(age) != 2:
            raise IndexError
        min = int(age[0].strip())
        max = int(age[1].strip())
    except Exception as e:
        print(e)
        return await message.answer("Не могу распознать возраст, попробуйте снова")
    
    if min <0 or max <0:
        return await message.answer("Возраст не может быть отрицательным")
    if min < 18:
        return await message.answer("Минимальный возраст 18 лет.")
    if min > max:
        return await message.answer("Минимальный возраст не может привышать максимальный возраст.")
    user = await models.UserModel.get(tg_id=message.chat.id)
    settings: models.UserSearchSettings = await user.search_settings
    if settings.min_age != min or settings.max_age != max: 
        settings.min_age = min
        settings.max_age = max
        await settings.save()
        today = date.today()
        user_age = int((today - user.birthday).total_seconds() / 60 / 60 / 24 / 365)
        await recalculation_age(user=user, user_age=user_age)
    await state.finish()
    return await settings_handler(message)



@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'settings_children')
async def settings_children_handler(call: types.CallbackQuery):
    await call.message.edit_text("Выберите один из пунктов", reply_markup=await settings_children_keyboard())



@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'set_settings_children')
async def set_settings_children_handler(call: types.CallbackQuery):
    user = await models.UserModel.get(tg_id=call.message.chat.id)
    settings: models.UserSearchSettings = await user.search_settings
    answer = call.data.split(':')[1]
    if answer == 'yes':
        return await set_children_age_state_handler(call)
    elif answer == 'no':
        value = False
    elif answer == 'none':
        value = None
    if settings.children != value:
        settings.children = value
        settings.children_min_age = None
        settings.children_max_age = None
        await settings.save()
        await recalculation_children(user=user)
    await call.message.delete()
    return await settings_handler(call.message)


async def set_children_age_state_handler(call: types.CallbackQuery):
    await SearchSettingsState.children_age.set()
    await call.message.edit_text("Введите возраст детей от и до в формате 0-17, если возраст детей не важен, введите 0")

@dp.message_handler(state=SearchSettingsState.children_age)
async def set_value_children_age_hanlder(message: types.Message, state: FSMContext):
    try:
        if message.text.strip() != '0':
            age = message.text.split('-')
            if len(age) != 2:
                raise IndexError
            min = int(age[0].strip())
            max = int(age[1].strip())
    except Exception as e:
        print(e)
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

    user = await models.UserModel.get(tg_id=message.chat.id)
    settings: models.UserSearchSettings = await user.search_settings
    settings.children = True
    settings.children_min_age = min
    settings.children_max_age = max
    await settings.save()
    await recalculation_children(user=user)
    await state.finish()
    return await settings_handler(message)