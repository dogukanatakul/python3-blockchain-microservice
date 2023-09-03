# !/usr/bin/env python
# -*-coding:utf-8-*-
from web3 import Web3
from web3.middleware import geth_poa_middleware
from helper import _parseValue
import json
import requests
from decimal import Decimal
from config import config
import sys
import time
import os

network = sys.argv[1]
uuid = sys.argv[2]
filePath = os.path.dirname(os.path.realpath(__file__)) + '/'
while True:
    customTxh = []
    blocks = requests.post(config('REMOTE', 'SITE') + "/api/network/get-blocks/" + str(network)).json()
    for blockNum in blocks:
        printLog = 0
        try:
            exportList = []
            printLog += 1
            print(printLog, "a")
            w3 = Web3(Web3.WebsocketProvider(config('NODE', network + config('NODE', 'CHAIN')).format(config('MORALIS', uuid)), websocket_timeout=900, websocket_kwargs={'max_size': 999999999}))
            printLog += 1
            print(printLog, "b")
            w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            print(str(blockNum) + " started")
            latestBlock = w3.eth.getBlock('latest').number
            printLog += 1
            print(printLog, "c")
            if latestBlock > int(blockNum):
                printLog += 1
                print(printLog, "ç")
                latestBlock = int(w3.eth.getBlock('latest').number)
                wallets = requests.post(config('REMOTE', 'SITE') + '/api/network/wallets/27ba4f9a-8bee-49ed-a945-b90d4b89a874/' + network).json()
                if network == 'BSC':
                    with open(filePath + "abis/bep20.json") as f:
                        abi = json.load(f)
                else:
                    with open(filePath + "abis/erc20.json") as f:
                        abi = json.load(f)
                printLog += 1
                print(printLog, "çç")
                block = w3.eth.getBlock(blockNum, full_transactions=True).transactions
                printLog += 1
                print(printLog, "d")
                parseBlock = _parseValue(block)
                printLog += 1
                print(printLog, "e")
                for block in parseBlock:
                    printLog += 1
                    print(printLog, "f")
                    print(block['hash'])
                    try:
                        receipt = w3.eth.get_transaction_receipt(block['hash'])
                        transaction = w3.eth.get_transaction(block['hash'])
                        logs = receipt["logs"]
                        if len(logs) > 0:
                            printLog += 1
                            print(printLog, "k")
                            for log in logs:
                                if w3.toHex(block['hash']) not in customTxh:
                                    smart_contract = log["address"]
                                    contract = w3.eth.contract(smart_contract, abi=abi)
                                    receipt_event_signature_hex = w3.toHex(log["topics"][0])
                                    abi_events = [abi for abi in contract.abi if abi["type"] == "event"]
                                    for event in abi_events:
                                        # Get event signature components
                                        name = event["name"]
                                        inputs = [param["type"] for param in event["inputs"]]
                                        inputs = ",".join(inputs)
                                        # Hash event signature
                                        event_signature_text = f"{name}({inputs})"
                                        event_signature_hex = w3.toHex(w3.keccak(text=event_signature_text))
                                        if event_signature_hex == receipt_event_signature_hex:
                                            # Decode matching log
                                            decoded_logs = contract.events[event["name"]]().processReceipt(receipt)
                                            if len(decoded_logs) < 20:
                                                for decoded_log in decoded_logs:
                                                    if decoded_log['event'] == 'Transfer':
                                                        trans = _parseValue(decoded_log)
                                                        # print("token", trans)
                                                        if trans['args']['from'] in wallets or trans['args']['to'] in wallets:
                                                            token = w3.eth.contract(address=trans['address'], abi=abi)
                                                            exportList.append({
                                                                'block_number': trans['blockNumber'],
                                                                'from': trans['args']['from'],
                                                                'to': trans['args']['to'],
                                                                'contract': trans['address'],
                                                                'fee': str(w3.fromWei(w3.fromWei(receipt['gasUsed'] * transaction['gasPrice'], 'wei'), 'ether')),
                                                                'txh': trans['transactionHash'],
                                                                'value': str(Decimal(trans['args']['value'] / (10 ** token.functions.decimals().call()))),
                                                                'network': network,
                                                                'status': receipt['status']
                                                            })
                                            else:
                                                customTxh.append(w3.toHex(block['hash']))
                                                print("to loong logs.")
                        else:
                            printLog += 1
                            print(printLog, "k")
                            trans = _parseValue(transaction)
                            printLog += 1
                            print(printLog, "h")
                            # print("coin", trans)
                            if trans['from'] in wallets or trans['to'] in wallets:
                                exportList.append({
                                    'block_number': trans['blockNumber'],
                                    'from': trans['from'],
                                    'to': trans['to'],
                                    'contract': None,
                                    'fee': str(w3.fromWei(w3.fromWei(receipt['gasUsed'] * transaction['gasPrice'], 'wei'), 'ether')),
                                    'txh': trans['hash'],
                                    'value': str(Web3.fromWei(trans['value'], 'ether')),
                                    'network': network,
                                    'status': receipt['status']
                                })
                    except Exception as e:
                        print("error:", str(e))
                if len(exportList) > 0:
                    request = requests.post(config('REMOTE', 'SITE') + '/api/network/set-transactions/' + network, json=exportList, headers={"Content-Type": "text/json"}).status_code
                    if request != 200:
                        raise Exception("transaction request fail")
                if len(customTxh) > 0:
                    print(customTxh)
                printLog += 1
                print(printLog, "ş")
                printLog += 1
                print(printLog)
                print(str(blockNum) + " parsed")
        except Exception as e:
            print("error----------", str(e))
            time.sleep(10)
