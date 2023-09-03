import requests
from config import config
from tronpy.abi import trx_abi
import sys
import os
import json
import time
from decimal import Decimal

server = "TRX" + config('NODE', 'CHAIN')
while True:
    wallet = requests.post(config('REMOTE', 'SITE') + '/api/network/tron/random-wallets/trx')
    if wallet.status_code == 200:
        wallet = wallet.json()
        tronTokenDecimals = {}
        decode = "000000000000000000000000"
        try:
            response = requests.get(config('NODE', server) + "/v1/accounts/" + wallet['wallet'] + "/transactions?limit=" + str(200)).json()
            items = []
            for item in response['data']:
                if item['txID'] not in wallet['txh']:
                    if 'raw_data' in item:
                        for contract in item['raw_data']['contract']:
                            if contract['type'] == 'TriggerSmartContract':
                                try:
                                    parse = trx_abi.decode_abi(['address', 'uint256'], bytes.fromhex(contract['parameter']['value']['data'][8:]))
                                    contract_address = trx_abi.decode_single('address', bytes.fromhex(decode + contract['parameter']['value']['contract_address'][2:]))
                                    if contract_address in tronTokenDecimals:
                                        tokenDecimal = tronTokenDecimals[contract_address]
                                    else:
                                        tokenDecimal = requests.get(config('NODE', server + "_SCAN") + "/contract?contract=" + contract_address).json()['data'][0]['tokenInfo']['tokenDecimal']
                                        tronTokenDecimals[contract_address] = tokenDecimal
                                    items.append({
                                        'block_number': item['blockNumber'],
                                        'from': trx_abi.decode_single('address', bytes.fromhex(decode + contract['parameter']['value']['owner_address'][2:])),
                                        'to': parse[0],
                                        'contract': contract_address,
                                        'fee': str(Decimal(str(item['ret'][0]['fee'])) / Decimal(str(1000000))),
                                        'txh': item['txID'],
                                        'value': str(Decimal(str(parse[1])) / Decimal(str(10 ** int(tokenDecimal)))),
                                        'network': 'TRX',
                                        'status': '1' if item['ret'][0]['contractRet'] == 'SUCCESS' else '0',
                                    })
                                except Exception as e:
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                                    print(exc_type, fname, exc_tb.tb_lineno)
                            elif contract['type'] == 'TransferContract':
                                items.append({
                                    'block_number': item['blockNumber'],
                                    'from': trx_abi.decode_single('address', bytes.fromhex(decode + contract['parameter']['value']['owner_address'][2:])),
                                    'to': trx_abi.decode_single('address', bytes.fromhex(decode + contract['parameter']['value']['to_address'][2:])),
                                    'contract': None,
                                    'fee': int(item['ret'][0]['fee']) / 1000000,
                                    'txh': item['txID'],
                                    'value': str(Decimal(str(contract['parameter']['value']['amount'])) / Decimal(str(10 ** 6))),
                                    'network': 'TRX',
                                    'status': '1' if item['ret'][0]['contractRet'] == 'SUCCESS' else '0',
                                })
                            elif contract['type'] == 'TransferAssetContract':
                                if contract['parameter']['value']['asset_name'] in tronTokenDecimals:
                                    tokenDecimal = tronTokenDecimals[contract['parameter']['value']['asset_name']]
                                else:
                                    tokenDecimal = requests.post(config('NODE', server) + "/wallet/getassetissuebyid", json={
                                        "value": contract['parameter']['value']['asset_name']
                                    }).json()['precision']
                                    tronTokenDecimals[contract['parameter']['value']['asset_name']] = tokenDecimal
                                items.append({
                                    'block_number': item['blockNumber'],
                                    'from': trx_abi.decode_single('address', bytes.fromhex(decode + contract['parameter']['value']['owner_address'][2:])),
                                    'to': trx_abi.decode_single('address', bytes.fromhex(decode + contract['parameter']['value']['to_address'][2:])),
                                    'contract': contract['parameter']['value']['asset_name'],
                                    'fee': int(item['ret'][0]['fee']) / 1000000,
                                    'txh': item['txID'],
                                    'value': str(Decimal(str(contract['parameter']['value']['amount'])) / Decimal(10 ** int(tokenDecimal))),
                                    'network': 'TRX',
                                    'status': '1' if item['ret'][0]['contractRet'] == 'SUCCESS' else '0',
                                })
                    else:
                        print("ok")
            if len(items) > 0:
                putTransactions = requests.post(config('REMOTE', 'SITE') + '/api/network/set-transactions/TRX', data=json.dumps(items), headers={"Content-Type": "text/json"})
                if putTransactions.status_code != 200:
                    time.sleep(5)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
    else:
        time.sleep(5)
