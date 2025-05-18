from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    buttons = [
        "✅ Получить +2 года гарантии",
        "📖 Инструкции на товары",
        "⚠️ Проблема с товаром",
        "📨 Написать менеджеру"
    ]
    for button in buttons:
        builder.add(types.KeyboardButton(text=button))
    builder.adjust(1)

    await message.answer(
        "Добро пожаловать в бота Sunder для Ozon!",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("Справка по боту...")
