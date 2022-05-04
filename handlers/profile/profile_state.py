from aiogram.dispatcher.filters.state import State, StatesGroup

class ProfileSettingsState(StatesGroup):
    city = State()
    bday = State()
    hobbies = State()
    children = State()
    avatar = State()