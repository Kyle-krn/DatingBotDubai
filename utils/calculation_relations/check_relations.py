from models import models
from datetime import datetime
from typing import List


async def check_distance(user: models.UserModel, 
                         target_user: models.UserModel,
                         interest_place_user: List[models.DatingInterestPlace],
                         interest_place_4: models.DatingInterestPlace, 
                         interest_place_5: models.DatingInterestPlace, 
                         interest_place_6: models.DatingInterestPlace) -> bool:

    ipu = interest_place_user
    ip4 = interest_place_4
    ip5 = interest_place_5
    ip6 = interest_place_6
    tip = await target_user.interest_place_companion.all()
                   
    condition_1 = (ip4 in tip and ip5 not in tip and ip6 not in tip) or \
                    (ip4 in tip and ip5 in tip and ip6 not in tip) or \
                    (ip4 in tip and ip5 in tip and ip6 in tip) or \
                    (ip4 in tip and ip5 not in tip and ip6 in tip)
                    
    condition_2 = (ip4 not in tip and ip5 in tip and ip6 not in tip) or \
                    (ip4 in tip and ip5 in tip and ip6 not in tip) or \
                    (ip4 in tip and ip5 in tip and ip6 in tip) or \
                    (ip4 not in tip and ip5 in tip and ip6 in tip)

    condition_3 = (ip4 not in tip and ip5 not in tip and ip6 in tip) or \
                    (ip4 in tip and ip5 not in tip and ip6 in tip) or \
                    (ip4 in tip and ip5 in tip and ip6 in tip) or \
                    (ip4 not in tip and ip5 in tip and ip6 in tip)

    tar_place_1_and_2 = target_user.dubai or target_user.moving_to_dubai
    tar_place_1_and_3 = target_user.moving_to_dubai is False
    tar_place_2 = target_user.dubai is False and target_user.moving_to_dubai
    tar_place_2_and_3 = target_user.dubai is False
    tar_place_3 = target_user.dubai is False and target_user.moving_to_dubai is False
    tar_place_1 = target_user.dubai is True


    if (user.dubai and ip4 in ipu) and condition_1:
        return True
    elif (user.dubai and ip4 in ipu and ip5 in ipu and ip6 not in ipu) and (tar_place_1_and_2 and condition_1):
        '''1,4,5                            1,4; 1,4,5; 1,4,5,6 ; 1,4,6; 2,4; 2,4,5; 2,4,5,6 ; 2,4,6 '''
        return True
    elif (user.dubai and ip4 in ipu and ip5 in ipu and ip6 in ipu) and (condition_1):
        '''1,4,5,6                         1,4; 1,4,5; 1,4,5,6 ; 1,4,6; 2,4; 2,4,5; 2,4,5,6 ; 2,4,6; 3,4; 3,4,5; 3,4,5,6 ; 3,4,6;'''
        return True
    elif (user.dubai and ip4 in ipu and ip5 not in ipu and ip6 in ipu) and (tar_place_1_and_3 and condition_1):
        '''1,4,6                            1,4; 1,4,5; 1,4,5,6 ; 1,4,6; 3,4; 3,4,5; 3,4,5,6 ; 3,4,6;'''
        return True
    elif (user.dubai and ip4 not in ipu and ip5 in ipu and ip6 not in ipu) and (tar_place_2 and condition_1):
        '''1,5                               2,4; 2,4,5; 2,4,5,6 ; 2,4,6'''
        return True
    elif (user.dubai and ip4 not in ipu and ip5 in ipu and ip6 in ipu) and (tar_place_2_and_3 and condition_1):
        '''1,5,6                            2,4; 2,4,5; 2,4,5,6 ; 2,4,6; 3,4; 3,4,5; 3,4,5,6 ; 3,4,6;'''
        return True
    elif (user.dubai and ip4 not in ipu and ip5 not in ipu and ip6 in ipu) and (tar_place_3 and condition_1):
        '''1,6                               3,4; 3,4,5; 3,4,5,6 ; 3,4,6;'''
        return True 
    elif (user.dubai is False and user.moving_to_dubai is True and ip4 in ipu and ip5 not in ipu and ip6 not in ipu) and (tar_place_1 and condition_2):
        '''2,4                               1,5; 1,4,5; 1,4,5,6 ; 1,5,6'''
        return True
    elif (user.dubai is False and user.moving_to_dubai is True and ip4 in ipu and ip5 in ipu and ip6 not in ipu) and (tar_place_1_and_2 and condition_2):
        '''2,4,5                            1,5; 1,4,5; 1,4,5,6 ; 1,5,6; 2,5; 2,4,5; 2,4,5,6 ; 2,5,6;'''
        return True
    elif (user.dubai is False and user.moving_to_dubai is True and ip4 in ipu and ip5 in ipu and ip6 in ipu) and condition_2:
        '''2,4,5,6                         1,5; 1,4,5; 1,4,5,6 ; 1,5,6; 2,5; 2,4,5; 2,4,5,6 ; 2,5,6; 3,5; 3,4,5; 3,4,5,6 ; 3,5,6;'''
        return True
    elif (user.dubai is False and user.moving_to_dubai is True and ip4 in ipu and ip5 not in ipu and ip6 in ipu) and (tar_place_1_and_3 and condition_2):
        '''2,4,6                           1,5; 1,4,5; 1,4,5,6 ; 1,5,6; 3,5; 3,4,5; 3,4,5,6 ; 3,5,6;'''
        return True
    elif (user.dubai is False and user.moving_to_dubai is True and ip4 not in ipu and ip5 in ipu and ip6 not in ipu) and (tar_place_2 and condition_2):
        '''2,5                              2,5; 2,4,5; 2,4,5,6 ; 2,5,6'''
        return True
    elif (user.dubai is False and user.moving_to_dubai is True and ip4 not in ipu and ip5 in ipu and ip6 in ipu) and (tar_place_2_and_3 and condition_2):
        '''2,5,6                           2,5; 2,4,5; 2,4,5,6 ; 2,5,6; 3,5; 3,4,5; 3,4,5,6 ; 3,5,6;'''
        return True
    elif (user.dubai is False and user.moving_to_dubai is True and ip4 not in ipu and ip5 not in ipu and ip6 in ipu) and (tar_place_3 and condition_2):
        '''2,6                              3,5; 3,4,5; 3,4,5,6 ; 3,5,6'''
        return True
    elif (user.dubai is False and user.moving_to_dubai is False and ip4 in ipu and ip5 not in ipu and ip6 not in ipu) and (tar_place_1 and condition_3):
        '''3,4                              1,6; 1,4,6; 1,4,5,6 ; 1,5,6'''
        return True
    elif (user.dubai is False and user.moving_to_dubai is False and ip4 in ipu and ip5 in ipu and ip6 not in ipu) and (tar_place_1_and_2 and condition_3):
        '''3,4,5                           1,6; 1,4,6; 1,4,5,6 ; 1,5,6; 2,6; 2,4,6; 2,4,5,6 ; 2,5,6;'''
        return True
    elif (user.dubai is False and user.moving_to_dubai is False and ip4 in ipu and ip5 in ipu and ip6 in ipu) and condition_3:
        '''3,4,5,6                        1,6; 1,4,6; 1,4,5,6 ; 1,5,6; 2,6; 2,4,6; 2,4,5,6 ; 2,5,6; 3,6; 3,4,6; 3,4,5,6 ; 3,5,6; '''
        return True
    elif (user.dubai is False and user.moving_to_dubai is False and ip4 in ipu and ip5 not in ipu and ip6 in ipu) and (tar_place_1_and_3 and condition_3):
        '''3,4,6                           1,6; 1,4,6; 1,4,5,6 ; 1,5,6; 3,6; 3,4,6; 3,4,5,6 ; 3,5,6;'''
        pass
    elif (user.dubai is False and user.moving_to_dubai is False and ip4 not in ipu and ip5 in ipu and ip6 not in ipu) and (tar_place_2 and condition_3):
        '''3,5                              2,6; 2,4,6; 2,4,5,6 ; 2,5,6; '''
        pass
        return True
    elif (user.dubai is False and user.moving_to_dubai is False and ip4 not in ipu and ip5 in ipu and ip6 in ipu) and (tar_place_2_and_3 and condition_3):
        '''3,5,6                           2,6; 2,4,6; 2,4,5,6 ; 2,5,6; 3,6; 3,4,6; 3,4,5,6 ; 3,5,6;  '''
        pass
        return True
    elif (user.dubai is False and user.moving_to_dubai is False and ip4 not in ipu and ip5 not in ipu and ip6 in ipu) and (tar_place_3 and condition_3): 
        '''3,6                              3,6; 3,4,6; 3,4,5,6 ; 3,5,6;'''
        return True
    else:
        return False


async def check_settings_gender(user: models.UserModel,
                                target_user: models.UserModel) -> bool:
    '''Проверяет партнеров по половому признаку'''
    user_settings: models.UserSearchSettings = await user.search_settings
    target_user_settings: models.UserSearchSettings = await target_user.search_settings
    if user_settings.male is not None:
        if user_settings.male != target_user.male:
            return False
    if target_user_settings.male is not None:
        if target_user_settings.male != user.male:
            return False
    return True
    

async def check_purp(user: models.UserModel, 
                     target_user: models.UserModel,
                     purp_friend: models.PurposeOfDating,
                     purp_sex: models.PurposeOfDating,
                     purp_user: List[models.PurposeOfDating]) -> bool:
    '''Проверяет партнеров по цели знакомства'''
    purp_target_user = await target_user.purp_dating.all()
    count_purp = 0
    for item in purp_target_user:
        if item in purp_user:
            count_purp += 1
    if count_purp == 0:
        return False
    if ((purp_sex in purp_user and purp_sex in purp_user) and (purp_friend not in purp_user or purp_friend not in purp_target_user)) and user.male == target_user.male:
            '''Если у пользователей сходится цель знакомства - отношения, но не сходится дружба, то проверяется их пол, 
               если пол одинаковый то процент схожести интересов становится 0'''
            return False
    return True


async def check_age(old_user: int,
                    user: models.UserModel,
                    target_user: models.UserModel) -> int:
    percent_age = await models.DatingPercent.get(id=2)
    percent_age = percent_age.percent # 20 сразу накидываем за возраст
    year_now = datetime.now().year
    user_settings: models.UserSearchSettings = await user.search_settings
    tar_user_settings: models.UserSearchSettings = await target_user.search_settings
    
    age_user = old_user
    age_tar_user = year_now-target_user.birthday.year
    if user_settings.min_age is not None or user_settings.max_age is not None:
        if (user_settings.min_age < age_tar_user < user_settings.max_age) is False:
            return -1000

    if tar_user_settings.min_age is not None or tar_user_settings.max_age is not None:
        if (tar_user_settings.min_age < age_user < tar_user_settings.max_age) is False:
            return -1000

    difference = abs(old_user - (year_now-target_user.birthday.year))
    difference_percent = await models.DatingPercent.get(id=3)
    difference = difference * difference_percent.percent
    return percent_age - difference # Вычисляем разницу возраста и отнимаем ее 


async def check_children(user: models.UserModel,
                         target_user: models.UserModel) -> int:
    percent_children = 0
    user_settings: models.UserSearchSettings = await user.search_settings
    tar_user_settings: models.UserSearchSettings = await target_user.search_settings
    
    if user_settings.children is not None:
        if user_settings.children != target_user.children:
            return -1000
        if user_settings.children_min_age is not None and user_settings.children_max_age is not None and len(target_user.children_age) > 0:
            min_age_children = min(target_user.children_age)
            max_age_children = max(target_user.children_age)

            if user_settings.children_min_age > min_age_children or user_settings.children_max_age < max_age_children:
                return -1000
            
    if tar_user_settings.children is not None:
        if tar_user_settings.children != user.children:
            return -1000
        if tar_user_settings.children_min_age is not None and tar_user_settings.children_max_age is not None and len(user.children_age) > 0:
            min_age_children = min(user.children_age)
            max_age_children = max(user.children_age)

            if tar_user_settings.children_min_age > min_age_children or tar_user_settings.children_max_age < max_age_children:
                return -1000

    if user.children and target_user.children:
        '''Накидываем проценты за детей'''
        perecent_children = await models.DatingPercent.get(id=4)
        percent_age_children = await models.DatingPercent.get(id=5)
        percent_children += perecent_children.percent
        for user_children in user.children_age:
            for target_user_children in target_user.children_age:
                difference_age_children = abs(user_children-target_user_children)
                if difference_age_children <= 2:
                    percent_children += percent_age_children.percent # Накидываем проценты за возраст детей
    return percent_children


async def check_hobbies(target_user: models.UserModel,
                        hobbies_user: List[models.Hobbies]) -> int:
    perecent_hobbies_db = await models.DatingPercent.get(id=6)
    percent_hobbies = 0
    for target_hobbie in await target_user.hobbies.all():
        if target_hobbie in hobbies_user:
            percent_hobbies += perecent_hobbies_db.percent
    return percent_hobbies


