import re
from aiogram import types
from tortoise import List
from models.models import DatingInterestPlace, Hobbies, UserModel, PurposeOfDating


async def main_profile_keyboard(dubai: bool):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='📷 Фото',callback_data='change_ava:'),    
                 types.InlineKeyboardButton(text='Увлечения',callback_data='change_hobbies:'))
    if dubai is False:
        keyboard.add(types.InlineKeyboardButton(text='Семейное положение',callback_data='change_marriage:'),    
                    types.InlineKeyboardButton(text='Переезд в Дубаи',callback_data='change_remove_dubai:'))
    elif dubai is True:
        keyboard.add(types.InlineKeyboardButton(text='Семейное положение',callback_data='change_marriage:'))

    keyboard.add(types.InlineKeyboardButton(text='Возраст',callback_data='change_bday:'),    #change_marriage
                 types.InlineKeyboardButton(text='Город',callback_data='change_place:'))

    keyboard.add(types.InlineKeyboardButton(text='Цель знакомства',callback_data='change_purp:'),    #change_marriage
                 types.InlineKeyboardButton(text='Дети',callback_data='change_children:'))
    return keyboard

async def gender_keyboard(callback: str = "gender"):
    keyboard = types.InlineKeyboardMarkup()
    mal_button = types.InlineKeyboardButton(text='♂️ Мужчина',callback_data=f'{callback}:male') 
    fem_button = types.InlineKeyboardButton(text='♀️ Женщина',callback_data=f'{callback}:female')
    keyboard.add(mal_button, fem_button)
    if callback == 'partner_gender':
        keyboard.add(types.InlineKeyboardButton(text='⚤ Не важно',callback_data=f'{callback}:none'))
    return keyboard


async def city_answer_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Да',callback_data='city:yes'), 
                 types.InlineKeyboardButton(text='Нет',callback_data='city:no'))
    return keyboard


async def dubai_answer_keyboard(remove_in_dubai: bool = None, callback: str = 'remove_dubai'):
    keyboard = types.InlineKeyboardMarkup()
    text_yes = 'Да'
    text_no = 'Нет'
    if remove_in_dubai is not None:
        text_yes = '✅ Да' if remove_in_dubai is True else "Да"
        text_no = '✅ Нет' if remove_in_dubai is False else "Нет"
    keyboard.add(types.InlineKeyboardButton(text=text_yes,
                                            callback_data=f'{callback}:yes'), 
                 types.InlineKeyboardButton(text=text_no,
                                            callback_data=f'{callback}:no'))
    return keyboard


async def companion_dubai_keyboard(user: UserModel, callback_prefix: str = ''):
    keyboard = types.InlineKeyboardMarkup()
    interest_user = await user.interest_place_companion.all()
    interestings = await DatingInterestPlace.all()
    for interest in interestings:
        text = interest.title_interest
        if interest in interest_user:
            text = "✅ " + text
        keyboard.add(types.InlineKeyboardButton(text=text, callback_data=f"{callback_prefix}companion_dubai:{interest.id}"))
    if len(interest_user) > 0:
        callback = 'bday:'
        if callback_prefix == 'c_':
            callback = 'back_settings:'
        keyboard.add(types.InlineKeyboardButton(text="Далее", callback_data=callback))
    return keyboard


async def skip_settings_keyboard(callback: str):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Пропустить", callback_data=callback))
    return keyboard


async def remove_hobbie_keyboard(hobbies_list: List[Hobbies], status_user: str = 'new'):
    keyboard = types.InlineKeyboardMarkup()
    for hobbie in hobbies_list:
        keyboard.add(types.InlineKeyboardButton(text=hobbie.title_hobbie, callback_data=f"remove_hobbie:{hobbie.id}"))
    if status_user == 'new':
        text = "Перейти к следующему шагу"
    elif status_user == 'old':
        text = "Продолжить"
    keyboard.add(types.InlineKeyboardButton(text=text, callback_data=f"skip_hobbie:"))
    
    return keyboard


async def marital_status_keyboard(user_martial_status: str, callback: str = "ms"):
    '''callback = "ms" or "c_ms"'''
    keyboard = types.InlineKeyboardMarkup()                                         # mar_status - ms
    status_1 = "Женат/Замужем" 
    keyboard.add(types.InlineKeyboardButton(text=status_1 if status_1 != user_martial_status else "✅" + status_1, 
                                            callback_data=f"{callback}:{status_1}"))
    status_2 = "В отношениях"
    keyboard.add(types.InlineKeyboardButton(text=status_2 if status_2 != user_martial_status else "✅" + status_2, 
                                            callback_data=f"{callback}:{status_2}"))
    status_3 = "Свободен(-на)"
    keyboard.add(types.InlineKeyboardButton(text=status_3 if status_3 != user_martial_status else "✅" + status_3, 
                                            callback_data=f"{callback}:{status_3}"))
    return keyboard


async def children_keyboard(prefix_callback: str = ''):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Да", callback_data=f"{prefix_callback}add_children:"))
    keyboard.add(types.InlineKeyboardButton(text="Нет", callback_data=f"{prefix_callback}skip_children:no"))
    keyboard.add(types.InlineKeyboardButton(text="Не скажу", callback_data=f"{prefix_callback}skip_children:not_say"))
    return keyboard


async def purp_keyboard(user_purp: List[PurposeOfDating], callback_for_next: str = "send_ava", callback_for_purp: str = "purp"):
    keyboard = types.InlineKeyboardMarkup()
    purps = await PurposeOfDating.all()
    for purp in purps:
        text = purp.title_purp
        if purp in user_purp:
            text = "✅ " + text
        keyboard.add(types.InlineKeyboardButton(text=text, callback_data=f"{callback_for_purp}:{purp.id}"))
    if len(user_purp) > 0:
        keyboard.add(types.InlineKeyboardButton(text="Продолжить", callback_data=f"{callback_for_next}:"))
    return keyboard


async def avatar_keyboard(status_user: str):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="ℹ️ Как загрузить фото без потери качества?", callback_data="how_upload_document:"))
    if status_user == 'old':
        keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="cancel_state:"))
    # keyboard.add(types.InlineKeyboardButton(text="Пропустить", callback_data="skip_ava:"))
    return keyboard


async def back_document_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    # keyboard.add(types.InlineKeyboardButton(text="ℹ️ Как загрузить фото без потери качества?", callback_data="how_upload_document:"))
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="back_send_ava:"))
    return keyboard


async def settings_search_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Пол", callback_data="settings_gender:"),
                types.InlineKeyboardButton(text="Возраст", callback_data="settings_age:"))
    keyboard.add(types.InlineKeyboardButton(text="Дети", callback_data="settings_children:"),
                types.InlineKeyboardButton(text="Местоположение пары", callback_data="settings_companion_dubai:"))
    return keyboard


async def settings_children_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Есть", callback_data="set_settings_children:yes"))
    keyboard.add(types.InlineKeyboardButton(text="Нет", callback_data="set_settings_children:no"))
    keyboard.add(types.InlineKeyboardButton(text="Не важно", callback_data="set_settings_children:none"))
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="set_settings_children:cancel"))
    return keyboard
