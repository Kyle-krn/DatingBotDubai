from loader import dp
from aiogram import types
from aiogram.dispatcher import FSMContext
from handlers.profile.views_self_profile_handlers import profile_handler
from handlers.search_settings.view_settings_handler import settings_handler

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'cancel_state', state='*')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'cancel_state_settings', state='*')
async def cancel_state_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.finish()
    if call.data.split(':')[0] == 'cancel_state_settings':
        return await settings_handler(call.message)
    else:
        return await profile_handler(call.message)
