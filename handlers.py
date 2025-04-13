import requests

from PIL import Image
from pyzbar.pyzbar import decode
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from bs4 import BeautifulSoup


def  parsing_site(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    trs = soup.find_all('tr')
    string = ''
    for tr in trs:
        if not tr.text.isspace():
            string += tr.text.replace(' ', ': ', 1) + '\n'
    string += '\n' + link
    return string

def exist_trs(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    trs = soup.find_all('tr')
    return len(trs) > 0


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
    return parsing_site(link)

def get_link(ticket_id):
    base_url = 'http://195.239.22.157:48123/pub/pay?code='
    link = base_url + f'[{ticket_id.upper()}]'
    if exist_trs(link):
        return link
    else:
        base_url = 'http://5.17.29.108:88/pub/pay?code='
        link = base_url + f'[{ticket_id.upper()}]'
        return link


def get_parking_payment(ticket_id: str, secret: str = '123', api_base: str = None) -> float:
    """
    Получает сумму оплаты парковки по ticket_id

    Args:
        ticket_id (str): Номер парковочного билета
        secret (str): Секретный ключ для подписи (по умолчанию '123')
        api_base (str): Базовый URL API (если None, используется стандартный)

    Returns:
        float: Сумма оплаты

    Raises:
        ValueError: Если не удалось получить сумму оплаты
        ConnectionError: Если возникла ошибка соединения
    """
    try:
        link = get_link(ticket_id)
        if exist_trs(link):
            string = parsing_site(link)

            return string
        return 'Неверный идентификатор талона.\nПроверьте идентификатор талона и перепишите его сюда.'

    except requests.RequestException as e:
        raise ConnectionError(f"Ошибка соединения с API: {str(e)}")
    except Exception as e:
        raise ValueError(f"Ошибка обработки данных: {str(e)}")