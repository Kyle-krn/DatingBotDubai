from datetime import datetime
from models import models
from tortoise.queryset import Q

from utils.zodiak import zodiac_sign


async def generate_ad_text(target_user: models.UserModel, relation):
    zodiak = await zodiac_sign(target_user.birthday)

    year = datetime.now().year
    text = f"{target_user.name}, {year-target_user.birthday.year}\n"  \
           f"{zodiak}\n" \
           f"🗺️ {target_user.place}\n" \
           f"👫 {target_user.marital_status}\n"  \
           f"Дети: "
    if target_user.children is True:
        text += "Есть\n"
    elif target_user.children is False:
        text += "Нет\n"
    elif target_user.children is None:
        text += "Не скажу\n"
    if target_user.children_age != []:
        text += "Возраст детей: " + ", ".join([str(i)+" г." for i in target_user.children_age]) + "\n"
    target_hobbies = await target_user.hobbies.all()
    if target_hobbies:
        text += "Увлечения: " + ", ".join([i.title_hobbie for i in target_hobbies]) + "\n"
    # relation = await user_view.relation
    text += f"Процент совместимости: {relation.percent_compatibility}%"
    return text


# async def 