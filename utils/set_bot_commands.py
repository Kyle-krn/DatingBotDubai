from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("dating", "Найти пару"),
            types.BotCommand("likes", "Симпатии"),
            types.BotCommand("profile", "Профиль"),
            types.BotCommand("settings", "Настройки"),
            types.BotCommand("rate_plane", "Тарифный план"),
            types.BotCommand("help", "Помощь")
        ]
    )
