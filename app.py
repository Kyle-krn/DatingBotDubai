import asyncio
from aiogram import executor
from utils.misc import logging
from loader import dp, db, bot
from data.config import TORTOISE_ORM
import middlewares, filters, handlers
from tasks import scheduler
from utils.set_bot_commands import set_default_commands
from utils.postgres_func import init_postgres_func
from utils.postgres_func.insert_data_table import init_data_db

async def on_startup(dispatcher):
    await set_default_commands(dispatcher)
    await db.init(config=TORTOISE_ORM)
    asyncio.create_task(scheduler(bot))
    
async def on_shutdown(dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()

if __name__ == '__main__':
    """Для запуска бота через полинг"""
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)

