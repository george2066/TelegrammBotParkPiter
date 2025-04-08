import sys
import logging
import secrets

from Qrreader import qrcode_func
from hash import get_parking_payment
from io import BytesIO

import PIL.Image as Image
import asyncio
import json.scanner
import requests

from aiogram import Bot, Dispatcher, FlagGenerator, Router
from aiogram import MagicFilter
from aiogram import F
from aiogram.filters import (
    Command,
    CommandStart,
    ExceptionMessageFilter,
    ExceptionTypeFilter,
)
from aiogram.types import BotCommand, CallbackQuery, Chat, Dice, Poll, TelegramObject, Message, Invoice, Document, File
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup,\
    KeyboardButton, ReplyKeyboardRemove, ReplyKeyboardMarkup
from aiogram.fsm.storage.base import BaseStorage, BaseEventIsolation, StorageKey, State, Union, AsyncGenerator
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from aiogram.types.callback_query import CallbackQuery
from aiogram.types.user import User
from aiogram.enums import ParseMode
from aiogram.utils.chat_action import ChatActionSender
from aiogram.client.default import DefaultBotProperties
from aiogram import types
from aiogram.utils.chat_action import ChatActionSender


logging.basicConfig(level=logging.INFO)

bot = Bot(token=secrets.TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router_reg = Router()
dp.include_router(router_reg)


photo_ids = []


def ticket_kb():
    keyboard=ReplyKeyboardMarkup(keyboard =[
        [KeyboardButton(text='Ввести номер')]
    ], resize_keyboard=True)
    return keyboard

def sendPhoto_kb():
    Keyboard = ReplyKeyboardMarkup(keyboard=[
        [InlineKeyboardButton(text='Отправить фото', callback_data='sendPhoto')]
    ])
    return Keyboard


@dp.message(CommandStart())
async def check_payment(message: Message):
    # Просим пользователя ввести ticket_id
    await message.answer("Пожалуйста, введите код для проверки оплаты")
    await message.delete()

@dp.message(lambda message: message.text)
async def process_ticket_id(message: Message):
    ticket_id = message.text
    try:
        # Вызываем функцию с полученным ticket_id
        amount = get_parking_payment(ticket_id)

        # Отправляем результат пользователю
        await message.answer(f"Сумма оплаты для кода, который вы ввели: {amount} руб.")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")
        


@router_reg.message(F.photo)
async def process_photo(message: Message):
    photo_data = message.photo[-1]
    file_id = photo_data.file_id

    try:
        file = await bot.get_file(file_id)
        file_path = file.file_path
        image_data = await bot.download_file(file_path)
        # Создаем объект Image из загруженных данных
        image = Image.open(BytesIO(image_data.getvalue()))
        link =  qrcode_func(image)
        await message.answer(f"Сумма оплаты для кода, который вы ввели: {link} руб.")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")






async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
