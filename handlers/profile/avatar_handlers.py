from datetime import datetime
from data.config import PHOTO_TYPES, VIDEO_TYPES
from loader import dp, BASE_DIR
from models import models
from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.inline.user_settings_keyboards import avatar_keyboard, back_document_keyboard
from keyboards.reply_keyboards.keyboards import main_keyboard
from .profile_state import ProfileSettingsState
from handlers.group.new_reg_user_handlers import calculation_new_user, send_new_registration_in_chanel
import os


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'send_ava')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'change_ava')
async def send_document_handler(call: types.CallbackQuery):
    await ProfileSettingsState.avatar.set()
    state = dp.get_current().current_state()
    if call.data.split(':')[0] == 'send_ava':
        status_user='new'
        await state.update_data(status_user=status_user)
        await call.message.edit_text(text="Пришли, пожалуйста, фото или видео☺️", reply_markup=await avatar_keyboard(status_user))
    else:
        status_user = 'old'
        await state.update_data(status_user=status_user)
        await call.message.delete()
        await call.message.answer(text="Пришли, пожалуйста, фото или видео☺️", reply_markup=await avatar_keyboard(status_user))
    


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'back_send_ava', state=ProfileSettingsState.avatar)
async def back_send_document_handler(call: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    await call.message.edit_text(text="Пришли, пожалуйста, фото или видео☺️", reply_markup=await avatar_keyboard(user_data['status_user']))


@dp.message_handler(content_types=['document', 'photo', 'video'], state=ProfileSettingsState.avatar)
async def upload_file_handler(message: types.Message, state: FSMContext):
    user = await models.UserModel.get(tg_id=message.chat.id)
    user_data = await state.get_data()
    static_path = "/static/"
    folder_path = f'avatar_telegram/{user.id}/'
    full_path = static_path + folder_path
    if os.path.exists(BASE_DIR + "/static/avatar_telegram/") is False:
        os.mkdir(BASE_DIR + "/static/avatar_telegram/")

    if os.path.exists(BASE_DIR + full_path) is False:
        os.mkdir(BASE_DIR + full_path)

    if message.video:
        if (message.video.file_size / 1024 / 1024) > 10:
            return await message.answer("Пожалуйста, загрузите файл до 10 Мб.")
        file_id = message.video.file_id
        file_type = message.video.file_name.split('.')[-1]
        file_path = full_path + f'avatar.{file_type}'
        photo_bool=False
        await message.video.download(BASE_DIR + file_path)

    elif message.photo:
        file_id = message.photo[-1].file_id
        file_path = full_path + "avatar.jpg"
        photo_bool=True
        file_type="jpg"
        await message.photo[-1].download(BASE_DIR + file_path)

    elif message.document:
        if (message.document.file_size / 1024 / 1024) > 10:
            return await message.answer("Пожалуйста, загрузите файл до 10 Мб.")
        file_id = message.document.file_id
        file_type = message.document.file_name.split('.')[-1]
        file_path = full_path + f'avatar.{file_type}'
        if file_type.lower() not in PHOTO_TYPES and file_type.lower() not in VIDEO_TYPES:
            return await message.answer("Разрешенные типы данных: jpeg, webm, png, mp4, avi")
        elif file_type.lower() in PHOTO_TYPES:
            photo_bool = True
        elif file_type.lower() in VIDEO_TYPES:
            photo_bool = False
        await message.document.download(BASE_DIR + file_path)

    avatar = await models.AvatarModel.get_or_none(user=user)
    if not avatar:
        avatar = await models.AvatarModel.create(file_id=file_id,
                                                    photo_bool=photo_bool,
                                                    file_path=file_path,
                                                    file_type=file_type,
                                                    user=user)
    else:
        avatar.file_id = file_id
        avatar.photo_bool=photo_bool
        avatar.file_path=file_path
        avatar.file_type=file_type
        await avatar.save()
    await state.finish()
    old = False
    if user_data['status_user'] == 'old':
        user.verification = False
        user.last_verification_time = datetime.utcnow()
        old = True
        await user.save()
        text = "Аватар успешно изменен! Ожидайте верификации вашего профиля от администрации."
    else:
        user.end_registration = True
        user.last_verification_time = datetime.utcnow()
        await user.save()
        text = "Регистрация успешно завершена! Ожидайте верификации вашего профиля от администрации."
        await calculation_new_user(user=user)
    await send_new_registration_in_chanel(user, old=old)
    await message.answer(text, reply_markup=await main_keyboard())


# @dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'skip_ava', state=ProfileSettingsState.avatar)
# async def skip_ava_handler(call: types.CallbackQuery, state: FSMContext):
#     await state.finish()
#     # await send_new_registration_in_chanel()
#     await call.message.delete()
#     await call.message.answer("Регистрация успешно завершена! Ожидайте верификации вашего профиля от администрации.", reply_markup=await main_keyboard())


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'how_upload_document', state=ProfileSettingsState.avatar)
async def how_upload_document_handler(call: types.CallbackQuery, state: FSMContext):
    text = "Загрузи фото без потери качества по инструкции.\n\n"  \
           "<b>На android:</b>\n"  \
           "1.Нажать на значок в виде скрепки \n"  \
           '2.Перейти в раздел "Файл" \n'  \
           "3.Выбрать фото или видео и отправить.\n\n"  \
           "<b>На iOS:</b>\n"  \
           "1.Нажать на значок в виде скрепки\n"  \
           '2.Выбрать "Файл"\n'  \
           '3.Выбрать "Фото или видео"\n'  \
           "4.Выбрать фото или видео и отправить."
    await call.message.edit_text(text=text, reply_markup=await back_document_keyboard())    