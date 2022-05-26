from datetime import datetime
from models import models
from utils.zodiak import zodiac_sign


async def generate_ad_text(target_user: models.UserModel, general_percent: int) -> str:
    """Генерирует текст объявления"""
    zodiak = await zodiac_sign(target_user.birthday)
    city = await target_user.place
    marital_status = await target_user.marital_status
    # year = datetime.now().year
    age = (datetime.utcnow().date() - target_user.birthday).days / 365
    text = f"{target_user.name}, {int(age)}\n"  \
           f"{zodiak}\n" \
           f"🗺️ {city.place_name}\n" \
           f"👫 {marital_status.title_status}\n"  \
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
    # percent = relation.percent_compatibility
    if general_percent is not None:
        if general_percent > 99:
            general_percent = 99
        text += f"Процент совместимости: {general_percent}%"
    return text

