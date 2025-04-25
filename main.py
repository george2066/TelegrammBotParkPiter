import os
import re
import sys
import logging

import secret

from handlers import read_QR, get_parking, get_link_for_payed, free_tariff, json_error, get_file_path_to_photo, \
    get_quantity_captures
from io import BytesIO

import PIL.Image as Image
import asyncio
import json.scanner

from aiogram import F
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, FSInputFile
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

logging.basicConfig(level=logging.INFO)

bot = Bot(token=secret.TOKEN)
dp = Dispatcher(storage=MemoryStorage())

@dp.message(CommandStart())
async def check_payment(message: Message):
    kb = [
        [
            KeyboardButton(text="Показать ТАРИФ"),
            KeyboardButton(text="Показать ЗАДОЛЖЕННОСТЬ")
        ],
        [KeyboardButton(text="Сфотографировать ШЛАГБАУМ")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb)
    await message.answer(f"{'Добро пожаловать!\n' if message.text == '/start' else ''}Выберете опцию:",
                         reply_markup=keyboard)

@dp.message(F.text == "Показать ТАРИФ")
async def show_tariff(message: Message):
    await message.reply('''
Тарифы:

Цена ЧАС: ... руб.
Цена ДЕНЬ: ... руб.
Цена МЕСЯЦ: ... руб.
    ''')

@dp.callback_query(lambda c: c.data == 'back')
async def back_handler(callback_query: CallbackQuery):
    await callback_query.answer()
    await check_payment(callback_query.message)

@dp.message(F.text == "Показать ЗАДОЛЖЕННОСТЬ")
async def show_arrears(message: Message):
    await message.reply("Пожалуйста, введите код для проверки оплаты или пришлите QR-код вашего талона.")
@dp.message(F.text == "Сфотографировать ШЛАГБАУМ")
async def choose_captures(message: Message):
    try:
        quantity_captures = get_quantity_captures()
        kb = [[InlineKeyboardButton(text=f'Камера №{n + 1}', callback_data=f'camera_{n + 1}')] for n in range(quantity_captures)]
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
        await message.answer(text='Выберите камеру:', reply_markup=keyboard)
    except Exception as e:
        await message.answer(text=f'⚠️В драйвере отсутствуют камеры, подключённые к вашему компьютеру.⚠️\nОбратитесь за поддержкой в компанию CardPark:\nhttps://cardpark.su/\n\nОшибка:\n\n{e}')
@dp.message(F.photo)
async def process_photo(message: Message):
    photo_data = message.photo[-1]
    file_id = photo_data.file_id

    try:
        file = await bot.get_file(file_id)
        file_path = file.file_path
        image_data = await bot.download_file(file_path)
        image = Image.open(BytesIO(image_data.getvalue()))
        try:
            link =  read_QR(image)
        except Exception as e:
            await message.answer(json_error)
        ticket_id = re.findall(r"\[(.*?)\]", link)[0]
        kb = []
        if not free_tariff(ticket_id):
            kb.append([InlineKeyboardButton(text="Оплатить", url=get_link_for_payed(ticket_id))])
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
        await handler_free_tariff(message, ticket_id, keyboard)
    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")
@dp.message(F.text)
async def process_ticket_id(message: Message):
    kb = []
    ticket_id = message.text
    if not free_tariff(ticket_id):
        kb.append([InlineKeyboardButton(text="Оплатить", url=get_link_for_payed(ticket_id))])
    kb.append([InlineKeyboardButton(text="Назад", callback_data="back")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    if keyboard != json_error:
        await handler_free_tariff(message, ticket_id, keyboard)
    else:
        await message.answer(json_error)
@dp.callback_query(lambda c: c.data == 'back')
async def back_handler(callback_query: CallbackQuery):
    await callback_query.answer()
    await check_payment(callback_query.message)

@dp.callback_query(lambda c: c.data and c.data.startswith('camera_'))
async def show_photo(callback_query: CallbackQuery):
    camera_number = int(callback_query.data.split('_')[1])
    file_path = str(get_file_path_to_photo(camera_number))
    photo = FSInputFile(path=file_path)
    await callback_query.message.answer_photo(photo=photo)

async def handler_free_tariff(message: Message, ticket_id: str, keyboard: InlineKeyboardMarkup):
    try:
        string = get_parking(ticket_id)
        if free_tariff(ticket_id):
            await message.answer(string)
            await check_payment(message)
        else:
            if string == json_error:
                await message.answer(string)
                await check_payment(message)
            else:
                await message.answer(string, reply_markup=keyboard)
    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")

async def main() -> None:
    bot = Bot(token=secret.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен разработчиком")