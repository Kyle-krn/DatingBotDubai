from datetime import date
import redis
from models import models
from .relations_handlers import check_children, check_age, check_distance, check_hobbies, check_purp, check_settings_gender
from tortoise.queryset import Q
from handlers.dating.dating_handlers import redis_cash_1
from handlers.view_relations.views_handlers import redis_cash_2
from typing import Coroutine

async def clear_cache(r: redis.Redis, key: int):
    query = r.get(str(key))
    if query is not None:
        r.delete(str(key))

async def clear_cache_relation(tg_id_1: int, tg_id_2: int):
    await clear_cache(r=redis_cash_1, key=tg_id_1)
    await clear_cache(r=redis_cash_2, key=tg_id_1)
    await clear_cache(r=redis_cash_1, key=tg_id_2)
    await clear_cache(r=redis_cash_2, key=tg_id_2)
    

async def get_target_user_from_relation(user: models.UserModel, relation: models.UsersRelations):
    if user.id != relation.user_id:
        target_user = await relation.user
    else:
        target_user = await relation.target_user
    return target_user


async def recalculation_int(user: models.UserModel, 
                            check_func: Coroutine,
                            attr_name: str,
                            ):
    relations = await models.UsersRelations.filter(Q(user=user) | Q(target_user=user))
    for relation in relations:
        target_user = await get_target_user_from_relation(user=user, relation=relation)
        
        if check_func is check_children:
            new_percent = await check_func(user=user, target_user=target_user)
        elif check_func is check_age:
            today = date.today()
            old_age = int((today - user.birthday).total_seconds() / 60 / 60 / 24 / 365)
            new_percent = await check_func(old_user=old_age, user=user, target_user=target_user)
        elif check_func is check_hobbies:
            hobbies_user = await user.hobbies.all()
            new_percent = await check_func(target_user=target_user, hobbies_user=hobbies_user)
        

        old_percent = getattr(relation, attr_name)
        if old_percent != new_percent:
            setattr(relation, attr_name, new_percent)
            if relation.result_distance_check is True and relation.result_purp_check is True and relation.result_gender_check is True:
                percent_for_1_2_step = await models.DatingPercent.get(id=1)
                general_percent = percent_for_1_2_step.percent + relation.percent_age + relation.percent_children + relation.percent_hobbies
                if general_percent > 0:
                    relation.percent_compatibility = general_percent                                                  
                    await models.UserView.get_or_create(user=user, target_user=target_user, relation=relation)
                    await models.UserView.get_or_create(user=target_user, target_user=user, relation=relation)
                else:
                    relation.percent_compatibility = 0
        await relation.save()
        await clear_cache_relation(tg_id_1=user.tg_id, tg_id_2=target_user.tg_id)



async def recalculation_location(user: models.UserModel):
    interest_place_user = await user.interest_place_companion.all()   
    interest_place_4 = await models.DatingInterestPlace.get(id=1)
    interest_place_5 = await models.DatingInterestPlace.get(id=2)
    interest_place_6 = await models.DatingInterestPlace.get(id=3)
    relations = await models.UsersRelations.filter(Q(user=user) | Q(target_user=user))
    for relation in relations:

        target_user = await get_target_user_from_relation(user=user, relation=relation)

        reslut_distance_check = await check_distance(user=user, 
                             target_user=target_user,
                             interest_place_user=interest_place_user,
                             interest_place_4=interest_place_4,
                             interest_place_5=interest_place_5,
                             interest_place_6=interest_place_6)
        if relation.result_distance_check == True and reslut_distance_check == False:
            relation.percent_compatibility = 0
            relation.result_distance_check = False
            await relation.save()
            await clear_cache_relation(tg_id_1=user.tg_id, tg_id_2=target_user.tg_id)
        
        elif relation.result_distance_check == False and reslut_distance_check == True:
            relation.result_distance_check = True
            if relation.result_purp_check and relation.result_gender_check is True:
                percent_for_1_2_step = await models.DatingPercent.get(id=1)
                new_percent = percent_for_1_2_step.percent + relation.percent_age + relation.percent_children + relation.percent_hobbies
                if new_percent > 0:
                    relation.percent_compatibility = new_percent
                    await models.UserView.get_or_create(user=user, target_user=target_user, relation=relation)
                    await models.UserView.get_or_create(user=target_user, target_user=user, relation=relation)
                else:
                    relation.percent_compatibility = 0
            await relation.save()
            await clear_cache_relation(tg_id_1=user.tg_id, tg_id_2=target_user.tg_id)






async def recalculation_purp(user: models.UserModel):
    relations = await models.UsersRelations.filter(Q(user=user) | Q(target_user=user))
    for relation in relations:
        target_user = await get_target_user_from_relation(user=user, relation=relation)
        purp_friend = await models.PurposeOfDating.get(id=1)
        purp_sex = await models.PurposeOfDating.get(id=2)
        purp_user = await user.purp_dating.all()
        
        result_purp_check = await check_purp(user=user,
                                             target_user=target_user,
                                             purp_friend=purp_friend,
                                             purp_sex=purp_sex,
                                             purp_user=purp_user)
        
        if relation.result_purp_check is True and result_purp_check is False:
            relation.percent_compatibility = 0
            relation.result_purp_check = False
            await relation.save()
        if relation.result_purp_check is False and result_purp_check is True:
            relation.result_purp_check = True
            if relation.result_distance_check and relation.result_gender_check is True:
                percent_for_1_2_step = await models.DatingPercent.get(id=1)
                new_percent = percent_for_1_2_step.percent + relation.percent_age + relation.percent_children + relation.percent_hobbies
                if new_percent > 0:
                    relation.percent_compatibility = new_percent
                    await models.UserView.get_or_create(user=user, target_user=target_user, relation=relation)
                    await models.UserView.get_or_create(user=target_user, target_user=user, relation=relation)
                else:
                    relation.percent_compatibility = 0
                # await relation.save()
            await relation.save()
            await clear_cache_relation(tg_id_1=user.tg_id, tg_id_2=target_user.tg_id)



async def recalculation_by_gender(user: models.UserModel):
    relations = await models.UsersRelations.filter(Q(user=user) | Q(target_user=user))
    for relation in relations:
        target_user = await get_target_user_from_relation(user=user, relation=relation)
        result_gender_check = await check_settings_gender(user=user, target_user=target_user)

        if relation.result_gender_check is True and result_gender_check is False:
            relation.percent_compatibility = 0
            relation.result_gender_check = False
            await relation.save()
        
        elif relation.result_gender_check is False and result_gender_check is True:
            relation.result_gender_check = True
            if relation.result_distance_check and relation.result_purp_check:
                percent_for_1_2_step = await models.DatingPercent.get(id=1)
                new_percent = percent_for_1_2_step.percent + relation.percent_age + relation.percent_children + relation.percent_hobbies
                if new_percent > 0:
                    relation.percent_compatibility = new_percent
                    await models.UserView.get_or_create(user=user, target_user=target_user, relation=relation)
                    await models.UserView.get_or_create(user=target_user, target_user=user, relation=relation)
                else:
                    relation.percent_compatibility = 0
                # await relation.save()
            await relation.save()


