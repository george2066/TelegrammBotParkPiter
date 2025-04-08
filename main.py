import sys
import logging
import secrets

from handlers import qrcode_func
from hash import get_parking_payment
from io import BytesIO

import PIL.Image as Image
import asyncio
import json.scanner

from aiogram import Bot, Dispatcher, Router
from aiogram import F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.types import InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties


logging.basicConfig(level=logging.INFO)

bot = Bot(token=secrets.TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router_reg = Router()
dp.include_router(router_reg)


photo_ids = []





@dp.message(CommandStart())
async def check_payment(message: Message):
    kb = [
        [
            KeyboardButton(text="Показать ТАРИФ"),
            KeyboardButton(text="Показать ЗАДОЛЖЕННОСТЬ")
        ],
        [KeyboardButton(text="Оплатить ЗАДОЛЖЕННОСТЬ")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb)
    await message.answer(f"Добро пожаловать!\nВыберете опцию:", reply_markup=keyboard)

@dp.message(F.text == "Показать ТАРИФ")
async def show_tariff(message: Message):
    await message.reply("Отличный выбор!")

@dp.message(F.text == "Показать ЗАДОЛЖЕННОСТЬ")
async def show_arrears(message: Message):
    await message.reply("Пожалуйста, введите код для проверки оплаты или пришлите QR-код вашего талона.")

@dp.message(F.text == "Оплатить ЗАДОЛЖЕННОСТЬ")
async def pay_arrears(message: Message):
    await message.reply("Отличный выбор!")


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
    bot = Bot(token=secrets.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен пользователем")
