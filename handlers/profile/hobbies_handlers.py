from loader import dp
from aiogram import types
from .profile_state import ProfileSettingsState
from aiogram.dispatcher import FSMContext
from keyboards.inline.user_settings_keyboards import skip_settings_keyboard, remove_hobbie_keyboard
from models import models
from .marriage_handlers import marriage_handler
from .views_self_profile_handlers import profile_handler

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == "change_hobbies")
async def set_hobbies_state(call: types.CallbackQuery):
    await ProfileSettingsState.hobbies.set()
    state = dp.get_current().current_state()
    text = "Перечислите ваши увлечения, или как вы любите проводить время через запятую.\n"  \
           "Или вернитесь к этому шагу позже Меню- профиль - Описание\n"  \
           "Пример наиболее частых увлечений: выводим самые популярные ответы и процент пользователей 10 ответов"
    if isinstance(call, types.Message):
        msg = await call.answer(text, reply_markup=await skip_settings_keyboard(callback="skip_hobbie:"))
        status_user="new"
    else:
        status_user="old"
        print('here')
        await call.message.delete()
        msg = await call.message.answer(text, reply_markup=await skip_settings_keyboard(callback="skip_hobbie:"))
    await state.update_data(msg=msg, status_user=status_user, append_hobbie=False)

@dp.message_handler(state=ProfileSettingsState.hobbies)
async def input_hobbies_handler(message: types.Message, state: FSMContext):
    hobbies = [i.strip().capitalize() for i in message.text.split(',')]
    user_data = await state.get_data()
    old_msg: types.Message = user_data['msg']
    user = await models.UserModel.get(tg_id=message.chat.id)
    list_hobbie = []
    for hobbie in hobbies:
        hobbie_db = await models.Hobbies.get_or_none(title_hobbie=hobbie)
        if not hobbie_db:
            hobbie_db = await models.Hobbies.create(title_hobbie=hobbie) 
        # hobbie = await Hobbies.create()
        list_hobbie.append(hobbie_db)
    
    # await old_msg.edit_reply_markup(reply_markup=None)
    await old_msg.delete()
    await user.hobbies.add(*list_hobbie)
    # await state.finish()
    user_status = user_data['status_user']

    msg = await message.answer("Вы можете удалить хобби нажав на его название или прислать новые в том же формате, через запятую.", 
                               reply_markup=await remove_hobbie_keyboard(hobbies_list=await user.hobbies.all()))
    # if user_data[]
    await state.update_data(msg=msg, status_user=user_data['status_user'], append_hobbie=True)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'remove_hobbie', state=ProfileSettingsState.hobbies)
async def remove_hobbie_handler(call: types.CallbackQuery):
    hobbie_id = call.data.split(':')[1]
    hobbie = await models.Hobbies.get(id=hobbie_id)
    user = await models.UserModel.get(tg_id=call.message.chat.id)
    await user.hobbies.remove(hobbie)
    await call.message.edit_text("Вы можете удалить хобби нажав на его название.", reply_markup=await remove_hobbie_keyboard(await user.hobbies.all()))



# @dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'add_hobbie')
# async def add_hobbie_handler(call: types.CallbackQuery):
#     await ProfileSettingsState.hobbies.set()
#     text = "Перечислите ваши увлечения, или как вы любите проводить время через запятую.\n"  \
#            "Или вернитесь к этому шагу позже Меню- профиль - Описание\n"  \
#            "Пример наиболее частых увлечений: выводим самые популярные ответы и процент пользователей 10 ответов"
#     msg = await call.message.edit_text(text, reply_markup=await skip_settings_keyboard(callback="skip_hobbie:"))
#     state = dp.get_current().current_state()
#     await state.update_data(msg=msg)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'skip_hobbie', state=ProfileSettingsState.hobbies)
async def skip_hobbies_handler(call: types.CallbackQuery, state: FSMContext):
    # if call.data.split(':')[0] == 'skip_hobbie':
    user_data = await state.get_data()
    await state.finish()
    if user_data['append_hobbie'] is False:
        await call.answer("Вы не указали ваши увлечения.")
    else:
        
        await call.answer("Успешно добавлено!")
    if user_data['status_user'] == 'new':
        await marriage_handler(call)
    else:
        await call.message.delete()
        return await profile_handler(call.message)