# states.py
from aiogram.fsm.state import State, StatesGroup

class OrderForm(StatesGroup):
    name = State()
    contact = State()
    address = State()