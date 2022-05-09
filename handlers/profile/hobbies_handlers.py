from loader import dp, bot
from aiogram import types
from .profile_state import ProfileSettingsState
from aiogram.dispatcher import FSMContext
from keyboards.inline.user_settings_keyboards import skip_settings_keyboard, remove_hobbie_keyboard
from models import models
from .marriage_handlers import marriage_handler
from .views_self_profile_handlers import profile_handler
from tortoise.queryset import Q
from handlers.calculation_relations.recalculation_relations import recalculation_hobbies
from tortoise import Tortoise

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == "change_hobbies")
async def set_hobbies_state(call: types.CallbackQuery):
    top_hobbies = await get_top_hobbies()
    name_top_hobbies = []
    for item in top_hobbies[:10]:
        hobbie = await models.Hobbies.get(id=item['hobbies_id'])
        name_top_hobbies.append(hobbie.title_hobbie)
    await ProfileSettingsState.hobbies.set()
    state = dp.get_current().current_state()
    text = "Перечислите ваши увлечения, или как вы любите проводить время через запятую.\n"  \
           "Или вернитесь к этому шагу позже Меню- профиль - Описание\n"  \
           "Пример наиболее частых увлечений: "
    text += ", ".join(name_top_hobbies)
    if isinstance(call, types.Message):
        msg = await call.answer(text, reply_markup=await skip_settings_keyboard(callback="skip_hobbie:"))
        status_user="new"
    else:
        status_user="old"
        await call.message.delete()
        msg = await call.message.answer(text, reply_markup=await skip_settings_keyboard(callback="skip_hobbie:"))
    await state.update_data(msg_id=msg.message_id, status_user=status_user, append_hobbie=False)


@dp.message_handler(state=ProfileSettingsState.hobbies)
async def input_hobbies_handler(message: types.Message, state: FSMContext):
    hobbies = [i.strip().capitalize() for i in message.text.split(',')]
    user_data = await state.get_data()
    print(user_data)
    # await state.finish()
    old_msg_id: types.Message = user_data['msg_id']
    user = await models.UserModel.get(tg_id=message.chat.id)
    list_hobbie = []
    for hobbie in hobbies:
        hobbie_db = await models.Hobbies.get_or_none(title_hobbie=hobbie)
        if not hobbie_db:
            hobbie_db = await models.Hobbies.create(title_hobbie=hobbie) 
        list_hobbie.append(hobbie_db)
    await bot.delete_message(chat_id=message.chat.id, message_id=old_msg_id)
    # await old_msg.delete()
    await user.hobbies.add(*list_hobbie)
    user_status = user_data['status_user']
    msg = await message.answer("Вы можете удалить хобби нажав на его название или прислать новые в том же формате, через запятую.", 
                               reply_markup=await remove_hobbie_keyboard(hobbies_list=await user.hobbies.all()))
    await state.update_data(msg_id=msg.message_id, status_user=user_data['status_user'], append_hobbie=True)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'remove_hobbie', state=ProfileSettingsState.hobbies)
async def remove_hobbie_handler(call: types.CallbackQuery):
    hobbie_id = call.data.split(':')[1]
    hobbie = await models.Hobbies.get(id=hobbie_id)
    user = await models.UserModel.get(tg_id=call.message.chat.id)
    await user.hobbies.remove(hobbie)
    await call.message.edit_text("Вы можете удалить хобби нажав на его название.", reply_markup=await remove_hobbie_keyboard(await user.hobbies.all()))


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'skip_hobbie', state=ProfileSettingsState.hobbies)
async def skip_hobbies_handler(call: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    
    await state.finish()
    if user_data['append_hobbie'] is False:
        await call.answer("Вы не указали ваши увлечения.")
    else:
        await call.answer("Успешно добавлено!")

    if user_data['status_user'] == 'new':
        await marriage_handler(call)
    else:
        if user_data['append_hobbie'] is True:
            user = await models.UserModel.get(tg_id=call.message.chat.id)
            await recalculation_hobbies(user=user)
        await call.message.delete()
        return await profile_handler(call.message)


async def get_top_hobbies():
    conn = Tortoise.get_connection("default")
    sql = "SELECT hobbies_id, COUNT(*) " \
          "FROM users_hobbies " \
          "GROUP BY hobbies_id " \
          "order by count desc;"
    top_hobbies = await conn.execute_query_dict(sql)
    return top_hobbies
