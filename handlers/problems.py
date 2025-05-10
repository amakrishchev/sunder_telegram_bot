from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup


class ProblemStates(StatesGroup):
    waiting_for_problem_type = State()
    waiting_for_description = State()
    waiting_for_media = State()
    waiting_for_receipt = State()


async def start_problems(message: types.Message):
    """
    Начало воронки проблем с товаром.
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        "Заводской брак",
        "Некомплект",
        "Вопрос по работе товара",
        "Возврат товара",
        "Назад"
    ]
    keyboard.add(*buttons)

    await message.answer(
        "Выберите тип проблемы:",
        reply_markup=keyboard
    )
    await ProblemStates.waiting_for_problem_type.set()


def register_problems_handlers(dp: Dispatcher):
    """
    Регистрирует обработчики для воронки проблем.
    """
    dp.register_message_handler(
        start_problems,
        text="⚠️ Проблема с товаром"
    )
