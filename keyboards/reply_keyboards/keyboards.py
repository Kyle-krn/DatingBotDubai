from aiogram import types


async def geolocation_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton(text='Отправить локацию', request_location=True))
    return keyboard


# async def main_keyboard():
