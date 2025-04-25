import hashlib
import json
import socket
from json.decoder import JSONDecodeError

import requests

from PIL import Image
from cv2 import VideoCapture, imwrite
from pyzbar.pyzbar import decode
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from bs4 import BeautifulSoup

import secret

client = socket.socket()
client.connect(("192.168.1.145", 81))
client.close()

json_error = '⛔️Неверный идентификатор талона.⛔️\nПроверьте идентификатор талона и перепишите его сюда.'
link_endpoint = 'http://192.168.1.145:81/parking/parkapp'
secret_word = secret.SECRET_WORD

def get_JSON(ticket_id):
    try:
        link = get_link_JSON(ticket_id)
        json_data = requests.get(link).json()
        return json_data
    except JSONDecodeError as e:
        return json_error
def get_link_JSON(ticket_id):
    data = 'ticket_id=' + ticket_id.upper() + '&' + secret_word
    hash_SHA1 = hashlib.sha1(data.encode('utf-8')).hexdigest()
    link = f'{link_endpoint}/invoice?ticket_id={ticket_id}&hash={hash_SHA1}'
    return link
def get_link_for_payed(client_id):
    link = 'http://5.17.29.108:88/pub/pay'
    data = f'id={client_id}'
    hash_SHA1 = hashlib.sha1(data.encode('utf-8')).hexdigest()
    data = f'?id={client_id}&hash={hash_SHA1}'
    link += data
    return link
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
    link = get_link(link) if 'http' not in link else link
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
def get_parking(ticket_id: str):
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
def get_amount(ticket_id):
    json_data = get_JSON(ticket_id)
    try:
        return json_data['amount']
    except Exception as e:
        return 'У вас бесплатный проезд'
def get_file_path_to_photo(number: int):
    camera = f'camera={number}'
    data = f'{camera}&{secret_word}'
    hash_SHA1 = hashlib.sha1(data.encode('utf-8')).hexdigest()
    link = f'{link_endpoint}/makephoto'
    link = f'{link}?{camera}&hash={hash_SHA1}'
    response = requests.post(link)
    file_path = response.json()['file']
    return file_path
def get_quantity_captures():
    link = link_endpoint + '/cameras'
    response = requests.get(link)
    json_data = response.json()
    return len(json_data)