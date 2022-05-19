from aiogram import types


async def like_keyboard(view_id: int, superlike_count: int, callback: str = 'reaction', offset: int = 0):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="👍", callback_data=f"{callback}:like:{view_id}:{offset}"), 
                 types.InlineKeyboardButton(text=f"⭐({superlike_count})", callback_data=f"{callback}:superlike:{view_id}:{offset}"), 
                 types.InlineKeyboardButton(text="👎", callback_data=f"{callback}:dislike:{view_id}:{offset}"))
    if callback == "y_like_reaction":
        keyboard.add(types.InlineKeyboardButton(text="⬅️", callback_data=f"offset_your_likes:{offset-1}"),
                 types.InlineKeyboardButton(text="➡️", callback_data=f"offset_your_likes:{offset+1}"))    
    return keyboard


async def verification_keyboards(user_id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Одобрить", callback_data=f"verification:{user_id}:True"),
                 types.InlineKeyboardButton(text="Отклонить", callback_data=f"verification:{user_id}:False"),)
    return keyboard


async def view_relation_keyboard(count_your_like: int, count_mutal_like: int):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text=f"({count_your_like}) 💟 Тебя лайкнули", callback_data=f"your_likes:0"),
                 types.InlineKeyboardButton(text=f"({count_mutal_like}) 😍 Взаимные лайки", callback_data=f"mutal_likes:0"),)
    return keyboard


async def mutal_likes_keyboard(offset):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="⬅️", callback_data=f"mutal_likes:{offset-1}"),
                 types.InlineKeyboardButton(text="➡️", callback_data=f"mutal_likes:{offset+1}"))
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="back_likes:"))
    return keyboard


async def one_button_keyboard(text: str, callback: str):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text=text, callback_data=callback))
    return keyboard


