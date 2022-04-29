from loader import dp
from aiogram import types
from models import models
from datetime import datetime, date
from tortoise.queryset import Q

@dp.message_handler(commands=['dating'])
async def search_dating(message: types.Message):
    photo_types = ('jpeg', 'jpg', "webm", "png")
    video_types = ("mp4", "avi")

    user = await models.UserModel.get(tg_id=message.chat.id)
    user_view = (await user.user_view.filter(Q(relation__percent_compatibility__gt=0) & Q(target_user__verification=True)).order_by('count_view').limit(1))[0]
    # print(user_view)
    user_view = (await user.user_view.filter(relation__percent_compatibility__gt=0).order_by('count_view').limit(1))[0]
    target_user = await user_view.target_user
    avatar = await target_user.avatar
    zodiak = await zodiac_sign(target_user.birthday)
    print(await target_user.interest_place_companion.all())
    print(await user.interest_place_companion.all())
    year = datetime.now().year
    text = f"{target_user.name}, {year-target_user.birthday.year}\n"  \
           f"{zodiak}\n" \
           f"🗺️ {target_user.place}\n" \
           f"👫 {target_user.marital_status}\n"  \
           f""
           
    
    if avatar.file_type.lower() in photo_types:
        await message.answer_photo(photo=avatar.file_id, caption=text) 
    elif avatar.file_type.lower() in video_types:
        pass
    


@dp.message_handler(commands=['znak'])
async def znak_hand(message: types.Message):
    user = await models.UserModel.get(tg_id=message.chat.id)
    print(type(user.birthday))

    # for i in range(1, 13):
        # print(i)
    x = await zodiac_sign(date(month=2, day=1, year=1996))
    print(x)


async def zodiac_sign(bday: date):
    if date(month=3, day=21, year=bday.year) <= bday <= date(month=4, day=19, year=bday.year):
        return "♈ Овен"
    
    elif date(month=4, day=20, year=bday.year) <= bday <= date(month=5, day=20, year=bday.year):
        return "♉ Телец"
    
    elif date(month=5, day=21, year=bday.year) <= bday <= date(month=6, day=19, year=bday.year):
        return "♊ Близнецы"
    
    elif date(month=6, day=21, year=bday.year) <= bday <= date(month=7, day=22, year=bday.year):
        return "♋ Рак"
    
    elif date(month=7, day=23, year=bday.year) <= bday <= date(month=8, day=22, year=bday.year):
        return "♌ Лев"
    
    elif date(month=8, day=23, year=bday.year) <= bday <= date(month=9, day=22, year=bday.year):
        return "♍ Дева"
    
    elif date(month=9, day=23, year=bday.year) <= bday <= date(month=10, day=22, year=bday.year):
        return "♎ Весы"
    
    elif date(month=10, day=23, year=bday.year) <= bday <= date(month=11, day=21, year=bday.year):
        return "♏ Скорпион"
    
    elif date(month=11, day=22, year=bday.year) <= bday <= date(month=12, day=21, year=bday.year):
        return "♐ Стрелец"
    
    elif (date(month=12, day=22, year=bday.year) <= bday <= date(month=1, day=19, year=bday.year+1)) or  \
         (date(month=12, day=22, year=bday.year-1) <= bday <= date(month=1, day=19, year=bday.year)):
        return "♑ Козерог"
    
    elif date(month=1, day=20, year=bday.year) <= bday <= date(month=2, day=18, year=bday.year):
        return "♒ Водолей"
    
    elif date(month=2, day=19, year=bday.year) <= bday <= date(month=3, day=20, year=bday.year):
        return "♓ Рыбы"
    
    