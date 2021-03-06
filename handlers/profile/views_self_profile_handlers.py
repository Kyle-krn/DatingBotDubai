from datetime import datetime
from data.config import PHOTO_TYPES, VIDEO_TYPES
from loader import dp
from aiogram import types
from models import models
from keyboards.inline.user_settings_keyboards import main_profile_keyboard
from utils.text_for_ad import generate_ad_text
from utils.zodiak import zodiac_sign


@dp.message_handler(commands=['profile'])
@dp.message_handler(regexp="^(👤 Профиль)$")
# @dp.call(regexp="^(👤 Профиль)$")
async def profile_handler(message: types.Message):
    user = await models.UserModel.get(tg_id=message.chat.id)
    # if user.end_registration is False:
    if user.male is None or user.place is None or user.birthday is None or user.marital_status is None:
        # return await message.answer("Вы не закончили регистрацию")
        return await message.answer("Вы не закончили регистрацию")
    
    avatar = await user.avatar
    if not avatar:
        photo = types.input_file.InputFile("static/guest.png")
        return await message.answer_photo(photo=photo, reply_markup=await main_profile_keyboard(dubai=user.dubai))

    zodiak = await zodiac_sign(user.birthday)

    year = datetime.now().year

    text = await generate_ad_text(target_user=user, general_percent=None)
    # text = f"{user.name}, {year-user.birthday.year}\n"  \
    #        f"{zodiak}\n" \
    #        f"🗺️ {user.place}\n" \
    #        f"👫 {user.marital_status}\n"  \
    #        f"Дети: "
    # if user.children is True:
    #     text += "Есть\n"
    # elif user.children is False:
    #     text += "Нет\n"
    # elif user.children is None:
    #     text += "Не скажу\n"
    # if user.children_age != []:
    #     text += "Возраст детей: " + ", ".join([str(i)+" г." for i in user.children_age]) + "\n"
    # target_hobbies = await user.hobbies.all()
    # if target_hobbies:
    #     text += "Увлечения: " + ", ".join([i.title_hobbie for i in target_hobbies]) + "\n"

    # photo_types = ('jpeg', 'jpg', "webm", "png")
    # video_types = ("mp4", "avi")
    if avatar.file_id is None:
        return await message.answer_photo(photo=open('static/guest.png', 'rb'),caption=text, reply_markup=await main_profile_keyboard(dubai=user.dubai))
    
    if avatar.file_type.lower() in PHOTO_TYPES:
        await message.answer_photo(photo=avatar.file_id,caption=text, reply_markup=await main_profile_keyboard(dubai=user.dubai))
    elif avatar.file_type.lower() in VIDEO_TYPES:
        await message.answer_video(video=avatar.file_id, caption=text, reply_markup=await main_profile_keyboard(dubai=user.dubai))
