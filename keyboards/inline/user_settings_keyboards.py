import re
from aiogram import types
from tortoise import List
from models.models import DatingInterestPlace, Hobbies, UserModel, PurposeOfDating
async def gender_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='♂️ Мужчина',callback_data='gender:male'), 
                 types.InlineKeyboardButton(text='♀️ Женщина',callback_data='gender:female'))
    return keyboard


async def city_answer_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Да',callback_data='city:yes'), 
                 types.InlineKeyboardButton(text='Нет',callback_data='city:no'))
    return keyboard


async def dubai_answer_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Да',callback_data='remove_dubai:yes'), 
                 types.InlineKeyboardButton(text='Нет',callback_data='remove_dubai:no'))
    return keyboard


async def companion_dubai_keyboard(user: UserModel):
    keyboard = types.InlineKeyboardMarkup()
    interest_user = await user.interest_place_companion.all()
    interestings = await DatingInterestPlace.all()
    for interest in interestings:
        text = interest.title_interest
        if interest in interest_user:
            text = "✅ " + text
        keyboard.add(types.InlineKeyboardButton(text=text, callback_data=f"companion_dubai:{interest.id}"))
    if len(interest_user) > 0:
        keyboard.add(types.InlineKeyboardButton(text="Далее", callback_data="bday:"))
    return keyboard


async def skip_settings_keyboard(callback: str):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Пропустить", callback_data=callback))
    return keyboard


async def remove_hobbie_keyboard(hobbies_list: List[Hobbies]):
    keyboard = types.InlineKeyboardMarkup()
    for hobbie in hobbies_list:
        keyboard.add(types.InlineKeyboardButton(text=hobbie.title_hobbie, callback_data=f"remove_hobbie:{hobbie.id}"))
    keyboard.add(types.InlineKeyboardButton(text="Добавить увлечения", callback_data=f"add_hobbie:"))
    keyboard.add(types.InlineKeyboardButton(text="Продолжить", callback_data=f"marriage:"))
    return keyboard


async def marital_status_keyboard():
    keyboard = types.InlineKeyboardMarkup()                                         # mar_status - ms
    status = "Женат/Замужем"
    keyboard.add(types.InlineKeyboardButton(text=status, callback_data=f"ms:{status}"))
    status = "В отношениях"
    keyboard.add(types.InlineKeyboardButton(text=status, callback_data=f"ms:{status}"))
    status = "Свободен(-на)"
    keyboard.add(types.InlineKeyboardButton(text=status, callback_data=f"ms:{status}"))
    return keyboard


async def children_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Да", callback_data=f"children:yes"))
    keyboard.add(types.InlineKeyboardButton(text="Нет", callback_data=f"skip_children:no"))
    keyboard.add(types.InlineKeyboardButton(text="Не скажу", callback_data=f"skip_children:not_say"))
    return keyboard


async def purp_keyboard(user_purp: List[PurposeOfDating]):
    keyboard = types.InlineKeyboardMarkup()
    purps = await PurposeOfDating.all()
    for purp in purps:
        text = purp.title_purp
        if purp in user_purp:
            text = "✅ " + text
        keyboard.add(types.InlineKeyboardButton(text=text, callback_data=f"purp:{purp.id}"))
    if len(user_purp) > 0:
        keyboard.add(types.InlineKeyboardButton(text="Продолжить", callback_data=f"send_ava:"))
    return keyboard


async def avatar_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="ℹ️ Как загрузить фото без потери качества?", callback_data="how_upload_document:"))
    keyboard.add(types.InlineKeyboardButton(text="Пропустить", callback_data="skip_ava:"))
    return keyboard


async def back_document_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    # keyboard.add(types.InlineKeyboardButton(text="ℹ️ Как загрузить фото без потери качества?", callback_data="how_upload_document:"))
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="back_send_ava:"))
    return keyboard