import asyncio
from aiogram import Bot, Dispatcher
import aiogram.fsm.storage.memory as MemoryStorage
# from aiogram.contrib.fsm_storage.memory import MemoryStorage
from handlers import register_handlers
from config import load_config


async def main():
    config = load_config()
    bot = Bot(token=config.telegram_token)
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    register_handlers(dp)  # Регистрация всех обработчиков

    try:
        await dp.start_polling()
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
