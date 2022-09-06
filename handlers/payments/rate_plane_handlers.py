from datetime import datetime
from loader import dp
from models import models
from aiogram import types
from keyboards.inline.payments_keyboards import rate_keyboard
from data import config
from dateutil.relativedelta import *

@dp.message_handler(commands=['rate_plane'])
@dp.message_handler(regexp="^(💸 Тарифные планы)$")
async def rate_plane_handler(message: types.Message):
    user = await models.UserModel.get(tg_id=message.chat.id)
    if user.end_registration is False:
        return await message.answer("Вы не закончили регистрацию")
    text = "Gold - 4,99 на 1 мес\n" \
           "- Неограниченные возможность видеть тех, кто ставит тебе лайки\n" \
           "- неограниченная возможность ставить лайки (без тарифа 3 лайка в день)\n\n" \
           "Super Like - 1$ за 10 суперлайков\n" \
           "- Твой суперлайк увидят сразу, даже если у пользователя нет тарифа Gold\n" \
           "- увеличивает вероятность взаимного лайнка в несколько раз!\n\n"

    if user.end_premium is not None:
        text += f"<b>Ваш Gold статус активен до {user.end_premium.strftime('%d.%m.%Y')}</b>"
    await message.answer(text=text, reply_markup=await rate_keyboard())


from loader import dp, bot
from aiogram import types
from tortoise.queryset import Q


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'buy')
async def payments_order(call: types.CallbackQuery):
    await call.message.delete()
    product = call.data.split(':')[1]
    if product == 'gold':
        count_mount = int(call.data.split(':')[2])
        prices = [types.LabeledPrice(label=f"Gold", amount=35000*count_mount)]
        payload = f"gold:{count_mount}"
    elif product == 'likes':
        count_likes = int(call.data.split(':')[2])
        prices = [types.LabeledPrice(label=f"{count_likes} суперлайков", amount=1000*count_likes)]
        payload = f"likes:{count_likes}"


    user = await models.UserModel.get(tg_id=call.message.chat.id)
    end_premium_date = datetime.utcnow() + relativedelta(months=+1)
    if user.end_premium is None:
        user.end_premium = end_premium_date
    else:
        user.end_premium = user.end_premium + relativedelta(months=+1)
    if payload.split(":")[0] == 'gold':
        count_mount = int(payload.split(':')[1])
        text = f"Благодарим вас за покупку, вы куппили {count_mount} месяц Gold!"
        count_likes = None
    elif payload.split(":")[0] == 'likes':
        count_likes = int(payload.split(':')[1])
        text = f"Благодарим вас за покупку, вы куппили {count_likes} суперлайков!"
        user.superlike_count += count_likes
        count_mount = None
    await user.save()
    # await models.UserSuccessPayments.create(user=user, 
    #                                        amount=total_amount/100, 
    #                                        product=payload.split(':')[0],
    #                                        count_mount=count_mount,
    #                                        count_likes=count_likes)

    await bot.delete_message(call.message.chat.id, call.message.message_id-1)
    await bot.send_message(
        call.message.chat.id,
        text,
        )
    
    # await bot.send_invoice(call.message.chat.id,
    #                        title='Ваша корзина',
    #                        description='Ваша корзина',
    #                        provider_token=config.PROVIDER_TOKEN,
    #                        currency='rub',
    #                        photo_url='https://thumbs.dreamstime.com/b/happy-shop-logo-design-template-shopping-designs-stock-134743566.jpg',
    #                        photo_height=512,  # !=0/None or picture won't be shown
    #                        photo_width=512,
    #                        photo_size=512, 
    #                        is_flexible=False,  # True If you need to set up Shipping Fee
    #                        prices=prices,
    #                        start_parameter='example',
    #                        need_name=False,
    #                        need_shipping_address=False,
    #                        need_phone_number=False,
    #                        payload=payload)





@dp.pre_checkout_query_handler(lambda query: True)
async def checkout(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                        error_message="Aliens tried to steal your card's CVV,"
                                                      " but we successfully protected your credentials,"
                                                      " try to pay again in a few minutes, we need a small rest.")


@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    total_amount = message.successful_payment.total_amount
    payload = message.successful_payment.invoice_payload
    user = await models.UserModel.get(tg_id=message.chat.id)
    end_premium_date = datetime.utcnow() + relativedelta(months=+1)
    if user.end_premium is None:
        user.end_premium = end_premium_date
    else:
        user.end_premium = user.end_premium + relativedelta(months=+1)
    if payload.split(":")[0] == 'gold':
        count_mount = int(payload.split(':')[1])
        text = f"Благодарим вас за покупку, вы куппили {count_mount} месяц Gold!"
        count_likes = None
    elif payload.split(":")[0] == 'likes':
        count_likes = int(payload.split(':')[1])
        text = f"Благодарим вас за покупку, вы куппили {count_likes} суперлайков!"
        user.superlike_count += count_likes
        count_mount = None
    await user.save()
    await models.UserSuccessPayments.create(user=user, 
                                           amount=total_amount/100, 
                                           product=payload.split(':')[0],
                                           count_mount=count_mount,
                                           count_likes=count_likes)

    await bot.delete_message(message.chat.id, message.message_id-1)
    await bot.send_message(
        message.chat.id,
        text,
        )
