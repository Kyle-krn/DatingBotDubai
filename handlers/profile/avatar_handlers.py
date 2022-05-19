from datetime import datetime
from typing import Union
from data.config import KEYBOARD_TEXT, PHOTO_TYPES, VIDEO_TYPES, BASE_DIR
from handlers.cancel_state_handler import redirect_handler
from loader import dp, bot
from models import models
from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.inline.user_settings_keyboards import avatar_keyboard, back_document_keyboard
from keyboards.reply_keyboards.keyboards import main_keyboard
from .profile_state import ProfileSettingsState
from handlers.group.new_reg_user_handlers import send_new_registration_in_chanel
from utils.calculation_relations.calculations import calculation_new_user
import os


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'send_ava')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'change_ava')
async def send_document_handler(call: Union[types.CallbackQuery, types.Message]):
    await ProfileSettingsState.avatar.set()
    state = dp.get_current().current_state()
    if isinstance(call, types.Message) or call.data.split(':')[0] == 'send_ava':
        status_user='new'
        if isinstance(call, types.Message):
            tg_id=call.chat.id
        else:
            tg_id=call.message.chat.id

        user = await models.UserModel.get(tg_id=tg_id)
        user_purp = await user.purp_dating.all()
        user_purp = [i.title_purp for i in user_purp]
        user_purp = ", ".join(user_purp)
        await state.update_data(status_user=status_user)
        if isinstance(call, types.Message):
            await call.answer(text="Пришли, пожалуйста, фото или видео☺️", reply_markup=await avatar_keyboard(status_user))
        else:
            await call.message.edit_text(text=f"Ваши цели знакомства: {user_purp}")
            await call.message.answer(text="Пришли, пожалуйста, фото или видео☺️", reply_markup=await avatar_keyboard(status_user))

        
    else:
        status_user = 'old'
        await state.update_data(status_user=status_user)
        await call.message.delete()
        await call.message.answer(text="Пришли, пожалуйста, фото или видео☺️", reply_markup=await avatar_keyboard(status_user))
    


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'back_send_ava', state=ProfileSettingsState.avatar)
async def back_send_document_handler(call: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    await call.message.edit_text(text="Пришли, пожалуйста, фото или видео☺️", reply_markup=await avatar_keyboard(user_data['status_user']))


@dp.message_handler(content_types=['document', 'photo', 'video', 'text'], state=ProfileSettingsState.avatar)
async def upload_file_handler(message: types.Message, state: FSMContext):
    user = await models.UserModel.get(tg_id=message.chat.id)
    user_data = await state.get_data()
    if message.text:
        if message.text in KEYBOARD_TEXT and user.end_registration is True:
            await state.finish()    
            return await redirect_handler(message=message, button_text=message.text)
        
        return await message.answer(text="Пришли, пожалуйста, фото или видео☺️", reply_markup=await avatar_keyboard(user_data['status_user']))
        # else:
        #     return
    
    
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
        # print(message.document)
        # return await message.answer_document()
        # file_id = message.document.file_id
        file_type = message.document.file_name.split('.')[-1]
        file_path = full_path + f'avatar.{file_type}'
        if file_type.lower() not in PHOTO_TYPES and file_type.lower() not in VIDEO_TYPES:
            return await message.answer("Разрешенные типы данных: jpeg, webm, png, mp4, avi")
        
        
        await message.document.download(BASE_DIR + file_path)
        
        if file_type.lower() in PHOTO_TYPES:
            photo_bool = True
            msg = await bot.send_photo(chat_id=390442593, photo=open(BASE_DIR + file_path, 'rb'))
            file_id = msg.photo[-1].file_id

        elif file_type.lower() in VIDEO_TYPES:
            photo_bool = False
            msg = await bot.send_video(chat_id=390442593, photo=open(BASE_DIR + file_path, 'rb'))
            file_id = message.video.file_id
    
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