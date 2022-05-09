from datetime import datetime
from keyboards.inline.inline_keyboards import verification_keyboards
from models import models
from loader import bot
from loader import dp
from aiogram import types
from handlers.calculation_relations.relations_handlers import calculation_2_user
from tortoise.queryset import Q

async def send_new_registration_in_chanel(user: models.UserModel, old: bool = False):
    avatar = await user.avatar
    photo_types = ('jpeg', 'jpg', "webm", "png")
    video_types = ("mp4", "avi")
    # print(avatar.file_type.lower())
    text = ""
    if old:
        text += f"<b>Новая фотография у пользвателя #{user.id}</b>\n\n"
    text += f"<b>ID</b> - {user.tg_id}\n"  \
           f"<b>Username</b> - {user.tg_username}\n"  \
           f"<b>Full name</b> - {user.name}\n"  \
           f"<b>Gender</b> - "
    if user.male:
        text += "Male\n"
    else:
        text += "Female\n"
    text += f"<b>Place</b> - {user.place}\n"  \
            f"<b>Lat, Lon</b> - {user.lat}, {user.long}\n"  \
            f"<b>Moving in Dubai</b> - {user.moving_to_dubai}\n"  \
            f"<b>Bday</b> - {user.birthday}\n"  \
            f"<b>Companion place</b> - "  
    text += ", ".join([i.title_interest for i in await user.interest_place_companion.all()]) + "\n"
    text += f"<b>Hobbies</b> - "
    text += ", ".join([i.title_hobbie for i in await user.hobbies.all()]) + "\n"
    text += f"<b>TMZ</b> - {user.tmz}\n" \
            f"<b>Children</b> - "
    if user.children is True:
        text += "Have\n"
    if user.children is False:
        text += "No have\n"
    if user.children is None:
        text += "Not say\n"
    text += "<b>Age children</b> - "
    text += ", ".join([str(i) for i in user.children_age]) + "\n"
    text += f"<b>Marital status</b> - {user.marital_status}\n"
    text += "<b>Purp dating</b> - "
    text += ", ".join([i.title_purp for i in await user.purp_dating.all()]) + "\n"
    # text += f"<b>Search radius</b> - {user.search_radius} km"
    if avatar:
        if avatar.file_type.lower() in photo_types:
            await bot.send_photo(-1001732505124, photo=avatar.file_id, caption=text, reply_markup=await verification_keyboards(user.id))
        elif avatar.file_type.lower() in video_types:
            await bot.send_video(-1001732505124, video=avatar.file_id, caption=text, reply_markup=await verification_keyboards(user.id))
    else: 
        await bot.send_photo(-1001732505124, photo="https://www.etexstore.com/wp-content/plugins/all-in-one-seo-pack/images/default-user-image.png", caption=text, reply_markup=await verification_keyboards(user.id))


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'verification')
async def verification_user(call: types.CallbackQuery):
    user_id = int(call.data.split(':')[1])
    answer = call.data.split(':')[2]
    user = await models.UserModel.get(id=user_id)
    user.verification = True
    await user.save()
    await call.answer("Одобренно")
    await call.message.edit_reply_markup(reply_markup=None)
    await calculation_new_user(user)


async def calculation_new_user(user: models.UserModel):
    verification_user_list = await models.UserModel.filter(Q(ban=False)).exclude(id=user.id)
    # print(verification_user_list)
    purp_friend = await models.PurposeOfDating.get(id=1)
    purp_sex = await models.PurposeOfDating.get(id=2)
    purp_user = await user.purp_dating.all()
    year_now = datetime.now().year
    old_user = year_now - user.birthday.year
    hobbies_user = await user.hobbies.all()
    interest_place_user = await user.interest_place_companion.all()
    interest_place_4 = await models.DatingInterestPlace.get(id=1)
    interest_place_5 = await models.DatingInterestPlace.get(id=2)
    interest_place_6 = await models.DatingInterestPlace.get(id=3)
    for target_user in verification_user_list:
        percent, percent_age, percent_children, percent_hobbies, result_distance_check, result_purp_check, result_gender_check = await calculation_2_user(user=user,
                                                                                                                                     target_user=target_user,
                                                                                                                                     purp_friend=purp_friend,
                                                                                                                                     purp_sex=purp_sex,
                                                                                                                                     purp_user=purp_user,
                                                                                                                                     hobbies_user=hobbies_user,
                                                                                                                                     interest_place_user=interest_place_user,
                                                                                                                                     interest_place_4=interest_place_4, 
                                                                                                                                     interest_place_5=interest_place_5, 
                                                                                                                                     interest_place_6=interest_place_6,
                                                                                                                                     old_user=old_user)
        print(percent, percent_age, percent_children, percent_hobbies, result_distance_check, result_purp_check, result_gender_check)
        print(f"User {user.tg_username} -> User {target_user.tg_username} = {percent}%")
        relation = await models.UsersRelations.get_or_none(Q(Q(user=user) & Q(target_user=target_user)) | Q(Q(target_user=user) & Q(user=target_user)))
        if not relation:
            relation = await models.UsersRelations.create(user=user, 
                                                        target_user=target_user, 
                                                        percent_compatibility=percent, 
                                                        percent=percent,
                                                        percent_age=percent_age,
                                                        percent_children=percent_children,
                                                        percent_hobbies=percent_hobbies,
                                                        result_distance_check=result_distance_check, 
                                                        result_purp_check=result_purp_check,
                                                        result_gender_check=result_gender_check)
        if percent > 0:
            await models.UserView.get_or_create(user=user, target_user=target_user, relation=relation)
            await models.UserView.get_or_create(user=target_user, target_user=user, relation=relation)
    print('\n')