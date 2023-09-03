# !/usr/bin/env python
# -*-coding:utf-8-*-
import json
import time
import requests
from web3 import Web3
import sys
from config import config

network = sys.argv[1]
w3 = Web3(Web3.WebsocketProvider(config('NODE', network + config('NODE', 'CHAIN')).format(config('MORALIS', 'FIND_BLOCK')), websocket_timeout=900, websocket_kwargs={'max_size': 999999999}))

blockNumbers = []
while True:
    try:
        txhs = requests.post(config('REMOTE', 'SITE') + "/api/network/get-transactions/" + str(network))
        if txhs.status_code == 200:
            for txh in txhs.json():
                transaction = w3.eth.get_transaction(txh)
                if transaction['blockNumber'] is not None:
                    blockNumbers.append({
                        'block_number': transaction['blockNumber'],
                        'network': network
                    })
            if len(blockNumbers) > 0:
                requests.post(config('REMOTE', 'SITE') + "/api/network/set-blocks", json=blockNumbers, headers={"Content-Type": "text/json"})
                time.sleep(5)
            else:
                time.sleep(15)
        else:
            raise Exception("php error")
    except:
        time.sleep(15)
