from models import models
from .relations_handlers import check_children, check_age, check_distance, check_hobbies, check_purp
from tortoise.queryset import Q

async def recalculation_children(user: models.UserModel):
    relations = await models.UsersRelations.filter(Q(user=user) | Q(target_user=user))
    for relation in relations:
        if user.id != relation.user_id:
            target_user = await relation.user
        else:
            target_user = await relation.target_user

        percent_children = await check_children(user=user,
                                                target_user=target_user)

        if relation.percent_children != percent_children:
            relation.percent_children = percent_children
            if relation.result_distance_check is True and relation.result_purp_check is True:
                new_percent = 30 + relation.percent_age + relation.percent_children + relation.percent_hobbies
                if new_percent > 0:                                                                                     # С булевым значениями и проверять валидность отношений 
                    relation.percent_compatibility = new_percent                                                  # например если хоть в одном чеке будет False то отношения
                    # user_view = await models.UserView.get_or_none(user=user, relation=relation)                   # уходят в 0 процентов
                    # if user_view is None:
                    await models.UserView.get_or_create(user=user, target_user=target_user, relation=relation)
                    await models.UserView.get_or_create(user=target_user, target_user=user, relation=relation)
                else:
                    relation.percent_compatibility = 0
            await relation.save()



async def recalculation_age(user: models.UserModel, user_age: int):
    # result_age = await check_age()
    relations = await models.UsersRelations.filter(Q(user=user) | Q(target_user=user))
    for relation in relations:
        if user.id != relation.user_id:
            target_user = await relation.user
        else:
            target_user = await relation.target_user
        result_age_check = await check_age(old_user=user_age, target_user = target_user)
        print(f"{user} -> {target_user} ----> {result_age_check}")
        relation.percent_age = result_age_check
        if relation.result_distance_check is True and relation.result_purp_check is True:
            new_percent = 30 + relation.percent_age + relation.percent_children + relation.percent_hobbies
            if new_percent > 0:
                relation.percent_compatibility = new_percent
                await models.UserView.get_or_create(user=user, target_user=target_user, relation=relation)
                await models.UserView.get_or_create(user=target_user, target_user=user, relation=relation)
            else:
                relation.percent_compatibility = 0
            await relation.save()


async def recalculation_location(user: models.UserModel):
    interest_place_user = await user.interest_place_companion.all()   
    interest_place_4 = await models.DatingInterestPlace.get(id=1)
    interest_place_5 = await models.DatingInterestPlace.get(id=2)
    interest_place_6 = await models.DatingInterestPlace.get(id=3)
    relations = await models.UsersRelations.filter(Q(user=user) | Q(target_user=user))
    for relation in relations:
        if user.id != relation.user_id:
            target_user = await relation.user
        else:
            target_user = await relation.target_user
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
        
        elif relation.result_distance_check == False and reslut_distance_check == True:
            relation.result_distance_check = True
            if relation.result_purp_check:
                new_percent = 30 + relation.percent_age + relation.percent_children + relation.percent_hobbies
                if new_percent > 0:
                    relation.percent_compatibility = new_percent
                    await models.UserView.get_or_create(user=user, target_user=target_user, relation=relation)
                    await models.UserView.get_or_create(user=target_user, target_user=user, relation=relation)
                else:
                    relation.percent_compatibility = 0
                # await relation.save()
            await relation.save()




async def recalculation_hobbies(user: models.UserModel):
    hobbies_user = await user.hobbies.all()
    relations = await models.UsersRelations.filter(Q(user=user) | Q(target_user=user))
    for relation in relations:
        if user.id != relation.user_id:
            target_user = await relation.user
        else:
            target_user = await relation.target_user
        percent_hobbies = await check_hobbies(target_user=target_user, hobbies_user=hobbies_user)
        if relation.percent_hobbies != percent_hobbies:
            relation.percent_hobbies = percent_hobbies
            if relation.result_distance_check is True and relation.result_purp_check is True: # Добавить поля в модельку relation для фильтров настроек которые задает юзера
                new_percent = 30 + relation.percent_age + relation.percent_children + relation.percent_hobbies  # типа result_age_filter_check, result_children_filter_check
                if new_percent > 0:                                                                                     # С булевым значениями и проверять валидность отношений 
                    relation.percent_compatibility = new_percent                                                  # например если хоть в одном чеке будет False то отношения
                    # user_view = await models.UserView.get_or_none(user=user, relation=relation)                   # уходят в 0 процентов
                    # if user_view is None:
                    await models.UserView.get_or_create(user=user, target_user=target_user, relation=relation)
                    await models.UserView.get_or_create(user=target_user, target_user=user, relation=relation)
                else:
                    relation.percent_compatibility = 0
            await relation.save()
            # else:
                


async def recalculation_purp(user: models.UserModel):
    relations = await models.UsersRelations.filter(Q(user=user) | Q(target_user=user))
    for relation in relations:
        if user.id != relation.user_id:
            target_user = await relation.user
        else:
            target_user = await relation.target_user

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
            if relation.result_distance_check:
                new_percent = 30 + relation.percent_age + relation.percent_children + relation.percent_hobbies
                if new_percent > 0:
                    relation.percent_compatibility = new_percent
                    await models.UserView.get_or_create(user=user, target_user=target_user, relation=relation)
                    await models.UserView.get_or_create(user=target_user, target_user=user, relation=relation)
                else:
                    relation.percent_compatibility = 0
                # await relation.save()
            await relation.save()
        print(f"{user} -> {target_user} ----> {result_purp_check}")