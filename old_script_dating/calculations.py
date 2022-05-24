import random
from typing import List
from models import models
from datetime import datetime
from tortoise.queryset import Q
import .check_relations as check
from tortoise import run_async

async def calculation_new_user(user: models.UserModel):
    """Создает связи с новыми пользователями прошедшими регистрацию"""
    verification_user_list = await models.UserModel.filter(Q(ban=False) & Q(end_registration=True)).exclude(id=user.id)
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
                            #  year_now: int,
                             old_user: int) -> int:
    """ Вычисляет полные отношения между 2умя юзерами"""
    percent = 0
    result_distance_check = await check.check_distance(user=user, 
                                                 target_user=target_user,
                                                 interest_place_user=interest_place_user,
                                                 interest_place_4=interest_place_4,
                                                 interest_place_5=interest_place_5,
                                                 interest_place_6=interest_place_6)
    result_purp_check = await check.check_purp(user=user,
                                         target_user=target_user,
                                         purp_friend=purp_friend,
                                         purp_sex=purp_sex,
                                         purp_user=purp_user)
    result_settings_gender = await check.check_settings_gender(user=user,
                                                        target_user=target_user)
    percent += 30 # 30 процентов за прошлые пункты
    percent_age = await check.check_age(old_user=old_user,
                                  user=user,
                                  target_user=target_user)
    percent += percent_age


    percent_children = await check.check_children(user=user,
                                            target_user=target_user)
    percent += percent_children


    percent_hobbies = await check.check_hobbies(target_user=target_user,
                                          hobbies_user=hobbies_user)
    percent += percent_hobbies
    if result_distance_check is False or result_purp_check is False or result_settings_gender is False:
        percent = 0
    if percent < 0:
        percent = 0
    return percent, percent_age, percent_children, percent_hobbies, result_distance_check, result_purp_check, result_settings_gender



