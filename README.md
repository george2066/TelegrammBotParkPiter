# TelegrammBotParkPiter

Сохраните в файле C:\Parking
Откройте командную строку и пропишите туда следующие команды (обязательно перед этим установите ***Visual C++*** и ***Python 3.12.8***):


(в корне вашего файлового пути)
- ***pip install poetry***

(теперь переходите в файл вашего бота)
- Сделайте файл ***secrets.py*** и сохраните туда:
  - ***TOKEN*** вашего бота.
  - ***API_KEY*** ключ
  - ***SHOP_ID*** вашего магазина
  - ***TOKEN_PAYMENTS*** вашей оплаты
- ***python -m venv .venv***
- ***poetry init***
- ***poetry add bs4 opencv-python requests pillow aiogram pyzbar***
- ***.venv\Scripts\activate.bat***
- ***pythonw main.py***

Если сделали что-то не то, то просто удалите созданные этими командами папки и файлы.
