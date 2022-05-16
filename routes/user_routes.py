from datetime import datetime, timedelta
from typing import Optional
from handlers.calculation_relations.relations_handlers import check_age, check_children, check_hobbies
from models import models
from tortoise.queryset import Q
from fastapi import Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import APIRouter
from loader import templates, bot
from dateutil.relativedelta import *
import starlette.status as status

from routes.login_routes import get_current_username
user_router = APIRouter()


@user_router.get("/", response_class=HTMLResponse)
async def list_user(request: Request, verif: bool = False, username: str = None, log: str = Depends(get_current_username)):
    if verif is True:
        users = await models.UserModel.filter(Q(verification=False) & Q(ban=False)).order_by('-last_verification_time', 'id')
    
    if username:
        users = await models.UserModel.filter(tg_username__icontains=username)

    if verif is False and not username:
        users = await models.UserModel.all().order_by('id')
    data_users = [
        {"id": i.id,
        "username": i.tg_username,
        "name": i.name,
        "premium": "✅" if i.end_premium else "❌",
        "ban": "✅" if i.ban is False  else "❌",
        "verification": "✅" if i.verification is True else "❌"
        } for i in users
    ]
    return templates.TemplateResponse("list_users.html", {"request": request, "users": data_users   })




@user_router.get("/get_user/{id}", response_class=HTMLResponse)
async def test(request: Request, id: int, log: str = Depends(get_current_username)):
    user = await models.UserModel.get(id=id)
    avatar = await user.avatar
    data = {"id": user.id,
            "tg_id": user.tg_id,
            "tg_username": user.tg_username,
            "name": user.name,
            "bday": user.birthday,
            "place": user.place,
            "file_path": avatar.file_path,
            "marital_status": user.marital_status,
            "superlike": user.superlike_count,
            "free_likes": user.free_likes,
            "verification": user.verification ,
            "end_registration": '✅' if user.end_registration is True else "❌"}
    
    if user.male is None:
        data['gender'] = "Не указано"
    else:
        data["gender"] = "Муж." if user.male is True else "Жен."
    
    if user.moving_to_dubai is None:
        data['moving_to_dubai'] = 'Не указано'
    else:
        data['moving_to_dubai'] = '✅' if user.moving_to_dubai is True else "❌"
    
    hobbies = await user.hobbies
    hobbies_str_list = [i.title_hobbie for i in hobbies]
    if len(hobbies) == 0:
        data['hobbies'] = None
    else:
        data['hobbies'] = hobbies_str_list
    
    if user.children is None:
        data['children'] = "Не скажу"
        data['children_age'] = None
    elif user.children is False:
        data['children'] = "Нет"
        data['children_age'] = None
    elif user.children is True:
        data['children'] = "Нет"
        data['children_age'] = False if len(user.children_age) == 0 else ", ".join([str(i) for i in user.children_age])

    purp = [i.title_purp for i in await user.purp_dating] 
    
    if len(purp) == 0:
        data['purp'] = "Не указано"
    else:
        data['purp'] = ", ".join(purp)
    
    if user.end_premium is None:
        data['premium'] = "Нет Gold статуса"
    else:
        data['premium'] = f"До {user.end_premium.strftime('%d.%m.%Y')}"

    data['ban'] = "В бане ❌" if user.ban is True else "Ограничений нет ✅"
    return templates.TemplateResponse("item.html", {"request": request, "user": data, "photo_bool": avatar.photo_bool, "hobbies": hobbies})

@user_router.get("/ban_user/{id}", response_class=RedirectResponse)
async def ban_user_handler(request: Request, id: int, log: str = Depends(get_current_username)):
    user = await models.UserModel.get(id=id)
    user.ban = not user.ban
    await user.save()
    if user.ban:
        await bot.send_message(chat_id=user.tg_id, text="Вы забанены.")
    else:
        await bot.send_message(chat_id=user.tg_id, text="Вас разбанили.")
    return f"/get_user/{id}"

@user_router.get("/verif_user/{id}", response_class=RedirectResponse)
async def verif_user(request: Request, id: int, log: str = Depends(get_current_username)):
    user = await models.UserModel.get(id=id)
    user.verification = not user.verification
    await user.save()
    if user.verification:
        await bot.send_message(chat_id=user.tg_id, text="Ваш аккаунт верифицирован.")
    else:
        await bot.send_message(chat_id=user.tg_id, text="Ваш аккаунт перестал был верифицированым.")
    return f"/get_user/{id}"



@user_router.post("/del_hobbie/{id}")
async def del_hobbie_handler(request: Request, id: int, hobbies: list = Form(...), log: str = Depends(get_current_username)):
    # body = await request.json()
    user = await models.UserModel.get(id=id)
    for hobbie in hobbies:
        await user.hobbies.remove(await models.Hobbies.get(id=hobbie))
    return RedirectResponse(
        f'/get_user/{id}', 
        status_code=status.HTTP_302_FOUND)

@user_router.post("/append_superlike/{id}")
async def append_superlikes(request: Request, id: int, superlike_count: int = Form(...), log: str = Depends(get_current_username)):
    user = await models.UserModel.get(id=id)
    user.superlike_count += superlike_count
    await user.save()
    return RedirectResponse(
        f'/get_user/{id}', 
        status_code=status.HTTP_302_FOUND)


@user_router.post("/append_premium/{id}")
async def append_superlikes(request: Request, id: int, mounth_count: int = Form(...), log: str = Depends(get_current_username)):
    user = await models.UserModel.get(id=id)
    end_premium_date = datetime.utcnow() + relativedelta(months=+mounth_count)
    if user.end_premium is None:
        user.end_premium = end_premium_date
    else:
        user.end_premium = user.end_premium + relativedelta(months=+mounth_count)
    if user.end_premium.replace(tzinfo=None) < datetime.now():
        user.end_premium = None
    await user.save()
    return RedirectResponse(
        f'/get_user/{id}', 
        status_code=status.HTTP_302_FOUND)

@user_router.post("/del_avatar/{id}")
async def del_hobbie_handler(request: Request, id: int, msg: Optional[str] = Form(None), log: str = Depends(get_current_username)):
    user = await models.UserModel.get(id=id)
    avatar = await user.avatar
    avatar.file_id = None
    avatar.file_path = None
    avatar.file_type = None
    avatar.photo_bool = None
    await avatar.save()
    if not msg:
        text = "Ваше фото отклонено."
    else:
        text = msg
    await bot.send_message(chat_id=user.tg_id ,text=text)
    return RedirectResponse(
        f'/get_user/{id}', 
        status_code=status.HTTP_302_FOUND)



      