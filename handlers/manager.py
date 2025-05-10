from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.filters.state import State, StatesGroup


class ManagerStates(StatesGroup):
    waiting_for_question = State()
    waiting_for_contact = State()


async def start_manager(message: types.Message):
    """
    Начало воронки связи с менеджером.
    """
    await message.answer(
        "Опишите ваш вопрос менеджеру:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await ManagerStates.waiting_for_question.set()


async def process_question(message: types.Message, state: FSMContext):
    """
    Обработка вопроса для менеджера.
    """
    await state.update_data(question=message.text)
    await message.answer(
        "Введите ваше имя и телефон для связи:\n"
        "Формат: Иван Иванов +79001234567"
    )
    await ManagerStates.waiting_for_contact.set()


def register_manager_handlers(dp: Dispatcher):
    """
    Регистрирует обработчики для воронки связи с менеджером.
    """
    dp.register_message_handler(
        start_manager,
        text="📨 Написать менеджеру"
    )
    dp.register_message_handler(
        process_question,
        state=ManagerStates.waiting_for_question
    )
