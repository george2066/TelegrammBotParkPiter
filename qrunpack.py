import cv2
from cv2 import QRCodeDetector, imread
from qreader import QReader
from pyzbar.pyzbar import decode







def qrcode_func(image_url: str = "C:/Users/User/Desktop/python_tg_bot_releas_edition/qrcode_test.png"):
    
    qreader = QReader()
    
    image_url = "C:/Users/User/Desktop/python_tg_bot_releas_edition/qrcode_test.png"
    
    image = cv2.cvtColor(cv2.imread(image_url), cv2.COLOR_BGR2RGB)

    decoded_text = qreader.detect_and_decode(image=image)

    """ print(f"Image: {decoded_text}") """
    return decoded_text
"""     for img_path in (''):
    # Read the image
    img = imread(img_path) """
    
    

qrcode_func()