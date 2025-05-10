from aiogram import types, Dispatcher
from aiogram.filters import Command


async def cmd_start(message: types.Message):
    """
    Обработчик команды /start.
    Показывает главное меню с кнопками.
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        "✅ Получить +2 года гарантии",
        "📖 Инструкции на товары",
        "⚠️ Проблема с товаром",
        "📨 Написать менеджеру"
    ]
    keyboard.add(*buttons)

    await message.answer(
        "Добро пожаловать в бота Sunder для Ozon!\n"
        "Выберите нужный вариант:",
        reply_markup=keyboard
    )


async def cmd_help(message: types.Message):
    """Обработчик команды /help."""
    await message.answer(
        "Помощь по боту:\n"
        "✅ Гарантия - оформите расширенную гарантию\n"
        "📖 Инструкции - получите инструкции к товарам\n"
        "⚠️ Проблемы - сообщите о проблеме с товаром\n"
        "📨 Менеджер - свяжитесь с менеджером"
    )


def register_common_handlers(dp: Dispatcher):
    """
    Регистрирует общие обработчики команд.
    """
    dp.register_message_handler(cmd_start, Command("start"))
    dp.register_message_handler(cmd_help, Command("help"))
