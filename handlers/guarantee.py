from aiogram import Router, F, types, Bot
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta
from services.pdf_generator import generate_guarantee_certificate
# from services.receipt_analyzer import analyze_receipt
from services.receipt_analyzer import receipt_analyzer
from services.google_sheets import GoogleSheetsClient  # add_guarantee_request
from config import load_config
import os
import logging

router = Router()
config = load_config()
logger = logging.getLogger(__name__)


class GuaranteeStates(StatesGroup):
    waiting_product_link = State()
    waiting_device_type = State()
    waiting_contact = State()
    waiting_receipt = State()


@router.message(F.text == "✅ Получить +2 года гарантии")
async def start_guarantee(message: types.Message, state: FSMContext):
    """Начало воронки гарантии"""
    await state.clear()
    await message.answer(
        "🛠️ <b>Оформление расширенной гарантии +2 года</b>\n\n"
        "Пришлите ссылку на товар с Ozon в формате:\n"
        "<code>https://www.ozon.ru/product/12345678/</code>",
        parse_mode="HTML",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(GuaranteeStates.waiting_product_link)


@router.message(GuaranteeStates.waiting_product_link, F.text)
async def process_product_link(message: types.Message, state: FSMContext):
    """Обработка ссылки на товар"""
    if not any(domain in message.text for domain in ["ozon.ru/product/", "ozon.ru/category/"]):
        await message.answer("❌ Это не похоже на ссылку Ozon. Попробуйте ещё раз:")
        return

    await state.update_data(product_link=message.text)

    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="📱 Android"),
        types.KeyboardButton(text="🍏 iOS"),
        types.KeyboardButton(text="💻 ПК")
    )
    builder.row(types.KeyboardButton(text="❌ Отмена"))

    await message.answer(
        "📱 <b>Выберите ваше устройство</b>\n"
        "Мы отправим видеоинструкцию по оформлению гарантии:",
        parse_mode="HTML",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )
    await state.set_state(GuaranteeStates.waiting_device_type)


@router.message(GuaranteeStates.waiting_device_type, F.text.in_(["📱 Android", "🍏 iOS", "💻 ПК"]))
async def process_device_type(message: types.Message, state: FSMContext):
    """Обработка выбора устройства"""
    await state.update_data(device_type=message.text)
    await message.answer(
        "📞 <b>Введите ваши контактные данные</b>\n\n"
        "Формат: <code>Иван Иванов +79001234567</code>\n"
        "Мы свяжемся для подтверждения гарантии:",
        parse_mode="HTML",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(GuaranteeStates.waiting_contact)


@router.message(GuaranteeStates.waiting_contact, F.text)
async def process_contact(message: types.Message, state: FSMContext):
    """Обработка контактных данных"""
    try:
        name, phone = message.text.rsplit(maxsplit=1)
        if not phone.startswith("+"):
            raise ValueError
    except ValueError:
        await message.answer("❌ Неверный формат. Введите как в примере: <code>Иван Иванов +79001234567</code>", parse_mode="HTML")
        return

    await state.update_data(client_name=name, client_phone=phone)
    await message.answer(
        "🧾 <b>Пришлите фото чека о покупке</b>\n\n"
        "Убедитесь, что на фото видны:\n"
        "- Дата покупки\n"
        "- Название товара\n"
        "- Артикул",
        parse_mode="HTML"
    )
    await state.set_state(GuaranteeStates.waiting_receipt)


@router.message(GuaranteeStates.waiting_receipt, F.photo)
async def process_receipt_photo(
    message: types.Message,
    state: FSMContext,
    bot: Bot
):
    """Обработка фото чека"""
    try:
        # Скачиваем фото
        file_id = message.photo[-1].file_id
        file = await bot.get_file(file_id)
        receipt_path = f"temp/receipt_{message.from_user.id}.jpg"
        await bot.download_file(file.file_path, receipt_path)

        # Анализируем чек
        receipt_data = await receipt_analyzer(receipt_path)
        if not receipt_data:
            raise ValueError("Не удалось распознать чек")

        # Получаем все данные
        user_data = await state.get_data()
        purchase_date = datetime.strptime(receipt_data.purchase_date, "%d.%m.%Y")
        warranty_end = (purchase_date + timedelta(days=365*2)).strftime("%d.%m.%Y")
        order_id = f"{message.from_user.id}-{datetime.now().strftime('%Y%m%d')}"
        promo_code = f"SUNDER-{order_id}"

        # Генерируем сертификат
        pdf_data = {
            "order_id": order_id,
            "client_name": user_data['client_name'],
            "product_name": receipt_data.product_name,
            "purchase_date": receipt_data.purchase_date,
            "warranty_end": warranty_end
        }
        pdf_path = generate_guarantee_certificate(pdf_data)

        # Сохраняем в Google Sheets
        await GoogleSheetsClient({
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

        # Отправляем результат
        with open(pdf_path, 'rb') as pdf_file:
            await message.answer_document(
                pdf_file,
                caption=f"✅ <b>Гарантия оформлена!</b>\n\n"
                       f"🔹 Товар: {receipt_data.product_name}\n"
                       f"🔹 Гарантия до: {warranty_end}\n\n"
                       f"🎁 <b>Промокод на 15% скидку:</b> <code>{promo_code}</code>",
                parse_mode="HTML"
            )

        await message.answer(
            "Пожалуйста, оставьте отзыв на Ozon:\n"
            f"{user_data['product_link']}#comments"
        )

    except Exception as e:
        logger.error(f"Ошибка обработки гарантии: {e}")
        await message.answer(
            "❌ Произошла ошибка. Попробуйте отправить чек ещё раз или свяжитесь с менеджером."
        )
    finally:
        await state.clear()
        if os.path.exists(receipt_path):
            os.remove(receipt_path)


@router.message(StateFilter(GuaranteeStates), F.text == "❌ Отмена")
async def cancel_guarantee(message: types.Message, state: FSMContext):
    """Отмена оформления гарантии"""
    await state.clear()
    await message.answer(
        "❌ Оформление гарантии отменено",
        reply_markup=types.ReplyKeyboardRemove()
    )
