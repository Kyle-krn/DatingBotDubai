from aiogram.dispatcher.filters.state import State, StatesGroup


class SearchSettingsState(StatesGroup):
    age = State()
    children_age = State()