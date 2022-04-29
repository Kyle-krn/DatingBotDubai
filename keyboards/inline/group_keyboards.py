from aiogram import types

async def verification_keyboards(user_id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Одобрить", callback_data=f"verification:{user_id}:True"),
                 types.InlineKeyboardButton(text="Отклонить", callback_data=f"verification:{user_id}:False"),)
    return keyboard