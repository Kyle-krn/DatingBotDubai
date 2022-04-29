from datetime import datetime, date
from fileinput import hook_encoded
from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from models.models import AvatarModel, PurposeOfDating, UserModel, DatingInterestPlace, Hobbies
from loader import dp
from keyboards.inline.user_settings_keyboards import (gender_keyboard, city_answer_keyboard, dubai_answer_keyboard, companion_dubai_keyboard, skip_settings_keyboard,
                                                     remove_hobbie_keyboard, marital_status_keyboard, children_keyboard, purp_keyboard, avatar_keyboard, back_document_keyboard)
from keyboards.reply_keyboards.keyboards import geolocation_keyboard
from aiogram.dispatcher.filters.state import State, StatesGroup
from utils.utils_map import get_location_by_city, get_location_by_lat_long
from aiogram.dispatcher import FSMContext
import os

from handlers.group.new_reg_user_handlers import send_new_registration_in_chanel

class ProfileSettingsState(StatesGroup):
    city = State()
    bday = State()
    hobbies = State()
    children = State()
    avatar = State()


@dp.message_handler(commands=['user'])
async def test_group(message: types.Message):
    # user = await UserModel.get_or_none(id=49)
    # user = await UserModel.get_or_none(id=58)
    for user in await UserModel.all():
        await send_new_registration_in_chanel(user)


@dp.message_handler(commands=['test'])
async def test_group(message: types.Message):
    user = await UserModel.get_or_none(id=44)
    print(await user.user_view.filter(relation__percent_compatibility__gt=0))
    # user = await UserModel.get_or_none(id=58)
    # for user in await UserModel.all():
    #     await send_new_registration_in_chanel(user)

@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    user = await UserModel.get_or_none(tg_id=message.chat.id)
    # await send_new_registration_in_chanel(user)
    if user:
        await user.delete()
        user = None
    if not user:
        user = await UserModel.create(tg_id=message.chat.id,
                                      tg_username=message.chat.username,
                                      name=message.chat.full_name)
        await message.answer(f"Укажите Ваш пол:", reply_markup=await gender_keyboard())


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'gender')
async def gender_handler(call: types.CallbackQuery):
    user = await UserModel.get(tg_id=call.message.chat.id)
    gender = call.data.split(':')[1]
    if gender == 'male':
        user.male = True
        await call.answer("Вы выбрали: Мужчина")
    else:
        user.male = False
        await call.answer("Вы выбрали: Женщина")
    await user.save()
    await call.message.delete()
    await ProfileSettingsState.city.set()
    await call.message.answer(text="Введите ваш город", reply_markup=await geolocation_keyboard())


@dp.message_handler(state=ProfileSettingsState.city)
async def city_handler(message: types.Message, state: FSMContext):
    city = message.text
    city_info, geolocation, tmz= await get_location_by_city(city)
    if not city_info:
        await message.answer("Такой город не найден, попробуйте снова или отправьте геолокацию по кнопке ниже.")
    else:
        state = dp.get_current().current_state()
        await state.update_data(city_info=city_info, geolocation=geolocation, tmz=tmz)
        await message.answer(f"Ваш город {city_info}?", reply_markup=await city_answer_keyboard())


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'city', state=ProfileSettingsState.city)
async def answer_city_handler(call: types.CallbackQuery, state: FSMContext):
    answer = call.data.split(':')[1]
    if answer == 'yes':
        user_data = await state.get_data()
        user = await UserModel.get(tg_id=call.message.chat.id)
        user.place = user_data['city_info']
        user.lat = user_data['geolocation'][1]
        user.long = user_data['geolocation'][0]
        user.tmz = user_data['tmz']
        await call.answer(f"Ваш город: {user.place}")
        await user.save()
        await state.finish()
        await call.message.delete()
        msg = await call.message.answer("Загрузка ⏳", reply_markup=types.ReplyKeyboardRemove())
        await msg.delete()
        if not 'Dubai' in user.place:
            return await call.message.answer("Планируете переезд в Дубаи?", reply_markup=await dubai_answer_keyboard())
        else:
            user.dubai = True
            await user.save()
            return await call.message.answer("Укажите с кем вы заинтересованы в знакомствах?", reply_markup=await companion_dubai_keyboard(user))
    elif answer == 'no':
        await call.message.edit_text(text="Попробуйте снова", reply_markup=None)


@dp.message_handler(content_types=['location'], state=ProfileSettingsState.city)
async def geolocation_handler(message: types.Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude
    city_info, geolocation, tmz = await get_location_by_lat_long(lat=lat, long=lon)
    if not city_info:
        return await message.answer("К сожалению мы не смогли определить ваш город, напиши его текстом.")
    
    user = await UserModel.get(tg_id=message.chat.id)
    user.place = city_info
    user.lat = geolocation[0]
    user.long = geolocation[1]
    user.tmz = tmz
    await user.save()
    await state.finish()
    msg = await message.answer("Загрузка ⏳", reply_markup=types.ReplyKeyboardRemove())
    await msg.delete()
    if not 'Dubai' in user.place:
        return await message.answer("Планируете переезд в Дубаи?", reply_markup=await dubai_answer_keyboard())
    else:
        user.dubai = True
        await user.save()
        return await message.answer("Укажите с кем вы заинтересованы в знакомствах?", reply_markup=await companion_dubai_keyboard(user))



@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'remove_dubai')
async def remove_dubai_handler(call: types.CallbackQuery):
    user = await UserModel.get(tg_id=call.message.chat.id)
    answer = call.data.split(':')[1]
    if answer == 'yes':
        user.moving_to_dubai = True
        await call.answer("Планируете переезд в Дубаи")
    elif answer == 'no':
        user.moving_to_dubai = False
        await call.answer("Не планируете переезд в Дубаи")
    await user.save()
    await call.message.edit_text("Укажите с кем вы заинтересованы в знакомствах?", reply_markup=await companion_dubai_keyboard(user))


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'companion_dubai')
async def add_companion_dubai_interest(call: types.CallbackQuery):
    user = await UserModel.get(tg_id=call.message.chat.id)
    user_interest = await user.interest_place_companion.all()
    interest_id = call.data.split(':')[1]
    selected_interest = await DatingInterestPlace.get(id=interest_id)
    if selected_interest in user_interest:
        await user.interest_place_companion.remove(selected_interest)
    else:
        await user.interest_place_companion.add(selected_interest)
    await call.message.edit_text("Укажите с кем вы заинтересованы в знакомствах?", reply_markup=await companion_dubai_keyboard(user))



@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'bday')
async def birthday_handler(call: types.CallbackQuery):
    await ProfileSettingsState.bday.set()
    await call.message.delete()
    await call.message.answer("Укажи свою дату рождения в формате DD.MM.YYYY, например 23.05.1996")


@dp.message_handler(state=ProfileSettingsState.bday)
# @dp.message_handler(lambda message: True)
async def input_bday_handler(message: types.Message, state: FSMContext):
    try:
        bday = datetime.strptime(message.text, '%d.%m.%Y').date()
    except ValueError:
        return await message.answer("<b>Не верный формат!</b>\n\nУкажи свою дату рождения в формате DD.MM.YYYY, например 23.05.1996")
    today = date.today()
    age = int((today - bday).total_seconds() / 60 / 60 / 24 / 365)
    if (18 < age < 100) is False:
        return await message.answer("Обращаем ваше внимание: использование сервиса Zodier запрещено лицам, моложе 18 лет! Возможно, вы ошиблись! Укажите свою дату рождения в формате DD.MM.YYYY, например 23.07.1996")
    user = await UserModel.get(tg_id=message.chat.id)
    user.birthday = bday
    await user.save()
    await ProfileSettingsState.hobbies.set()
    text = "Перечислите ваши увлечения, или как вы любите проводить время через запятую.\n"  \
           "Или вернитесь к этому шагу позже Меню- профиль - Описание\n"  \
           "Пример наиболее частых увлечений: выводим самые популярные ответы и процент пользователей 10 ответов"
    msg = await message.answer(text, reply_markup=await skip_settings_keyboard(callback="skip_hobbies:"))
    state = dp.get_current().current_state()
    await state.update_data(msg=msg)



@dp.message_handler(state=ProfileSettingsState.hobbies)
# @dp.message_handler(lambda message: True)
async def input_hobbies_handler(message: types.Message, state: FSMContext):
    hobbies = [i.strip().capitalize() for i in message.text.split(',')]
    user_data = await state.get_data()
    old_msg: types.Message = user_data['msg']
    user = await UserModel.get(tg_id=message.chat.id)
    list_hobbie = []
    for hobbie in hobbies:
        hobbie_db = await Hobbies.get_or_none(title_hobbie=hobbie)
        if not hobbie_db:
            hobbie_db = await Hobbies.create(title_hobbie=hobbie) 
        # hobbie = await Hobbies.create()
        list_hobbie.append(hobbie_db)
    await old_msg.edit_reply_markup(reply_markup=None)
    await user.hobbies.add(*list_hobbie)
    await state.finish()
    await message.answer("Вы можете удалить хобби нажав на его название.", reply_markup=await remove_hobbie_keyboard(await user.hobbies.all()))
    


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'remove_hobbie')
async def remove_hobbie_handler(call: types.CallbackQuery):
    hobbie_id = call.data.split(':')[1]
    hobbie = await Hobbies.get(id=hobbie_id)
    user = await UserModel.get(tg_id=call.message.chat.id)
    await user.hobbies.remove(hobbie)
    await call.message.edit_text("Вы можете удалить хобби нажав на его название.", reply_markup=await remove_hobbie_keyboard(await user.hobbies.all()))



@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'add_hobbie')
async def add_hobbie_handler(call: types.CallbackQuery):
    await ProfileSettingsState.hobbies.set()
    text = "Перечислите ваши увлечения, или как вы любите проводить время через запятую.\n"  \
           "Или вернитесь к этому шагу позже Меню- профиль - Описание\n"  \
           "Пример наиболее частых увлечений: выводим самые популярные ответы и процент пользователей 10 ответов"
    msg = await call.message.edit_text(text, reply_markup=await skip_settings_keyboard(callback="skip_hobbies:"))
    state = dp.get_current().current_state()
    await state.update_data(msg=msg)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'skip_hobbies', state=ProfileSettingsState.hobbies)
async def skip_hobbies_handler(call: types.CallbackQuery, state: FSMContext):
    await call.answer("Вы не указали ваши увлечения.")
    await state.finish()
    await marriage_handler(call)

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'marriage')
async def marriage_handler(call: types.CallbackQuery):
    await call.message.edit_text(text='Ваше семейное положение?', reply_markup=await marital_status_keyboard())




@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'ms')
async def mar_status_handler(call: types.CallbackQuery):
    status = call.data.split(':')[1]
    await call.answer(f"Ваше семейное положение: {status}")
    user = await UserModel.get(tg_id=call.message.chat.id)
    user.marital_status = status
    await user.save()
    await call.message.edit_text(text="У вас есть дети? Информация будет использоваться для поиска более подходящих вам знакомств.", 
                                 reply_markup=await children_keyboard())




@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'children')
async def children_handler(call: types.CallbackQuery):
    answer = call.data.split(':')[1]
    user = await UserModel.get(tg_id=call.message.chat.id)
    user.children = True
    await user.save()
    # if answer == 'yes':
    await ProfileSettingsState.children.set()
    text = "Сколько лет вашим детям (если не хотите отвечать проставьте 0).\n"  \
            "Укажите количество лет для каждого ребенка через запятую."  \
            "Информация будет использоваться для поиска более подходящих вам знакомств."
    await call.message.edit_text(text=text)
    # else:



    # user = await UserModel.get(tg_id=call.message.chat.id)


@dp.message_handler(state=ProfileSettingsState.children)
async def children_state_handler(message: types.Message, state: FSMContext):
    user = await UserModel.get(tg_id=message.chat.id)
    if message.text.isdigit() and int(message.text) == 0:
        pass
    else:
        children_list = [i.strip() for i in message.text.split(',')]
        
        try:
            children_list = [int(i) for i in children_list]
        except (ValueError, TypeError):
            text = "Сколько лет вашим детям (если не хотите отвечать проставьте 0).\n"  \
               "Укажите количество лет для каждого ребенка через запятую."  \
               "Информация будет использоваться для поиска более подходящих вам знакомств."
            return await message.answer(text=text)
        
        
        user.children_age = children_list
        await user.save()
    await state.finish()
    await message.answer('Выберите цели знакомства', reply_markup=await purp_keyboard(await user.purp_dating.all()))


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'purp')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'skip_children')
async def purp_handler(call: types.CallbackQuery):
    user = await UserModel.get(tg_id=call.message.chat.id)
    if call.data.split(':')[0] == 'purp':
        purp_id = int(call.data.split(':')[1]) 
        purp = await PurposeOfDating.get(id=purp_id)
        
        if purp in await user.purp_dating.all():
            await user.purp_dating.remove(purp)
        else:
            await user.purp_dating.add(purp)
    if call.data.split(':')[0] == 'skip_children':
        if call.data.split(':')[1] == 'no':
            user.children = False
            await call.answer("Вы выбрали: Нет детей")
        else:
            user.children = None
            await call.answer("Вы выбрали: Не скажу")
        await user.save()
    await call.message.edit_text('Выберите цели знакомства', reply_markup=await purp_keyboard(await user.purp_dating.all()))



@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'send_ava')
async def send_document_handler(call: types.CallbackQuery):
    await ProfileSettingsState.avatar.set()
    await call.message.edit_text(text="Пришли, пожалуйста, фото или видео☺️", reply_markup=await avatar_keyboard())



@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'back_send_ava', state=ProfileSettingsState.avatar)
async def back_send_document_handler(call: types.CallbackQuery):
    await call.message.edit_text(text="Пришли, пожалуйста, фото или видео☺️", reply_markup=await avatar_keyboard())



@dp.message_handler(content_types=['document', 'photo', 'video'], state=ProfileSettingsState.avatar)
# @dp.message_handler(content_types=['document', 'photo', 'video'])
async def upload_file_handler(message: types.Message, state: FSMContext):
    user = await UserModel.get(tg_id=message.chat.id)
    # user = await UserModel.get(id=53)
    # print(await user.avatar.delete())
    if await user.avatar:
        await user.avatar.delete()
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
        await message.video.download(file_path)
        avatar = await AvatarModel.create(file_id=file_id,
                                          photo_bool=False,
                                          file_path=file_path,
                                          file_type=file_type)
    elif message.photo:
        # print(message.photo)
        file_id = message.photo[-1].file_id
        file_path = full_path + "avatar.jpg"
        await message.photo[-1].download(file_path)
        await message.answer_photo(photo=file_id)
        avatar = await AvatarModel.create(file_id=file_id, 
                                          photo_bool=True,
                                          file_path=file_path, 
                                          file_type="jpg")
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
        avatar = await AvatarModel.create(file_id=file_id,
                                          photo_bool=photo_bool,
                                          file_path=file_path, 
                                          file_type=file_type)
    user.avatar = avatar
    await user.save()
    await state.finish()
    await send_new_registration_in_chanel(user)
    await message.answer("Регистрация успешно завершена! Ожидайте верификации вашего профиля от администрации.")



@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'skip_ava', state=ProfileSettingsState.avatar)
async def skip_ava_handler(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    # await send_new_registration_in_chanel()
    await call.message.edit_text("Регистрация успешно завершена! Ожидайте верификации вашего профиля от администрации.")

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'how_upload_document', state=ProfileSettingsState.avatar)
async def how_upload_document_handler(call: types.CallbackQuery):
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
        

