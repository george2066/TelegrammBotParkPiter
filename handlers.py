import requests

from PIL import Image
from pyzbar.pyzbar import decode
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from bs4 import BeautifulSoup

def ticket_kb():
    keyboard=ReplyKeyboardMarkup(keyboard =[
        [KeyboardButton(text='Ввести номер')]
    ], resize_keyboard=True)
    return keyboard

def sendPhoto_kb():
    pass

def read_QR(image: Image.Image) -> str:
    decoded_objects = decode(image)
    link = None
    for obj in decoded_objects:
        link = obj.data.decode('utf-8')
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    trs = soup.find_all('tr')
    string = f'Это ваш билет? \n \n'
    for tr in trs:
        if not tr.text.isspace():
            string += tr.text.replace(' ', ': ', 1) + '\n'
    string += '\n' + link
    return string