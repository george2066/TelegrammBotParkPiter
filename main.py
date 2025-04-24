import os
import re
import sys
import logging

import secret

from handlers import read_QR, get_parking, get_link_for_payed, free_tariff, get_JSON, json_error
from io import BytesIO

import PIL.Image as Image
import asyncio
import json.scanner

from aiogram import F
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, LabeledPrice
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types.pre_checkout_query import PreCheckoutQuery

logging.basicConfig(level=logging.INFO)

bot = Bot(token=secret.TOKEN)
dp = Dispatcher(storage=MemoryStorage())


payment_button = [InlineKeyboardButton(text="Оплатить", callback_data='payed')]


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

    try:
        file = await bot.get_file(file_id)
        file_path = file.file_path
        image_data = await bot.download_file(file_path)
        image = Image.open(BytesIO(image_data.getvalue()))
        try:
            link = read_QR(image)
        except Exception as e:
            await message.answer(json_error)
        ticket_id = re.findall(r"\[(.*?)\]", link)[0]
        kb = []
        if not free_tariff(ticket_id):
            kb.append(payment_button)
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
        await handler_free_tariff(message, ticket_id, keyboard)
    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")


@dp.message(F.text)
async def process_ticket_id(message: Message):
    kb = []
    ticket_id = message.text
    if not free_tariff(ticket_id):
        kb.append(payment_button)
    kb.append([InlineKeyboardButton(text="Назад", callback_data="back")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    if keyboard != json_error:
        await handler_free_tariff(message, ticket_id, keyboard)
    else:
        await message.answer(json_error)















@dp.callback_query(lambda c: c.data == 'payed')
async def pay_handler(callback_query: CallbackQuery):
    query = callback_query.message.text
    cost = float(query.split('\n')[5].split()[5])
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await bot.send_invoice(
        chat_id=callback_query.from_user.id,
        title="parking_pay",
        description="Оплатить парковку",
        payload="payed",
        provider_token=secret.TOKEN_PAYMENTS,
        currency="RUB",
        start_parameter="card_park_bot",
        prices=[LabeledPrice(
            label=f'Оплата {cost}',
            amount=int(cost) * 100
        )]
    )


@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query_id=pre_checkout_query.id, ok=True)


@dp.callback_query(lambda message: message.successful_payment.invoice_payload == 'payed')
async def process_pay(message: Message):
    await message.answer(text='Вы оплатили парковку!')



















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
