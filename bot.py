import telebot
from config import config
from handlers import register_handlers

# Инициализация бота
bot = telebot.TeleBot(config.TOKEN)

# Регистрация обработчиков
register_handlers(bot)

# Запуск бота
if __name__ == "__main__":
    print("🤖 Бот запущен!")
    bot.infinity_polling()
