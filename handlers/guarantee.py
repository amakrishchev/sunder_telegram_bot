from telebot import TeleBot
from telebot.types import Message
from keyboards import cancel_button, device_keyboard


class GuaranteeStates:
    PRODUCT_LINK = 1
    DEVICE_TYPE = 2
    CONTACT = 3
    RECEIPT = 4


def register_guarantee_handlers(bot: TeleBot, user_states: dict):
    @bot.message_handler(func=lambda m: m.text == "✅ Гарантия +2 года")
    def start_guarantee(message: Message):
        user_states[message.chat.id] = GuaranteeStates.PRODUCT_LINK
        bot.send_message(
            message.chat.id,
            "🔗 Пришлите ссылку на товар с Ozon...",
            reply_markup=cancel_button()
        )

    @bot.message_handler(func=lambda m: user_states.get(m.chat.id) == GuaranteeStates.PRODUCT_LINK)
    def process_link(message: Message):
        if "ozon.ru/product/" not in message.text:
            bot.send_message(message.chat.id, "❌ Это не ссылка Ozon!")
            return
        bot.send_message(message.chat.id, "Круто, именно то, что нужно")

        user_states[message.chat.id] = GuaranteeStates.DEVICE_TYPE
        bot.send_message(
            message.chat.id,
            "📱 Выберите устройство:",
            reply_markup=device_keyboard()
        )
