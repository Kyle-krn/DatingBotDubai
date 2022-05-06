from aiogram.dispatcher.filters.state import State, StatesGroup
from requests import request
import requests

class ProfileSettingsState(StatesGroup):
    city = State()
    bday = State()
    hobbies = State()
    children = State()
    avatar = State()



