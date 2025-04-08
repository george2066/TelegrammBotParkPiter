from PIL import Image
from pyzbar.pyzbar import decode
from aiogram.types import InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup

def start():
    return f'Добро пожаловать!\nКакую операцию вы хотите провести?'

def ticket_kb():
    keyboard=ReplyKeyboardMarkup(keyboard =[
        [KeyboardButton(text='Ввести номер')]
    ], resize_keyboard=True)
    return keyboard

def sendPhoto_kb():
    pass

def qrcode_func(image: Image.Image):
    decoded_objects = decode(image)
    link = None
    for obj in decoded_objects:
        link = obj.data.decode('utf-8')
    return link