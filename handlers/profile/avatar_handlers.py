from loader import dp
from models import models
from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.inline.user_settings_keyboards import avatar_keyboard, back_document_keyboard
from keyboards.reply_keyboards.keyboards import main_keyboard
from .profile_state import ProfileSettingsState
from handlers.group.new_reg_user_handlers import send_new_registration_in_chanel
import os


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'send_ava')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'change_ava')
async def send_document_handler(call: types.CallbackQuery):
    await ProfileSettingsState.avatar.set()
    state = dp.get_current().current_state()
    if call.data.split(':')[0] == 'send_ava':
        await state.update_data(status_user='new')
        await call.message.edit_text(text="Пришли, пожалуйста, фото или видео☺️", reply_markup=await avatar_keyboard())
    else:
        await state.update_data(status_user='old')
        await call.message.delete()
        await call.message.answer(text="Пришли, пожалуйста, фото или видео☺️", reply_markup=await avatar_keyboard())
    


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'back_send_ava', state=ProfileSettingsState.avatar)
async def back_send_document_handler(call: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    print(user_data)
    await call.message.edit_text(text="Пришли, пожалуйста, фото или видео☺️", reply_markup=await avatar_keyboard())


@dp.message_handler(content_types=['document', 'photo', 'video'], state=ProfileSettingsState.avatar)
async def upload_file_handler(message: types.Message, state: FSMContext):
    user = await models.UserModel.get(tg_id=message.chat.id)
    user_data = await state.get_data()
    # print(await user.avatar)
    # if await user.avatar:
    #     await user.avatar.delete()
    static_path = "static/"
    folder_path = f'avatar_telegram/{user.id}/'
    full_path = static_path + folder_path
    if os.path.exists(full_path) is False:
        os.mkdir(full_path)

    if message.video:
        if (message.video.file_size / 1024 / 1024) > 10:
            return await message.answer("Пожалуйста, загрузите файл до 10 Мб.")
        file_id = message.video.file_id
        file_type = message.video.file_name.split('.')[-1]
        file_path = full_path + f'avatar.{file_type}'
        photo_bool=False
        await message.video.download(file_path)
        # avatar = await models.AvatarModel.get_or_none(user=user)
        # if not avatar:
        #     avatar = await models.AvatarModel.create(file_id=file_id,
        #                                              photo_bool=False,
        #                                              file_path=file_path,
        #                                              file_type=file_type,
        #                                              user=user)
        # else:
        #     avatar.file_id = file_id
        #     avatar.photo_bool=False
        #     avatar.file_path=file_path
        #     avatar.file_type=file_type
        #     await avatar.save()

    elif message.photo:
        file_id = message.photo[-1].file_id
        file_path = full_path + "avatar.jpg"
        photo_bool=True
        file_type="jpg"
        await message.photo[-1].download(file_path)
        await message.answer_photo(photo=file_id)
        # avatar = await models.AvatarModel.create(file_id=file_id, 
        #                                   photo_bool=True,
        #                                   file_path=file_path, 
        #                                   file_type="jpg",
        #                                   user=user)
    elif message.document:
        if (message.document.file_size / 1024 / 1024) > 10:
            return await message.answer("Пожалуйста, загрузите файл до 10 Мб.")
        file_id = message.document.file_id
        file_type = message.document.file_name.split('.')[-1]
        file_path = full_path + f'avatar.{file_type}'
        photo_types = ('jpeg', "webm", "png")
        video_types = ("mp4", "avi")
        if file_type.islower() not in photo_types + video_types:
            return await message.answer("Разрешенные типы данных: jpeg, webm, png, mp4, avi")
        elif file_type.islower() in photo_types:
            photo_bool = True
        elif file_type.islower() in video_types:
            photo_bool = False
        await message.document.download(file_path)
        # avatar = await models.AvatarModel.create(file_id=file_id,
        #                                   photo_bool=photo_bool,
        #                                   file_path=file_path, 
        #                                   file_type=file_type,
        #                                   user=user)
    # user.avatar = avatar
    # await user.save()
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
        old = True
        await user.save()
        text = "Аватар успешно изменен! Ожидайте верификации вашего профиля от администрации."
    else:
        user.end_registration = True
        await user.save()
        text = "Регистрация успешно завершена! Ожидайте верификации вашего профиля от администрации."
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