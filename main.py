import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from app.handlers import router
from app.database.models import async_main

from config import Config


async def main():
    await async_main()

    bot = Bot(token=Config.TOKEN)
    dp = Dispatcher()
    dp.include_router(router)  # Routers

    bot_commands = [
        BotCommand(command='/start', description='Перезапустить бота'),
    ]
    await bot.set_my_commands(bot_commands)

    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')
