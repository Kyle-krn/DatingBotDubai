from datetime import datetime
from typing import Coroutine
# from handlers.calculation_relations.relations_handlers import check_age, check_children, check_hobbies
import utils.calculation_relations.check_relations as check
from models import models
from fastapi import Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi import APIRouter
from loader import templates
from dateutil.relativedelta import *
import starlette.status as status
from routes.login_routes import get_current_username

percent_router = APIRouter()

@percent_router.get("/percent")
async def del_hobbie_handler(request: Request, log: str = Depends(get_current_username)):
    """Страничка перерасчета процентов отношений"""
    percents = await models.DatingPercent.all().order_by('id')
    return templates.TemplateResponse("percent.html", {"request": request, "percents":percents})


@percent_router.post("/percent/children")
async def change_percent_handler(request: Request, 
                                 percent_children: int = Form(...),
                                 percent_children_age: int = Form(...),
                                 log: str = Depends(get_current_username)):
    """Изменение процентов за детей"""
    percent_children_db = await models.DatingPercent.get(id=4)
    percent_children_age_db = await models.DatingPercent.get(id=5)
    if percent_children_db.percent == percent_children and percent_children_age_db.percent == percent_children_age:
        pass
    else:
        percent_children_db.percent = percent_children
        await percent_children_db.save()
        percent_children_age_db.percent = percent_children_age
        await percent_children_age_db.save()
        await reload_precent(func = check.check_children, attr_name="percent_children", relations_kwargs = {"percent_children__gt": 0})
    return RedirectResponse(f'/percent',status_code=status.HTTP_302_FOUND)

@percent_router.post("/percent/age")
async def change_percent_handler(request: Request, 
                                 percent_age: int = Form(...),
                                 percent_step: int = Form(...),
                                 log: str = Depends(get_current_username)):
    """Изменение процентов за возраст"""
    percent_age_db = await models.DatingPercent.get(id=2)
    percent_age_step_db = await models.DatingPercent.get(id=3)
    if percent_age_db.percent == percent_age and percent_age_step_db.percent == percent_step:
        pass
    else:
        percent_age_db.percent = percent_age
        await percent_age_db.save()
        percent_age_step_db.percent = percent_step
        await percent_age_step_db.save()
        # await reload_age()
        await reload_precent(func = check.check_age, attr_name="percent_age", relations_kwargs = {"percent_age__gt": 0})
    return RedirectResponse(f'/percent',status_code=status.HTTP_302_FOUND)


@percent_router.post("/percent/{id}")
async def change_percent_handler(request: Request, 
                                 id: int, 
                                 percent: int = Form(...),
                                 log: str = Depends(get_current_username)):
    """Изменение процентов за 1 и 2ой шаг или хобби"""
    percent_db = await models.DatingPercent.get(id=id)
    if percent_db.percent != percent:
        if percent_db.id == 1:
            await reload_percent_for_1_2_step(old_percent=percent_db.percent, new_percent=percent)
            percent_db.percent = percent
            await percent_db.save()
        elif percent_db.id == 6:
            percent_db.percent = percent
            await percent_db.save()
            # await reload_hobbies()
            await reload_precent(func=check.check_hobbies, attr_name="percent_hobbies", relations_kwargs = {"percent_hobbies__gt": 0})
    return RedirectResponse(f'/percent',status_code=status.HTTP_302_FOUND)


async def reload_precent(func: Coroutine, attr_name: str, relations_kwargs: dict):
    relations = await models.UsersRelations.filter(**relations_kwargs)
    for relation in relations:
        user = await relation.user
        target_user = await relation.target_user
        if func is check.check_children:
            new_percent = await func(user=user, target_user=target_user)
        elif func is check.check_age:
            year_now = datetime.now().year
            old_user = year_now - user.birthday.year
            new_percent = await func(old_user, user, target_user)
        elif func is check.check_hobbies:
            hobbies_user = await user.hobbies.all()
            new_percent = await func(target_user=target_user,
                                                hobbies_user=hobbies_user)

        setattr(relation, attr_name, new_percent)
        if relation.result_distance_check and relation.result_purp_check and relation.result_gender_check:
            step1_2 = await models.DatingPercent.get(id=1)
            general_percent = step1_2.percent + relation.percent_children + relation.percent_age + relation.percent_hobbies
            if general_percent > 0:
                relation.percent_compatibility = general_percent                                               
                await models.UserView.get_or_create(user=await relation.user, target_user=await relation.target_user, relation=relation)
                await models.UserView.get_or_create(user=await relation.target_user, target_user=await relation.user, relation=relation)
        else:
            relation.percent_compatibility = 0 
        await relation.save()


async def reload_percent_for_1_2_step(old_percent, new_percent):
    """Перерасчет за 1 и 2ой шаг"""
    relations = await models.UsersRelations.filter(percent_compatibility__gt=0)
    for relation in relations:

        percent = relation.percent_compatibility 
        percent = percent - old_percent + new_percent
        if percent > 0:
            relation.percent_compatibility = percent
            await models.UserView.get_or_create(user=await relation.user, target_user=await relation.target_user, relation=relation)
            await models.UserView.get_or_create(user=await relation.target_user, target_user=await relation.user, relation=relation)
        else:
            relation.percent_compatibility = 0 
        await relation.save()


