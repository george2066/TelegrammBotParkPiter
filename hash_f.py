import hashlib
import json.scanner
import requests
import hashlib
import json


class data_strg:
    Api1 = 'http://192.168.1.145:81/parking/parkapp/invoice?ticket_id='

    ticket_id = 'D675A0'
    secret = '123'
    data = (ticket_id).upper() + secret
    
    
    hash_sha1_data = hashlib.sha1(data.encode(encoding="utf-8")).hexdigest()
    """ hash_sha1_payed = '7b08c609f437920904d14a3192fbe5ed703fc760' """
    user_url_send = Api1 + ticket_id + "&hash=" + hash_sha1_data

    print(user_url_send)
    response = requests.get(user_url_send).json()

    send_event = requests.get(user_url_send)
    dataparse = send_event.json()
    
    if 'amount' in dataparse:
        pars_value = dataparse['amount']
    print(pars_value)
