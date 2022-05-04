from loader import dp
from aiogram import types
from .profile_state import ProfileSettingsState
from aiogram.dispatcher import FSMContext
from keyboards.inline.user_settings_keyboards import skip_settings_keyboard
from datetime import datetime, date
from models import models
from .hobbies_handlers import set_hobbies_state

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'bday')
async def birthday_handler(call: types.CallbackQuery):
    await ProfileSettingsState.bday.set()
    await call.message.delete()
    await call.message.answer("Укажи свою дату рождения в формате DD.MM.YYYY, например 23.05.1996")


@dp.message_handler(state=ProfileSettingsState.bday)
# @dp.message_handler(lambda message: True)
async def input_bday_handler(message: types.Message, state: FSMContext):
    try:
        bday = datetime.strptime(message.text, '%d.%m.%Y').date()
    except ValueError:
        return await message.answer("<b>Не верный формат!</b>\n\nУкажи свою дату рождения в формате DD.MM.YYYY, например 23.05.1996")
    today = date.today()
    age = int((today - bday).total_seconds() / 60 / 60 / 24 / 365)
    if (18 < age < 100) is False:
        return await message.answer("Обращаем ваше внимание: использование сервиса Zodier запрещено лицам, моложе 18 лет! Возможно, вы ошиблись! Укажите свою дату рождения в формате DD.MM.YYYY, например 23.07.1996")
    user = await models.UserModel.get(tg_id=message.chat.id)
    user.birthday = bday
    await user.save()
    await state.finish()
    return await set_hobbies_state(message)

    


