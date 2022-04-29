from typing import List
from data.config import TORTOISE_ORM
from tortoise import Tortoise, run_async
from models import models
import random
import requests
from pprint import PrettyPrinter
from utils.utils_map import get_location_by_city
pp = PrettyPrinter(indent=4)
import math
from geopy.distance import geodesic
from datetime import date, datetime
from tortoise.queryset import Q

location_list = ['Чебоксары', "Новочебоксраск", "Казань", "Ульяновск"]

async def up_user_db():
    await Tortoise.init(TORTOISE_ORM)
    dating_place = await models.DatingInterestPlace.all()
    print(dating_place[0])
    tg_id = random.randint(100000, 99999999999)
    r = requests.get('https://randomuser.me/api/')
    x = r.json()
    username = x['results'][0]['login']['username']
    male = bool(random.getrandbits(1))
    location, coord, tmz = await get_location_by_city(random.choice(location_list))
    moving_to_dabai = bool(random.getrandbits(1))


async def create_relation(user: models.UserModel, target_user: models.UserModel, percent: int, relation: models.UsersRelations = None):
    if relation is None:
        relation = await models.UsersRelations.create(user=user, target_user=target_user, percent_compatibility=percent)
    else:
        if relation.percent_compatibility != percent:
            relation.percent_compatibility = percent
            await relation.save()

    if percent > 0:
        await models.UserView.get_or_create(user=user, target_user=target_user, relation=relation)
        await models.UserView.get_or_create(user=target_user, target_user=user, relation=relation)
        # await models.UserView.get
    


# Дубаи                                                             1
# не Дубаи (планирую переезд)                                       2
# не Дубаи (НЕ планирую переезд)                                    3




# 1 - Находится в Дубае                                             4
# 2 - Планирует переезд в Дубай                                     5
# 3 - Не в дубае и не планирует туда переезд                        6


async def calculation_2_user(user: models.UserModel, 
                             target_user: models.UserModel,
                             purp_friend: models.PurposeOfDating,
                             purp_sex: models.PurposeOfDating,
                             purp_user: List[models.PurposeOfDating],
                             hobbies_user: List[models.Hobbies],
                             interest_place_user: List[models.DatingInterestPlace],
                             interest_place_4: models.DatingInterestPlace, 
                             interest_place_5: models.DatingInterestPlace, 
                             interest_place_6: models.DatingInterestPlace, 
                             year_now: int,
                             old_user: int) -> int:
    percent = 0

    allow_distance = user.search_radius if user.search_radius < target_user.search_radius else target_user.search_radius
    distance = geodesic((user.lat, user.long), (target_user.lat, target_user.long)).km
    target_interest_place = await target_user.interest_place_companion.all()
    if distance > allow_distance:
        if (user.dubai and interest_place_4 in interest_place_user and interest_place_5 in interest_place_user and interest_place_6 not in interest_place_user) and (target_user.moving_to_dubai):
            '''1,4,5                            1,4; 1,4,5; 1,4,5,6 ; 1,4,6; 2,4; 2,4,5; 2,4,5,6 ; 2,4,6 '''
            pass
        elif (user.dubai and interest_place_4 in interest_place_user and interest_place_5 in interest_place_user and interest_place_6 in interest_place_user):
            '''1,4,5,6                         1,4; 1,4,5; 1,4,5,6 ; 1,4,6; 2,4; 2,4,5; 2,4,5,6 ; 2,4,6; 3,4; 3,4,5; 3,4,5,6 ; 3,4,6;'''
            pass
        elif (user.dubai and interest_place_4 in interest_place_user and interest_place_5 not in interest_place_user and interest_place_6 in interest_place_user) and \
             (target_user.moving_to_dubai is False):
            '''1,4,6                            1,4; 1,4,5; 1,4,5,6 ; 1,4,6; 3,4; 3,4,5; 3,4,5,6 ; 3,4,6;'''
            pass
        elif (user.dubai and interest_place_4 not in interest_place_user and interest_place_5 in interest_place_user and interest_place_6 not in interest_place_user) and \
             (target_user.moving_to_dubai and target_user.dubai is False):
            '''1,5                               2,4; 2,4,5; 2,4,5,6 ; 2,4,6'''
            pass
        elif (user.dubai and interest_place_4 not in interest_place_user and interest_place_5 in interest_place_user and interest_place_6 in interest_place_user) and \
             (target_user.dubai is False):
            '''1,5,6                            2,4; 2,4,5; 2,4,5,6 ; 2,4,6; 3,4; 3,4,5; 3,4,5,6 ; 3,4,6;'''
            pass
        elif (user.dubai and interest_place_4 not in interest_place_user and interest_place_5 not in interest_place_user and interest_place_6 in interest_place_user) and \
             (target_user.dubai is False and target_user.moving_to_dubai is False):
            '''1,6                               3,4; 3,4,5; 3,4,5,6 ; 3,4,6;'''
            pass 
        elif (user.dubai is False and user.moving_to_dubai is True and interest_place_4 in interest_place_user and interest_place_5 not in interest_place_user and interest_place_6 not in interest_place_user) and \
             (target_user.dubai is True):
            '''2,4                               1,5; 1,4,5; 1,4,5,6 ; 1,5,6'''
            pass
        elif (user.dubai is False and user.moving_to_dubai is True and interest_place_4 in interest_place_user and interest_place_5 in interest_place_user and interest_place_6 not in interest_place_user) and  \
             ((target_user.dubai is True) or (target_user.dubai is False and target_user.moving_to_dubai is True)):
            '''2,4,5                            1,5; 1,4,5; 1,4,5,6 ; 1,5,6; 2,5; 2,4,5; 2,4,5,6 ; 2,5,6;'''
            pass
        elif (user.dubai is False and user.moving_to_dubai is True and interest_place_4 in interest_place_user and interest_place_5 in interest_place_user and interest_place_6 in interest_place_user):
            '''2,4,5,6                         1,5; 1,4,5; 1,4,5,6 ; 1,5,6; 2,5; 2,4,5; 2,4,5,6 ; 2,5,6; 3,5; 3,4,5; 3,4,5,6 ; 3,5,6;'''
            pass
        elif (user.dubai is False and user.moving_to_dubai is True and interest_place_4 in interest_place_user and interest_place_5 not in interest_place_user and interest_place_6 in interest_place_user) and \
             ((target_user.dubai is True) or (target_user.dubai is False and target_user.moving_to_dubai is True)):
            '''2,4,6                           1,5; 1,4,5; 1,4,5,6 ; 1,5,6; 3,5; 3,4,5; 3,4,5,6 ; 3,5,6;'''
            pass
        elif (user.dubai is False and user.moving_to_dubai is True and interest_place_4 not in interest_place_user and interest_place_5 in interest_place_user and interest_place_6 not in interest_place_user) and  \
             (target_user.dubai is False and target_user.moving_to_dubai is True):
            '''2,5                              2,5; 2,4,5; 2,4,5,6 ; 2,5,6'''
            pass
        elif (user.dubai is False and user.moving_to_dubai is True and interest_place_4 not in interest_place_user and interest_place_5 in interest_place_user and interest_place_6 in interest_place_user) and  \
             (target_user.dubai is False):
            '''2,5,6                           2,5; 2,4,5; 2,4,5,6 ; 2,5,6; 3,5; 3,4,5; 3,4,5,6 ; 3,5,6;'''
            pass
        elif (user.dubai is False and user.moving_to_dubai is True and interest_place_4 not in interest_place_user and interest_place_5 not in interest_place_user and interest_place_6 in interest_place_user) and  \
             (target_user.dubai is False and target_user.moving_to_dubai is False):
            '''2,6                              3,5; 3,4,5; 3,4,5,6 ; 3,5,6'''
            pass
        elif (user.dubai is False and user.moving_to_dubai is False and interest_place_4 in interest_place_user and interest_place_5 not in interest_place_user and interest_place_6 not in interest_place_user) and  \
             (target_user.dubai is True):
            '''3,4                              1,6; 1,4,6; 1,4,5,6 ; 1,5,6'''
            pass
        elif (user.dubai is False and user.moving_to_dubai is False and interest_place_4 in interest_place_user and interest_place_5 in interest_place_user and interest_place_6 not in interest_place_user) and \
             (target_user.dubai is True or target_user.moving_to_dubai is True):
            '''3,4,5                           1,6; 1,4,6; 1,4,5,6 ; 1,5,6; 2,6; 2,4,6; 2,4,5,6 ; 2,5,6;'''
            pass
        elif (user.dubai is False and user.moving_to_dubai is False and interest_place_4 in interest_place_user and interest_place_5 in interest_place_user and interest_place_6 in interest_place_user):
            '''3,4,5,6                        1,6; 1,4,6; 1,4,5,6 ; 1,5,6; 2,6; 2,4,6; 2,4,5,6 ; 2,5,6; 3,6; 3,4,6; 3,4,5,6 ; 3,5,6; '''
            pass
        elif (user.dubai is False and user.moving_to_dubai is False and interest_place_4 in interest_place_user and interest_place_5 not in interest_place_user and interest_place_6 in interest_place_user) and \
             ((target_user.dubai is True) or (target_user.moving_to_dubai is False and target_user.moving_to_dubai is False)):
            '''3,4,6                           1,6; 1,4,6; 1,4,5,6 ; 1,5,6; 3,6; 3,4,6; 3,4,5,6 ; 3,5,6;'''
            pass
        elif (user.dubai is False and user.moving_to_dubai is False and interest_place_4 not in interest_place_user and interest_place_5 in interest_place_user and interest_place_6 not in interest_place_user) and \
             (target_user.moving_to_dubai is True):
            '''3,5                              2,6; 2,4,6; 2,4,5,6 ; 2,5,6; '''
            pass
        elif (user.dubai is False and user.moving_to_dubai is False and interest_place_4 not in interest_place_user and interest_place_5 in interest_place_user and interest_place_6 in interest_place_user) and \
             (target_user.dubai is False):
            '''3,5,6                           2,6; 2,4,6; 2,4,5,6 ; 2,5,6; 3,6; 3,4,6; 3,4,5,6 ; 3,5,6;  '''
            pass
        elif (user.dubai is False and user.moving_to_dubai is False and interest_place_4 not in interest_place_user and interest_place_5 not in interest_place_user and interest_place_6 in interest_place_user) and \
             (target_user.dubai is False and target_user.moving_to_dubai is False): 
            '''3,6                              3,6; 3,4,6; 3,4,5,6 ; 3,5,6;'''
            pass
        else:
            return 0
    
    purp_target_user = await target_user.purp_dating.all()
    count_purp = 0
    for item in purp_target_user:
        if item in purp_user:
            count_purp += 1
    if count_purp == 0:
        # print(f'Несовместимость по цели знакомства {user} -> {target_user}')
        return 0

    
    if (purp_sex in purp_user and purp_sex in purp_target_user) and (purp_friend not in purp_user or purp_friend not in purp_target_user):
            '''Если у пользователей сходится цель знакомства - отношения, но не сходится дружба, то проверяется их пол, 
               если пол одинаковый то процент схожести интересов становится 0'''
    if user.male == target_user.male:
        # print(f'Несовместимость по цели знакомства (Цель секс совпадает, дружба нет и одинаковый пол) {user} -> {target_user}')
        return 0

    percent += 30 # 30 процентов за прошлые пункты

    percent += 20 # 20 сразу накидываем за возраст

    difference = abs(old_user - (year_now-target_user.birthday.year))
    percent -= difference * 2 # Вычисляем разницу возраста и отнимаем ее 
    
    if user.children and target_user.children:
        '''Накидываем проценты за детей'''
        percent += 20
        for user_children in user.children_age:
            for target_user_children in target_user.children_age:
                difference_age_children = abs(user_children-target_user_children)
                if difference_age_children <= 2:
                    percent += 10 # Накидываем проценты за возраст детей
        
    # print(len)
    for target_hobbie in await target_user.hobbies.all():
        if target_hobbie in hobbies_user:
            percent += 10
    
    if percent >= 100:
        percent = 99
    
    return percent

# Дубаи                                                             1
# не Дубаи (планирую переезд)                                       2
# не Дубаи (НЕ планирую переезд)                                    3




# 1 - Находится в Дубае                                             4
# 2 - Планирует переезд в Дубай                                     5
# 3 - Не в дубае и не планирует туда переезд                        6

async def test_q():
    await Tortoise.init(TORTOISE_ORM)
    user = await models.UserModel.get(id=46)
    marr = await models.UserModel.get(id=49)

    purp_friend = await models.PurposeOfDating.get(id=1)
    purp_sex = await models.PurposeOfDating.get(id=2)
    purp_user = await user.purp_dating.all()
    year_now = datetime.now().year
    old_user = year_now - user.birthday.year
    hobbies_user = await user.hobbies.all()

    interest_place_marr = await marr.interest_place_companion.all()

    interest_place_user = await user.interest_place_companion.all()
    
    interest_place_4 = await models.DatingInterestPlace.get(id=1)
    interest_place_5 = await models.DatingInterestPlace.get(id=2)
    interest_place_6 = await models.DatingInterestPlace.get(id=3)

    text_user = ""
    text_user += f"User #{user.tg_username} ---- "
    if user.dubai:
        text_user += "Находится в Дубаи "
    else:
        text_user += "Не находится в Дубаи "
    
    if user.moving_to_dubai is True:
        text_user += "(Планриует переезд): \n"
    else:
        text_user += "(не планриует переезд): \n"
    
    text_user += "Интересы знакомства: "
    text_user += ", ".join([i.title_interest for i in interest_place_user])

    text_target_user = ""
    text_target_user += f"User #{marr.tg_username} ---- "
    if marr.dubai:
        text_target_user += "Находится в Дубаи"
    else:
        text_target_user += "Не находится в Дубаи"
    
    if marr.moving_to_dubai is True:
        text_target_user += "(Планриует переезд): \n"
    else:
        text_target_user += "(не планриует переезд): \n"
    text_target_user += "Интересы знакомства: "
    text_target_user += ", ".join([i.title_interest for i in interest_place_marr])

    print(text_user)
    print('\n\n')
    print(text_target_user)
    percent = await calculation_2_user(user=user,
                                       target_user=marr,
                                       purp_friend=purp_friend,
                                       purp_sex=purp_sex,
                                       purp_user=purp_user,
                                       hobbies_user=hobbies_user,
                                       interest_place_user=interest_place_user,
                                       interest_place_4=interest_place_4, 
                                       interest_place_5=interest_place_5, 
                                       interest_place_6=interest_place_6, 
                                       year_now=year_now,
                                       old_user=old_user)
    print('\n')
    print(f"Процент совместимости -> {percent}%")

run_async(test_q())
