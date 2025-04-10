import sys
import logging

import secrets

from handlers import read_QR, get_parking, get_link_for_payed, free_tariff
from io import BytesIO

import PIL.Image as Image
import asyncio
import json.scanner

from aiogram import Bot, Dispatcher, Router
from aiogram import F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

logging.basicConfig(level=logging.INFO)

bot = Bot(token=secrets.TOKEN)
dp = Dispatcher(storage=MemoryStorage())


def get_kb(ticket_id):
    kb = []
    if not free_tariff(ticket_id):
        kb = [
            [InlineKeyboardButton(text="Оплатить", url=get_link_for_payed(ticket_id))],
        ]
    kb.append([InlineKeyboardButton(text="Назад", callback_data="back")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard

@dp.message(CommandStart())
async def check_payment(message: Message):
    kb = [
        [KeyboardButton(text="Показать ТАРИФ")],
        [KeyboardButton(text="Показать ЗАДОЛЖЕННОСТЬ")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb)
    await message.answer(f"{'Добро пожаловать!\n' if message.text == '/start' else ''}Выберете опцию:",
                         reply_markup=keyboard)
@dp.callback_query(lambda c: c.data == 'back')
async def back_handler(callback_query: CallbackQuery):
    await callback_query.answer()
    await check_payment(callback_query.message)
@dp.message(F.text == "Показать ТАРИФ")
async def show_tariff(message: Message):
    await message.reply('''
Тарифы:

Цена ЧАС: ... руб.
Цена ДЕНЬ: ... руб.
Цена МЕСЯЦ: ... руб.
    ''')
@dp.message(F.text == "Показать ЗАДОЛЖЕННОСТЬ")
async def show_arrears(message: Message):
    await message.reply("Пожалуйста, введите код для проверки оплаты или пришлите QR-код вашего талона.")
@dp.message(F.photo)
async def process_photo(message: Message):
    photo_data = message.photo[-1]
    file_id = photo_data.file_id
    keyboard = get_kb()

    try:
        file = await bot.get_file(file_id)
        file_path = file.file_path
        image_data = await bot.download_file(file_path)
        image = Image.open(BytesIO(image_data.getvalue()))
        link = read_QR(image)
        start = link.find('[')
        end = link.find(']')
        ticket_id = link[start:end]

        if free_tariff(ticket_id):
            await check_payment(message)
        else:
            await message.answer(link, reply_markup=keyboard)
    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")
@dp.message(F.text)
async def process_ticket_id(message: Message):
    keyboard = get_kb(message.text)
    ticket_id = message.text
    try:
        string = get_parking(ticket_id)
        if free_tariff(ticket_id):
            await message.answer(string)
            await check_payment(message)
        else:
            await message.answer(string, reply_markup=keyboard)
    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")
async def main() -> None:
    bot = Bot(token=secrets.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен разработчиком")
