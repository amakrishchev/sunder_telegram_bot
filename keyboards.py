import telebot


def main_menu():
    """Главное меню с кнопками"""
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("✅ Гарантия +2 года")
    markup.row("📖 Инструкции", "⚠️ Проблема")
    markup.row("📨 Менеджер")
    return markup


def cancel_button():
    """Кнопка отмены"""
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("❌ Отмена")
    return markup


def device_keyboard():
    """Кнопка отмены"""
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Android")
    markup.row("iOS")
    markup.row("Другое")
    return markup
