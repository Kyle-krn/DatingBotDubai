from tortoise import Tortoise
from data.config import TORTOISE_ORM
from models import models


async def insert_place(id: int, title_interest: str):
    sql = f'''INSERT INTO dating_interest_place
              (id, title_interest)
              SELECT {id}, '{title_interest}'
              WHERE
              NOT EXISTS (
                SELECT id FROM dating_interest_place WHERE id = {id});'''
    return sql


async def insert_percent(id: int, description: str, percent: int):
    sql = f'''   INSERT INTO dating_percent
              (id, description, percent)
              SELECT {id}, '{description}', {percent}
              WHERE
              NOT EXISTS (
                SELECT id FROM dating_percent WHERE id = {id});	'''
    return sql

async def insert_purp(id: int, title_purp: str):
    sql = f'''   INSERT INTO dating_purpose
              (id, title_purp)
              SELECT {id}, '{title_purp}'
              WHERE
              NOT EXISTS (
                SELECT id FROM dating_purpose WHERE id = {id});	'''
    return sql


async def insert_martial_status(id: int, martial_status: str):
    sql = f'''   INSERT INTO marital_status
              (id, title_status)
              SELECT {id}, '{martial_status}'
              WHERE
              NOT EXISTS (
                SELECT id FROM marital_status WHERE id = {id});	'''
    return sql

async def init_data_db():
    conn = Tortoise.get_connection("default")
    place_1 = await insert_place(id=1, title_interest="Находится в Дубае")
    place_2 = await insert_place(id=2, title_interest="Планирует переезд в Дубай")
    place_3 = await insert_place(id=3, title_interest="Не в Дубае и не планирует туда переезд")
    
    percent_1 = await insert_percent(id=1, description="1ый и 2ой шаг", percent=30)
    percent_2 = await insert_percent(id=2, description="Возраст", percent=20)
    percent_3 = await insert_percent(id=3, description="Отклонение возраста", percent=2)
    percent_4 = await insert_percent(id=4, description="Совпадение детей", percent=10)
    percent_5 = await insert_percent(id=5, description="По возрасту ребенка", percent=1)
    percent_6 = await insert_percent(id=6, description="Хобби", percent=10)

    purp_1 = await insert_purp(id=1, title_purp="Дружба")
    purp_2 = await insert_purp(id=2, title_purp="Отношения")

    martial_status_1 = await insert_martial_status(id=1, martial_status="Женат/Замужем")
    martial_status_2 = await insert_martial_status(id=2, martial_status="В отношениях")
    martial_status_3 = await insert_martial_status(id=3, martial_status="Свободен(-на)")
    await conn.execute_script(f"""
                               {place_1}
                               {place_2}
                               {place_3}
                               {percent_1}
                               {percent_2}                               
                               {percent_3}
                               {percent_4}
                               {percent_5}
                               {percent_6}
                               {purp_1}
                               {purp_2}
                               {martial_status_1}
                               {martial_status_2}                               
                               {martial_status_3}                                                        
                               """)
    # await models.DatingInterestPlace.get_or_create(id=1, title_interest="Находится в Дубае")
    # await models.DatingInterestPlace.get_or_create(id=2, title_interest="Планирует переезд в Дубай")
    # await models.DatingInterestPlace.get_or_create(id=3, title_interest="Не в Дубае и не планирует туда переезд")

    # percent_1_2 = await models.DatingPercent.get_or_none(id=1, description="1ый и 2ой шаг")
    # if not percent_1_2:
    #     await models.DatingPercent.create(id=1, description="1ый и 2ой шаг", percent=30)
    # percent_age = await models.DatingPercent.get_or_none(id=2, description="Возраст")
    # if not percent_age:
    #     await models.DatingPercent.create(id=2, description="Возраст", percent=20) 
    # percent_step_age = await models.DatingPercent.get_or_none(id=3, description="Отклонение возраста")
    # if not percent_step_age:
    #     await models.DatingPercent.create(id=3, description="Отклонение возраста", percent=2)
    # percent_children = await models.DatingPercent.get_or_none(id=4, description="Совпадение детей")
    # if not percent_children:
    #     await models.DatingPercent.create(id=4, description="Совпадение детей", percent=20)
    # percent_children_age = await models.DatingPercent.get_or_none(id=5, description="По возрасту ребенка")
    # if not percent_children_age:
    #     await models.DatingPercent.create(id=5, description="По возрасту ребенка", percent=10)
    # percent_hobbies = await models.DatingPercent.get_or_none(id=6, description="Хобби")
    # if not percent_hobbies:
    #     await models.DatingPercent.create(id=6, description="Хобби", percent=10)
    
    