from aiogram import types


async def like_keyboard(view_id: int, superlike_count: int):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="👍", callback_data=f"reaction:like:{view_id}"), 
                 types.InlineKeyboardButton(text=f"⭐({superlike_count})", callback_data=f"reaction:superlike:{view_id}"), 
                 types.InlineKeyboardButton(text="👎", callback_data=f"reaction:dislike:{view_id}"))
    return keyboard