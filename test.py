from random import random
import random
import string
from tortoise import run_async, Tortoise
from data import config
from faker import Faker

from models import models
from utils.calculation_relations.calculations import calculation_new_user
fake = Faker()


async def generate_users():
    await Tortoise.init(config.TORTOISE_ORM)
    for i in range(1, 10000):
        print(i)
        id = random.randint(10000, 10000000)
        tg_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        male = bool(random.randint(0,1))
        name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        place = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))
        moving_to_dubai = bool(random.randint(0,1))
        bday = fake.date_time_between(start_date='-90y', end_date='-18y')
        children = random.choice([None,bool(random.randint(0,1))])
        tmz = 3
        interest_place_user = []
        # interest_place_user = await user.interest_place_companion.all()
        interest_place_4 = await models.DatingInterestPlace.get(id=1)
        interest_place_5 = await models.DatingInterestPlace.get(id=2)
        interest_place_6 = await models.DatingInterestPlace.get(id=3)
        ip = [interest_place_4, interest_place_5, interest_place_6]
        for i in range(1, random.randint(2,4)):
            interest_place_user.append(ip.pop(0))

        purp_friend = await models.PurposeOfDating.get(id=1)
        purp_sex = await models.PurposeOfDating.get(id=2)
        purp_user = [purp_friend, purp_sex]

        user = await models.UserModel.create(tg_id=id, 
                                    tg_username=tg_name, 
                                    male=male, 
                                    name=name, 
                                    place=place, 
                                    moving_to_dubai=moving_to_dubai, 
                                    birthday=bday, 
                                    children=children,
                                    tmz=tmz,
                                    verification=True,
                                    end_registration=True)
        for i in interest_place_user:
            await user.interest_place_companion.add(i)
        for i in purp_user:
            await user.purp_dating.add(i)
        await models.UserSearchSettings.create(user=user)
    # user = await models.UserModel.get(id=2)
    # await calculation_new_user(user)


if __name__ == '__main__':
    run_async(generate_users())