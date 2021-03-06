from handlers.profile.avatar_handlers import send_document_handler
from handlers.profile.bday_handers import birthday_handler
from handlers.profile.city_handlers import city_set_state_handler
from handlers.profile.dubai_handlers import dubai_handler, settings_companion_place_hanlder
from handlers.profile.marriage_handlers import marriage_handler
from handlers.profile.purp_handlers import purp_handler
from keyboards.inline.user_settings_keyboards import gender_keyboard
from loader import dp
from models import models
from aiogram import types
from aiogram.dispatcher import FSMContext

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'end_registration_user', state="*")
async def redirect_end_register(call: types.CallbackQuery, state: FSMContext):
    user = await models.UserModel.get(tg_id=call.message.chat.id)
    await state.finish()
    await call.message.delete()
    return await end_registration(message=call.message, user=user)

async def end_registration(message: types.Message, user: models.UserModel):
    avatar = await models.AvatarModel.get_or_create(user=user)
    avatar = avatar[0]
    if user.male is None:
        return await message.answer(f"Укажите Ваш пол:", reply_markup=await gender_keyboard())
    elif user.place_id is None:
        return await city_set_state_handler(message)
    elif user.dubai is False and user.moving_to_dubai is None:
        return await dubai_handler(message)
    elif len(await user.interest_place_companion.all()) == 0:
        return await settings_companion_place_hanlder(message)
    elif user.birthday is None:
        return await birthday_handler(message)
    elif user.marital_status_id is None:
        return await marriage_handler(message)
    elif len(await user.purp_dating.all()) == 0:
        return await purp_handler(message, change=False)
    elif avatar.file_id is None:
        return await send_document_handler(message)