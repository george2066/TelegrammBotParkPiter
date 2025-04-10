import hashlib
import json

import requests

from PIL import Image
from pyzbar.pyzbar import decode
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from bs4 import BeautifulSoup


def parsing_site(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    trs = soup.find_all('tr')
    string = ''
    for tr in trs:
        if not tr.text.isspace():
            string += tr.text.replace(' ', ': ', 1) + '\n'
    string += '\n' + link
    return str(string)
def quantity_tr(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    trs = soup.find_all('tr')
    return len(trs)
def exist_trs(link):
    return quantity_tr(link) > 0
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
def free_tariff(ticket_id):
    trs = BeautifulSoup(requests.get(get_link(ticket_id)).text, 'html.parser').find_all('tr')
    return any('Бесплатное время' in tr.text for tr in trs)
def get_parking(ticket_id: str) -> float:
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
def get_amount(link):
    string = parsing_site(link)

    for i in string.split('\n'):
        if 'руб' in i:
            return int(''.join(([digit for digit in i if digit.isdigit()])))
    return 'У вас бесплатная парковка.'
def get_link_for_payed(ticket_id):
    json_data = get_JSON(ticket_id)
    secret = '123'
    link = 'http://192.168.1.145:81/parking/parkapp/invoice'
    amount = json_data['amount']
    data = f'amount={amount}&ticket_id={ticket_id}&secret={secret}'
    hash_SHA1 = hashlib.sha1(data.encode('utf-8')).hexdigest()
    data = f'?amount={amount}&ticket_id={ticket_id}&hash={hash_SHA1}'
    link += data
    return link
def get_JSON(ticket_id):
    secret = '123'
    data = 'ticket_id=' + ticket_id.upper() + '&' + secret
    hash_SHA1 = hashlib.sha1(data.encode('utf-8')).hexdigest()
    link = f'http://192.168.1.145:81/parking/parkapp/invoice?ticket_id={ticket_id}&hash={hash_SHA1}'
    print(link)
    response = requests.get(link)
    data = response.content.decode('utf-8')
    json_data = json.loads(data)
    return json_data
