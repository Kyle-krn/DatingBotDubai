from models import models
from fastapi import Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi import APIRouter
from loader import templates
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
            percent_db.percent = percent
            await percent_db.save()
        elif percent_db.id == 6:
            percent_db.percent = percent
            await percent_db.save()
            # await reload_hobbies()
    return RedirectResponse(f'/percent',status_code=status.HTTP_302_FOUND)

