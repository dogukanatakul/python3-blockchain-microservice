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
from sqlite import sqlite_get_first, sqlite_update, sqlite_insert
import asyncio
from helper import to_many_request


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


job = sys.argv[1]
filePath = os.path.dirname(os.path.realpath(__file__)) + '/'


async def parse(w3, abi, receipt, transaction):
    print("starting_parse:", transaction['blockHash'])
    global exportList
    global printLog
    customTxh = []
    global wallets
    global checkBot
    try:
        if len(receipt["logs"]) > 0:
            printLog += 1
            print(printLog, "token başlangıç")
            if transaction['hash'] not in customTxh:
                if len(receipt["logs"]) < 20:
                    for log in receipt["logs"]:
                        w3Request = True
                        while w3Request:
                            try:
                                contract = w3.eth.contract(log["address"], abi=abi)
                                w3Request = False
                            except Exception as e:
                                if not to_many_request(e):
                                    raise Exception(str(e))
                                else:
                                    await asyncio.sleep(1)
                        printLog += 1
                        print(printLog, "token kontrat abi")
                        if len(log["topics"]) > 0:
                            printLog += 1
                            print(printLog, "token gönderimi mevcut")
                            abi_events = [abi for abi in contract.abi if abi["type"] == "event"]
                            for event in abi_events:
                                if transaction['hash'] not in customTxh:
                                    printLog += 1
                                    print(printLog, "abi etkinliği geçildi")
                                    # Get event signature components
                                    name = event["name"]
                                    inputs = [param["type"] for param in event["inputs"]]
                                    inputs = ",".join(inputs)
                                    event_signature_hex = w3.toHex(w3.keccak(text=f"{name}({inputs})"))
                                    if event_signature_hex == w3.toHex(log["topics"][0]):
                                        printLog += 1
                                        print(printLog, "imzalanmış transfer")
                                        # Decode matching log
                                        decoded_logs = contract.events[event["name"]]().processReceipt(receipt)
                                        print(len(decoded_logs), " adet alt kayıt--------------")
                                        if len(decoded_logs) < 20:
                                            for decoded_log in decoded_logs:
                                                printLog += 1
                                                print(printLog, "token transfer parçalama")
                                                if decoded_log['event'] == 'Transfer':
                                                    printLog += 1
                                                    print(printLog, "Transfer")
                                                    trans = _parseValue(decoded_log)
                                                    # print("token", trans)
                                                    if trans['args']['from'] in wallets or trans['args']['to'] in wallets:
                                                        printLog += 1
                                                        print(printLog, "cccdds")
                                                        w3Request = True
                                                        while w3Request:
                                                            try:
                                                                token = w3.eth.contract(address=trans['address'], abi=abi)
                                                                w3Request = False
                                                            except Exception as e:
                                                                if not to_many_request(e):
                                                                    raise Exception(str(e))
                                                                else:
                                                                    await asyncio.sleep(1)
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
                                            print(bcolors.WARNING + transaction['blockHash'] + bcolors.ENDC, " : atlandı")
                                            customTxh.append(transaction['hash'])
                                            sqlite_insert('customs', {
                                                'block': transaction['blockNumber'],
                                                'txh': transaction['blockHash'],
                                                'network': checkBot['network'],
                                            })
                else:
                    print(bcolors.WARNING + transaction['hash'] + bcolors.ENDC, " : atlandı")
                    customTxh.append(transaction['hash'])
                    sqlite_insert('customs', {
                        'block': transaction['blockNumber'],
                        'txh': transaction['blockHash'],
                        'network': checkBot['network'],
                    })
        else:
            printLog += 1
            print(printLog, "k")
            printLog += 1
            print(printLog, "h")
            if transaction['from'] in wallets or transaction['to'] in wallets:
                exportList.append({
                    'block_number': transaction['blockNumber'],
                    'from': transaction['from'],
                    'to': transaction['to'],
                    'contract': None,
                    'fee': str(w3.fromWei(w3.fromWei(receipt['gasUsed'] * transaction['gasPrice'], 'wei'), 'ether')),
                    'txh': transaction['hash'],
                    'value': str(Web3.fromWei(transaction['value'], 'ether')),
                    'network': network,
                    'status': receipt['status']
                })
        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("error----------", exc_type, fname, exc_tb.tb_lineno)
        return False
        # raise Exception(str(e))


async def run_tasks(tasks):
    await asyncio.gather(*tasks)


async def get_txhs(block):
    print("get_txhs runned:" + str(block['hash']))
    global setTxhs
    w3Request = True
    while w3Request:
        try:
            receipt = w3.eth.get_transaction_receipt(block['hash'])
            w3Request = False
        except Exception as e:
            if not to_many_request(e):
                raise Exception(str(e))
            else:
                await asyncio.sleep(1)
    w3Request = True
    while w3Request:
        try:
            transaction = w3.eth.get_transaction(block['hash'])
            w3Request = False
        except Exception as e:
            if not to_many_request(e):
                raise Exception(str(e))
            else:
                await asyncio.sleep(1)
    setTxhs.append({
        'receipt': receipt,
        'transaction': _parseValue(transaction)
    })
    return True


while True:
    tasks = []
    printLog = 0
    getTxhs = []
    setTxhs = []
    checkBot = sqlite_get_first("bots", "bot", "#" + job)
    if checkBot['block'] is not None:
        network = checkBot['network']
        blockNum = int(checkBot['block'])
        try:
            exportList = []
            printLog += 1
            print(printLog, "a")
            w3 = Web3(Web3.WebsocketProvider(config('NODE', network + config('NODE', 'CHAIN')).format(checkBot['uuid']), websocket_timeout=900, websocket_kwargs={'max_size': 999999999}))
            printLog += 1
            print(printLog, "b")
            w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            print(str(blockNum) + " started")
            w3Request = True
            while w3Request:
                try:
                    latestBlock = w3.eth.getBlock('latest').number
                    w3Request = False
                except Exception as e:
                    if not to_many_request(e):
                        raise Exception(str(e))
                    else:
                        time.sleep(9)

            printLog += 1
            print(printLog, "c")
            if latestBlock > int(blockNum):
                printLog += 1
                print(printLog, "ç")
                wallets = requests.post(config('REMOTE', 'SITE') + '/api/network/wallets/27ba4f9a-8bee-49ed-a945-b90d4b89a874/' + network).json()
                if network == 'BSC':
                    with open(filePath + "abis/bep20.json") as f:
                        abi = json.load(f)
                else:
                    with open(filePath + "abis/erc20.json") as f:
                        abi = json.load(f)
                printLog += 1
                print(printLog, "çç")

                w3Request = True
                while w3Request:
                    try:
                        block = w3.eth.getBlock(blockNum, full_transactions=True).transactions
                        w3Request = False
                    except Exception as e:
                        if not to_many_request(e):
                            raise Exception(str(e))
                        else:
                            time.sleep(9)
                printLog += 1
                print(printLog, "d")
                parseBlock = _parseValue(block)
                printLog += 1
                print(printLog, "e")
                for block in parseBlock:
                    getTxhs.append(get_txhs(block))
                asyncio.get_event_loop().run_until_complete(run_tasks(getTxhs))
                for botTxh in setTxhs:
                    tasks.append(parse(w3, abi, botTxh['receipt'], botTxh['transaction']))
                asyncio.get_event_loop().run_until_complete(run_tasks(tasks))
                if len(exportList) > 0:
                    print(exportList)
                    time.sleep(9999)
                    request = requests.post(config('REMOTE', 'SITE') + '/api/network/set-transactions/' + network, json=exportList, headers={"Content-Type": "text/json"}).status_code
                    if request != 200:
                        raise Exception("transaction request fail")
                printLog += 1
                print(printLog, "ş")
                sqlite_update("bots", "block = null, network = null", "bot", checkBot['bot'])
                printLog += 1
                print(printLog)
                print(str(blockNum) + " parsed")
        except Exception as e:
            print(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("error----------", exc_type, fname, exc_tb.tb_lineno)
            time.sleep(5)
    else:
        print("no job")
        time.sleep(2)
