# import telebot
from keyboards import main_menu


def register_start_handlers(bot):
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        bot.reply_to(
            message,
            "👋 Добро пожаловать в бота Sunder!\nВыберите действие:",
            reply_markup=main_menu()
        )

    @bot.message_handler(commands=['help'])
    def send_help(message):
        bot.reply_to(message, "ℹ️ Помощь по боту...")
