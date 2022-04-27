from aiogram import types

async def gender_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='♂️ Мужчина',callback_data='gender:male'), 
                 types.InlineKeyboardButton(text='♀️ Женщина',callback_data='gender:female'))
    return keyboard