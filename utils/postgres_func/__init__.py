from tortoise import Tortoise

from data.config import TORTOISE_ORM
from . import utils_func
from . import check_func
from . import calculation_func
from . import users_func
from . import insert_data_table
async def init_postgres_func():
    conn = Tortoise.get_connection("default")
    sql_sort_array = await utils_func.sort_array_func()
    sql_check_place_user = await utils_func.place_user_func()
    sql_target_place_condition = await utils_func.target_place_condition()
    sql_filter_place = await check_func.filter_place_func()
    sql_filter_purp = await check_func.filter_purp()
    sql_filter_min_max_age_children = await check_func.filter_min_max_age_children()
    sql_calculation_age = await calculation_func.calculation_age_func()
    sql_calculation_children = await calculation_func.calculation_children_func()
    sql_calculation_hobbies = await calculation_func.calculation_hobbies_func()
    sql_calculation_general = await calculation_func.calculation_general_func()
    sql_get_user_func = await users_func.sql_query_get_user_func()
    sql_get_users_func = await users_func.get_users_func()
    sql_calculation_users_func = await users_func.calculation_users()
    
    await conn.execute_script(f"""{sql_sort_array} 
                                  {sql_check_place_user}
                                  {sql_target_place_condition}
                                  {sql_filter_place}
                                  {sql_filter_purp}
                                  {sql_filter_min_max_age_children}
                                  {sql_calculation_age}
                                  {sql_calculation_children}
                                  {sql_calculation_hobbies}
                                  {sql_calculation_general}
                                  {sql_get_user_func}
                                  {sql_get_users_func}
                                  {sql_calculation_users_func}""")

