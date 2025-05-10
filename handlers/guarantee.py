from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from services.google_sheets import GoogleSheetsService
from services.receipt_analyzer import DeepSeekAnalyzer
from services.pdf_generator import PDFGenerator
from config import load_config
from datetime import datetime, timedelta
import os
import logging
# from typing import Dict, Optional

logger = logging.getLogger(__name__)
config = load_config()


class GuaranteeStates(StatesGroup):
    waiting_for_link = State()
    waiting_for_device = State()
    waiting_for_contact = State()
    waiting_for_receipt = State()


# Инициализация сервисов
google_sheets = GoogleSheetsService(config.google_sheets_credentials)
pdf_generator = PDFGenerator()


def get_device_keyboard() -> types.ReplyKeyboardMarkup:
    """Создает клавиатуру для выбора устройства"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Android", "iOS", "ПК", "Отмена"]
    keyboard.add(*buttons)
    return keyboard


def get_cancel_keyboard() -> types.ReplyKeyboardMarkup:
    """Клавиатура с кнопкой отмены"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Отмена")
    return keyboard


async def start_guarantee(message: types.Message):
    """
    Начало воронки оформления гарантии
    """
    await message.answer(
        "🛡️ <b>Оформление расширенной гарантии +2 года</b>\n\n"
        "Пришлите ссылку на товар на Ozon в формате:\n"
        "<code>https://www.ozon.ru/product/12345678/</code>",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )
    await GuaranteeStates.waiting_for_link.set()


async def process_link(message: types.Message, state: FSMContext):
    """
    Обработка ссылки на товар
    """
    if message.text.lower() == "отмена":
        await cancel_process(message, state)
        return

    if not ("ozon.ru/product/" in message.text or "ozon.ru/category/" in message.text):
        await message.answer("❌ Это не похоже на ссылку Ozon. Попробуйте еще раз:")
        return

    await state.update_data(product_link=message.text)

    await message.answer(
        "📱 <b>Выберите ваше устройство</b>\n"
        "Мы отправим видеоинструкцию по оформлению гарантии:",
        parse_mode="HTML",
        reply_markup=get_device_keyboard()
    )
    await GuaranteeStates.waiting_for_device.set()


async def process_device(message: types.Message, state: FSMContext):
    """
    Обработка выбора устройства
    """
    if message.text == "Отмена":
        await cancel_process(message, state)
        return

    if message.text not in ["Android", "iOS", "ПК"]:
        await message.answer("Пожалуйста, выберите вариант из предложенных:")
        return

    await state.update_data(device=message.text)

    await message.answer(
        "📞 <b>Введите ваши контактные данные</b>\n\n"
        "Формат: <code>Иван Иванов +79001234567</code>\n"
        "Мы свяжемся с вами для подтверждения гарантии",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )
    await GuaranteeStates.waiting_for_contact.set()


async def process_contact(message: types.Message, state: FSMContext):
    """
    Обработка контактных данных
    """
    if message.text.lower() == "отмена":
        await cancel_process(message, state)
        return

    try:
        name, phone = message.text.rsplit(maxsplit=1)
        if not phone.startswith("+"):
            raise ValueError
    except ValueError:
        await message.answer("❌ Неверный формат. Введите как показано в примере:")
        return

    await state.update_data(client_name=name, client_phone=phone)

    await message.answer(
        "🧾 <b>Пришлите фото чека о покупке</b>\n\n"
        "Сфотографируйте или загрузите скриншот чека.\n"
        "Убедитесь, что видны:\n"
        "- Дата покупки\n"
        "- Название товара\n"
        "- Артикул",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )
    await GuaranteeStates.waiting_for_receipt.set()


async def process_receipt_photo(message: types.Message, state: FSMContext):
    """
    Обработка фото чека через DeepSeek API
    """
    if not message.photo:
        await message.answer("Пожалуйста, отправьте фото чека:")
        return

    try:
        # Сохраняем фото
        file_id = message.photo[-1].file_id
        file = await message.bot.get_file(file_id)
        file_path = f"temp/receipt_{message.from_user.id}.jpg"
        await file.download(destination_file=file_path)

        # Анализируем чек
        analyzer = DeepSeekAnalyzer(config.deepseek_api_key)
        receipt_data = await analyzer.analyze_receipt(file_path)

        if not receipt_data:
            raise ValueError("Не удалось распознать чек")

        # Получаем все данные из state
        user_data = await state.get_data()

        # Рассчитываем дату окончания гарантии (+2 года)
        purchase_date = datetime.strptime(receipt_data.purchase_date, "%d.%m.%Y")
        warranty_end = (purchase_date + timedelta(days=365*2)).strftime("%d.%m.%Y")

        # Генерируем промокод
        promo_code = f"SUNDER-{message.from_user.id}-{purchase_date.strftime('%Y%m')}"

        # Генерируем сертификат гарантии
        pdf_data = {
            "client_name": user_data['client_name'],
            "product_name": receipt_data.product_name,
            "purchase_date": receipt_data.purchase_date,
            "warranty_end": warranty_end,
            "order_id": f"{message.from_user.id}-{datetime.now().strftime('%Y%m%d')}"
        }
        pdf_path = pdf_generator.generate_guarantee_certificate(pdf_data)

        # Сохраняем данные в Google Sheets
        await google_sheets.add_guarantee_request({
            "name": user_data['client_name'],
            "phone": user_data['client_phone'],
            "product_link": user_data['product_link'],
            "article": receipt_data.article,
            "product_name": receipt_data.product_name,
            "purchase_date": receipt_data.purchase_date,
            "warranty_end": warranty_end,
            "promo_code": promo_code,
            "status": "completed"
        })

        # Отправляем пользователю результаты
        with open(pdf_path, 'rb') as pdf_file:
            await message.answer_document(
                pdf_file,
                caption="✅ <b>Ваша расширенная гарантия оформлена!</b>\n\n"
                        f"🔹 Товар: {receipt_data.product_name}\n"
                        f"🔹 Гарантия до: {warranty_end}\n\n"
                        f"🎁 <b>Ваш промокод на скидку 15%:</b> <code>{promo_code}</code>\n\n"
                        "Спасибо за покупку!",
                parse_mode="HTML"
            )

        # Предлагаем оставить отзыв
        await message.answer(
            "Пожалуйста, оставьте отзыв на Ozon:\n"
            f"{user_data['product_link']}#comments",
            reply_markup=types.ReplyKeyboardRemove()
        )

    except Exception as e:
        logger.error(f"Error processing receipt: {e}")
        await message.answer(
            "❌ Произошла ошибка при обработке чека. Попробуйте отправить более четкое фото или свяжитесь с менеджером.",
            reply_markup=get_cancel_keyboard()
        )
    finally:
        # Очищаем state
        await state.finish()
        # Удаляем временные файлы
        if os.path.exists(file_path):
            os.remove(file_path)


async def cancel_process(message: types.Message, state: FSMContext):
    """
    Отмена текущего процесса
    """
    await message.answer(
        "❌ Процесс оформления гарантии отменен",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.finish()


def register_guarantee_handlers(dp: Dispatcher):
    """
    Регистрация обработчиков для воронки гарантии
    """
    dp.register_message_handler(
        start_guarantee,
        text="✅ Получить +2 года гарантии",
        state="*"
    )
    dp.register_message_handler(
        process_link,
        state=GuaranteeStates.waiting_for_link
    )
    dp.register_message_handler(
        process_device,
        state=GuaranteeStates.waiting_for_device
    )
    dp.register_message_handler(
        process_contact,
        state=GuaranteeStates.waiting_for_contact
    )
    dp.register_message_handler(
        process_receipt_photo,
        content_types=types.ContentType.PHOTO,
        state=GuaranteeStates.waiting_for_receipt
    )
    dp.register_message_handler(
        cancel_process,
        text="Отмена",
        state="*"
    )
