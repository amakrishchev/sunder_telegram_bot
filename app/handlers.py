from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.database.requests as rq

router = Router()


class Register(StatesGroup):
    name = State()
    age = State()
    number = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer(
        text="Добро пожаловать в магазин 'Sunder'",
        reply_markup=kb.main
    )


@router.message(F.text == 'Каталог')
async def catalog(message: Message):
    await message.answer(
        text='Выберите категорию товара',
        reply_markup=await kb.categories()
    )


@router.callback_query(F.data.startswith('category_'))
async def category(callback: CallbackQuery):
    await callback.answer('Вы выбрали категорию')
    await callback.message.answer(
        text='Выберите товар по категории',
        reply_markup=await kb.items(callback.data.split('_')[1])
    )


@router.callback_query(F.data.startswith('item_'))
async def item(callback: CallbackQuery):
    item_data = await rq.get_item(callback.data.split('_')[1])
    await callback.answer('Вы выбрали товар')
    await callback.message.answer(
        text=f'Название: {item_data.name}\nОписание: {item_data.description}\nЦена: {item_data.price}$',
        reply_markup=await kb.items(callback.data.split('_')[1])
    )
