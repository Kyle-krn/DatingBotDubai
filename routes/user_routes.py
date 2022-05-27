from datetime import datetime
from typing import Optional
from models import models
from tortoise.queryset import Q
from fastapi import Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import APIRouter
from loader import templates, bot
from dateutil.relativedelta import *
import starlette.status as status
from aiogram.utils.exceptions import BotBlocked
from routes.login_routes import get_current_username
from urllib.parse import urlencode

user_router = APIRouter()


@user_router.get("/", response_class=HTMLResponse)
async def list_user(request: Request, 
                    page: int = 1,
                    verif: bool = False, 
                    username: str = None,
                    not_register: bool = False,
                    log: str = Depends(get_current_username)):
    """Список пользователей"""
    if verif is True:
        users = models.UserModel.filter(Q(verification=False) & Q(ban=False) & Q(end_registration=True)).order_by('-last_verification_time', 'id')
    if username:
        users = models.UserModel.filter(tg_username__icontains=username)
    if verif is False and not username:
        users = models.UserModel.all().order_by('id')
    if not_register is True:
        users = models.UserModel.filter(end_registration=False).order_by('id')
    params = request.query_params._dict
    if 'page' in params:
        del params['page']
    limit = 30
    offset = (page - 1) * limit
    count_users = await users.count()
    last_page = count_users/limit
    if count_users % limit == 0:
        last_page = int(last_page)
    elif count_users % limit != 0:
        last_page = int(last_page + 1)

    users = await users.offset(offset).limit(limit)
    query_params = urlencode(params)
    previous_page = page-1
    next_page = page+1
    if page == 1:
        previous_page = None
    if page == last_page:
        next_page = None
    if page > last_page:
        pass
    data_users = [
        {"id": i.id,
        "username": i.tg_username,
        "name": i.name,
        "premium": "✅" if i.end_premium else "❌",
        "ban": "✅" if i.ban is False  else "❌",
        "verification": "✅" if i.verification is True else "❌"
        } for i in users
    ]
    context = {"request": request, 
               "users": data_users,
               "previous_page": previous_page,
               "next_page": next_page,
               "page": page,
               "last_page": last_page,
               "query_params": query_params}
    return templates.TemplateResponse("list_users.html", context)



@user_router.get("/get_user/{id}", response_class=HTMLResponse)
async def test(request: Request, id: int, log: str = Depends(get_current_username)):
    """Подробнее о пользователе"""
    user = await models.UserModel.get_or_none(id=id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    avatar = await user.avatar
    user_place = await user.place
    marital_status = await user.marital_status
    data = {"id": user.id,
            "tg_id": user.tg_id,
            "tg_username": user.tg_username,
            "name": user.name,
            "bday": user.birthday,
            "place": user_place.place_name if user_place else "Не указан",
            "dubai": user.dubai,
            "file_path": avatar.file_path,
            "marital_status": marital_status.title_status if marital_status else "Не указан",
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
    """Бан/Разбан юзера"""
    user = await models.UserModel.get_or_none(id=id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user.ban = not user.ban
    await user.save()
    if user.ban:
        text = "Вы забанены."
    else:
        text = "Вас разбанили."
    try:
        await bot.send_message(chat_id=user.tg_id, text=text)
    except BotBlocked:
        pass
    return f"/get_user/{id}"


@user_router.get("/verif_user/{id}", response_class=RedirectResponse)
async def verif_user(request: Request, id: int, log: str = Depends(get_current_username)):
    """Забрать/Дать верификацию юзеру"""
    user = await models.UserModel.get_or_none(id=id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user.verification = not user.verification
    await user.save()
    if user.verification:
        user.end_registration = True
        await user.save()
        text="Ваш аккаунт верифицирован."
    else:
        text="Ваш аккаунт перестал был верифицированым."
    try:
        await bot.send_message(chat_id=user.tg_id, text=text)
    except BotBlocked:
        pass
    return f"/get_user/{id}"


@user_router.get("/del_likes/{id}", response_class=RedirectResponse)
async def verif_user(request: Request, id: int, log: str = Depends(get_current_username)):
    """Отчистить лайки и взаимные лайки для юзера"""
    user = await models.UserModel.get_or_none(id=id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user.spam_ad_ids = None
    await user.save()
    await models.UserView.filter(Q(user=user) & Q(like=True)).update(like=False, superlike=False)
    await models.MutualLike.filter(Q(user=user) | Q(target_user=user)).delete()
    return f"/get_user/{id}"


@user_router.get("/del_user/{id}", response_class=RedirectResponse)
async def verif_user(request: Request, id: int, log: str = Depends(get_current_username)):
    """Отчистить лайки и взаимные лайки для юзера"""
    user = await models.UserModel.get_or_none(id=id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    await user.delete()
    # user.spam_ad_ids = None
    await user.save()
    await models.UserView.filter(Q(user=user) & Q(like=True)).delete()
    await models.MutualLike.filter(Q(user=user) | Q(target_user=user)).delete()
    return f"/"


@user_router.post("/del_hobbie/{id}")
async def del_hobbie_handler(request: Request, id: int, hobbies: list = Form(...), log: str = Depends(get_current_username)):
    """Удаляем хобби"""
    user = await models.UserModel.get_or_none(id=id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    for hobbie in hobbies:
        await user.hobbies.remove(await models.Hobbies.get(id=hobbie))
    return RedirectResponse(
        f'/get_user/{id}', 
        status_code=status.HTTP_302_FOUND)


@user_router.post("/append_superlike/{id}")
async def append_superlikes(request: Request, 
                            id: int, 
                            superlike_count: int = Form(...), 
                            log: str = Depends(get_current_username)):
    """Накидываем суперлайки"""
    user = await models.UserModel.get_or_none(id=id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user.superlike_count += superlike_count
    await user.save()
    return RedirectResponse(
        f'/get_user/{id}', 
        status_code=status.HTTP_302_FOUND)


@user_router.post("/append_premium/{id}")
async def append_superlikes(request: Request, 
                            id: int, mounth_count: int = Form(...), 
                            log: str = Depends(get_current_username)):
    """Накидываем админку"""
    user = await models.UserModel.get_or_none(id=id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
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
async def del_hobbie_handler(request: Request, 
                             id: int, 
                             msg: Optional[str] = Form(None), 
                             log: str = Depends(get_current_username)):
    """Удаляем аватар"""
    user = await models.UserModel.get_or_none(id=id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user.verification = False
    user.end_registration = False
    await user.save()
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
    try:
        await bot.send_message(chat_id=user.tg_id ,text=text)
    except BotBlocked:
        pass
    return RedirectResponse(
        f'/get_user/{id}', 
        status_code=status.HTTP_302_FOUND)



      