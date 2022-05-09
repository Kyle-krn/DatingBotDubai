from aiogram import types


async def rate_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Купить Gold", callback_data="buy:gold:1"),
                 types.InlineKeyboardButton(text="Купить 10 суперлайков.", callback_data="buy:likes:10"))
    return keyboard


