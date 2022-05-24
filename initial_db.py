from data.config import TORTOISE_ORM
from utils.postgres_func import init_postgres_func
from utils.postgres_func.insert_data_table import init_data_db
from tortoise import Tortoise, run_async

async def initial_db():
    await init_data_db()
    await init_postgres_func()


if __name__ == '__main__':
    run_async(initial_db)
