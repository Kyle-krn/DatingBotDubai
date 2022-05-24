from handlers.search_settings.view_settings_handler import settings_handler
from keyboards.inline.user_settings_keyboards import gender_keyboard
from models import models
from aiogram import types
from loader import dp

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'settings_gender')
async def partner_gender_handler(call: types.CallbackQuery):
    user = await models.UserModel.get(tg_id=call.message.chat.id)
    settings: models.UserSearchSettings = await user.search_settings
    text = f"Пол: "
    if settings.male is True:
        text += "Муж.\n"
    elif settings.male is False:
        text += "Жен.\n"
    elif settings.male is None:
        text += "Неважно\n"
    text += "\nВыберите пол партнера"
    await call.answer()
    await call.message.answer(text, reply_markup=await gender_keyboard("partner_gender"))


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'partner_gender')
async def set_partner_gender_handler(call: types.CallbackQuery):
    user = await models.UserModel.get(tg_id=call.message.chat.id)
    settings: models.UserSearchSettings = await user.search_settings
    gender = call.data.split(':')[1]
    if gender == 'male':
        male = True
        text = "Мужчина"
    elif gender == 'female':
        male = False
        text = "Женщина"
    elif gender == 'none':
        male = None
        text = "Не важно"
    if settings.male != male:
        settings.male = male
        await settings.save()
    await call.message.edit_text(text=f"Выбранный пол партнера: {text}")
    # await call.message.delete()
    return await settings_handler(call.message)


