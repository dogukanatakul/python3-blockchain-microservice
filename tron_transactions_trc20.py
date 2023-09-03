import requests
from config import config
import sys
import os
import time
import json
from decimal import Decimal

server = "TRX" + config('NODE', 'CHAIN')
headers = {"Accept": "application/json", "Content-Type": "application/json", "TRON-PRO-API-KEY": "251db50f-89f1-4200-8878-6285a46c6d14"}
while True:
    wallet = requests.post(config('REMOTE', 'SITE') + '/api/network/tron/random-wallets/trc20')
    if wallet.status_code == 200:
        wallet = wallet.json()
        try:
            response = requests.get(config('NODE', server) + "/v1/accounts/" + wallet['wallet'] + "/transactions/trc20?limit=" + str(200)).json()
            items = []
            for item in response['data']:
                if item['transaction_id'] not in wallet['txh'] and item['type'] == 'Transfer':
                    txh = requests.post(config('NODE', server) + "/wallet/gettransactioninfobyid", json={
                        'value': item['transaction_id']
                    }).json()
                    items.append({
                        'block_number': txh['blockNumber'],
                        'from': item['from'],
                        'to': item['to'],
                        'contract': item['token_info']['address'],
                        'fee': str(Decimal(str(txh['fee'])) / Decimal(str(1000000))),
                        'txh': item['transaction_id'],
                        'value': str(Decimal(str(item['value'])) / Decimal(str(10 ** int(item['token_info']['decimals'])))),
                        'network': 'TRX',
                        'status': '1' if txh['receipt']['result'] == 'SUCCESS' else '0',
                    })
            if len(items) > 0:
                putTransactions = requests.post(config('REMOTE', 'SITE') + '/api/network/set-transactions/TRX', data=json.dumps(items), headers=headers)
                if putTransactions.status_code != 200:
                    time.sleep(5)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
    else:
        time.sleep(5)
