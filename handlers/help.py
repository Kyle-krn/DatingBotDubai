from loader import dp
from aiogram import types

@dp.message_handler(commands=['help'])
@dp.message_handler(regexp="^(🆘 Помощь)$")
async def command_help_handler(message: types.Message):
    text = "Как работает этот бот?\n"  \
        "Наш бот создан для тех кто эмигрировал или собирается эмигрировать в "  \
        "Дубай или приехал сюда отдохнуть. С ним вам легко будет "  \
        "найти новых друзей или построить отношения на новом месте.\n"  \
        "Все, что вам нужно делать, это ставить лайки другим пользователям, "  \
        "и когда ваши лайки совпадут, бот отправит вам контакты друг друга.\n"  \
        "Хотите, чтобы пользователь сразу получил ваш контакт? Просто отправьте "  \
        "ему суперлайк! Это увеличит ваши шансы на знакомство в 7 раз!\n"  \
        "С помощью тарифа Gold вы можете проверять тех, кому вы уже нравитесь, "  \
        "и лайкать их в ответ. С тарифом Gold вы гораздо быстрее "  \
        "найдете новых друзей или построите отношения!\n"  \
        "Купить суперлайки или тариф Gold можно в разделе “Платные тарифы”!"
    await message.answer(text)