from aiogram import types


async def geolocation_keyboard(status_user: str):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton(text='Отправить локацию', request_location=True))
    if status_user == 'old':
        keyboard.add(types.KeyboardButton(text='🛑 Отмена'))
    return keyboard


async def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text="👥 Найти пару"), types.KeyboardButton(text="👤 Профиль"))
    keyboard.add(types.KeyboardButton(text="💑 Симпатии"), types.KeyboardButton(text="⚙ Настройки"))
    keyboard.add(types.KeyboardButton(text="💸 Тарифные планы"), types.KeyboardButton(text="🆘 Помощь"))
    return keyboard