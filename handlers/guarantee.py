from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from services.google_sheets import add_guarantee_request


class GuaranteeStates(StatesGroup):
    waiting_for_link = State()
    waiting_for_device = State()
    waiting_for_contact = State()
    waiting_for_receipt = State()


async def start_guarantee(message: types.Message):
    await message.answer(
        "Привет! Для оформления гарантии отправь ссылку на товар."
    )
    await GuaranteeStates.waiting_for_link.set()  


async def process_link(message: types.Message, state: FSMContext):
    await state.update_data(link=message.text)  
    await message.answer(
        "Выбери устройство для инструкции:",
        reply_markup=get_device_keyboard()
    )
    await GuaranteeStates.waiting_for_device.set()


# Далее аналогично для остальных шагов...
def register_guarantee_handlers(dp: Dispatcher):
    dp.register_message_handler(
        start_guarantee,
        text="✅ Получить +2 года гарантии"
    )
    dp.register_message_handler(
        process_link,
        state=GuaranteeStates.waiting_for_link
    )
