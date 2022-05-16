from handlers.payments.rate_plane_handlers import rate_plane_handler
from handlers.view_relations.views_handlers import view_relations_handler
from loader import dp
from aiogram import types
from aiogram.dispatcher import FSMContext
from handlers.profile.views_self_profile_handlers import profile_handler
from handlers.search_settings.view_settings_handler import settings_handler
from handlers.dating.dating_handlers import search_dating
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'cancel_state', state='*')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'cancel_state_settings', state='*')
async def cancel_state_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.finish()
    if call.data.split(':')[0] == 'cancel_state_settings':
        return await settings_handler(call.message)
    else:
        return await profile_handler(call.message)


async def redirect_handler(message: types.Message, button_text: str):
    if button_text == '👥 Найти пару' or button_text == '/dating':
        return await search_dating(message)
    elif button_text == '👤 Профиль' or button_text == '/profile':
        return await profile_handler(message)
    elif button_text == "💑 Симпатии" or button_text == '/likes':
        return await view_relations_handler(message)
    elif button_text == '⚙ Настройки' or button_text == '/settings':
        return await settings_handler(message)
    elif button_text == '💸 Тарифные планы' or button_text == '/rate_plane':
        return await rate_plane_handler(message)
    elif button_text == '🆘 Помощь' or button_text == '/help':
        pass