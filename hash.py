import hashlib
import requests
import json.scanner

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
        base_url = api_base or 'http://192.168.1.145:81/parking/parkapp/invoice'
        data = 'ticket_id=' + ticket_id.upper() + '&' + secret
        hash_sha1 = hashlib.sha1(data.encode('utf-8')).hexdigest()
        url = f"{base_url}?ticket_id={ticket_id}&hash={hash_sha1}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if 'amount' not in result:
            raise ValueError("В ответе API отсутствует сумма оплаты")
            
        return float(result['amount'])
        
    except requests.RequestException as e:
        raise ConnectionError(f"Ошибка соединения с API: {str(e)}")
    except Exception as e:
        raise ValueError(f"Ошибка обработки данных: {str(e)}")