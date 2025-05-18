import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from config import load_config
import redis.asyncio as redis


async def main():
    # Загрузка конфига
    config = load_config()

    # Подключение к Redis
    redis_client = redis.from_url(config.REDIS_URL)
    try:
        await redis_client.ping()
        print("✅ Успешное подключение к Redis")
    except Exception as e:
        print(f"❌ Ошибка Redis: {e}")
        return

    # Инициализация бота
    bot = Bot(token=config.TELEGRAM_TOKEN)
    dp = Dispatcher(storage=RedisStorage(redis=redis_client))

    # Регистрация обработчиков
    from handlers import routers
    for router in routers:
        dp.include_router(router)

    try:
        print("🤖 Бот запущен")
        await dp.start_polling(bot)
    finally:
        await redis_client.close()


if __name__ == "__main__":
    asyncio.run(main())
