from PIL import Image
from pyzbar.pyzbar import decode

def qrcode_func(image: Image.Image):
    # Декодируем QR-код из переданного изображения
    decoded_objects = decode(image)
    # Инициализируем переменную для хранения ссылки
    link = None
    # Извлекаем данные из декодированных объектов
    for obj in decoded_objects:
        link = obj.data.decode('utf-8')
    return link







