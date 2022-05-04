from loader import dp
from aiogram import types
from models import models
from keyboards.inline.user_settings_keyboards import main_profile_keyboard


@dp.message_handler(commands=['profile'])
@dp.message_handler(regexp="^(👤 Профиль)$")
# @dp.call(regexp="^(👤 Профиль)$")
async def profile_handler(message: types.Message):
    user = await models.UserModel.get(tg_id=message.chat.id)
    avatar = await user.avatar
    if not avatar:
        photo = types.input_file.InputFile("static/guest.png")
        return await message.answer_photo(photo=photo, reply_markup=await main_profile_keyboard())
    
    photo_types = ('jpeg', 'jpg', "webm", "png")
    video_types = ("mp4", "avi")
    if avatar.file_type.lower() in photo_types:
        await message.answer_photo(photo=avatar.file_id, reply_markup=await main_profile_keyboard())
    elif avatar.file_type.lower() in video_types:
        await message.answer_video(video=avatar.file_id, reply_markup=await main_profile_keyboard())
