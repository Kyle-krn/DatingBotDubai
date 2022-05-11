import asyncio
from aiogram import executor
from utils.misc import logging
from loader import dp, db, bot
from data.config import TORTOISE_ORM
import middlewares, filters, handlers
from tasks import scheduler
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    # Устанавливаем дефолтные команды
    await set_default_commands(dispatcher)
    await db.init(config=TORTOISE_ORM)
    asyncio.create_task(scheduler(bot))
    
async def on_shutdown(dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


    # Уведомляет про запуск
    # await on_startup_notify(dispatcher)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)

