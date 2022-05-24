from data.config import PHOTO_TYPES, VIDEO_TYPES
from models import models
from loader import bot


async def send_new_registration_in_chanel(user: models.UserModel, old: bool = False):
    avatar = await user.avatar
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
    user_place = await user.place
    text += f"<b>Place</b> - {user_place.place_name}\n"  \
            f"<b>Moving in Dubai</b> - {user.moving_to_dubai}\n"  \
            f"<b>Bday</b> - {user.birthday}\n"  \
            f"<b>Companion place</b> - "  
    text += ", ".join([i.title_interest for i in await user.interest_place_companion.all()]) + "\n"
    text += f"<b>Hobbies</b> - "
    text += ", ".join([i.title_hobbie for i in await user.hobbies.all()]) + "\n"
    text += f"<b>TMZ</b> - {user_place.tmz}\n" \
            f"<b>Children</b> - "
    if user.children is True:
        text += "Have\n"
    if user.children is False:
        text += "No have\n"
    if user.children is None:
        text += "Not say\n"
    text += "<b>Age children</b> - "
    text += ", ".join([str(i) for i in user.children_age]) + "\n"
    marital_status = await user.marital_status
    text += f"<b>Marital status</b> - {marital_status.title_status}\n"
    text += "<b>Purp dating</b> - "
    text += ", ".join([i.title_purp for i in await user.purp_dating.all()]) + "\n"
    # text += f"<b>Search radius</b> - {user.search_radius} km"
    if avatar:
        if avatar.file_type.lower() in PHOTO_TYPES:
            await bot.send_photo(-1001732505124, photo=avatar.file_id, caption=text)
        elif avatar.file_type.lower() in VIDEO_TYPES:
            await bot.send_video(-1001732505124, video=avatar.file_id, caption=text)
    else: 
        await bot.send_photo(-1001732505124, photo="https://www.etexstore.com/wp-content/plugins/all-in-one-seo-pack/images/default-user-image.png", caption=text)

