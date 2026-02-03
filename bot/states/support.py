from aiogram.fsm.state import State, StatesGroup


class SupportTicketStates(StatesGroup):
    waiting_for_subject = State()
    waiting_for_description = State()
    waiting_for_contact = State()
