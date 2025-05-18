from aiogram import types, Dispatcher
from services.google_sheets import GoogleSheetsService


async def start_instructions(message: types.Message):
    """
    Начало воронки получения инструкций.
    """
    categories = await GoogleSheetsService.get_product_categories()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*categories)
    keyboard.add("Назад")

    await message.answer(
        "Выберите категорию товара:",
        reply_markup=keyboard
    )


def register_instructions_handlers(dp: Dispatcher):
    """
    Регистрирует обработчики для воронки инструкций.
    """
    dp.register_message_handler(
        start_instructions,
        text="📖 Инструкции на товары"
    )
