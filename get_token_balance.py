#!/usr/bin/env python
# -*-coding:utf-8-*-
from web3 import Web3
import json
from config import config
from decimal import Decimal
import os
from helper import to_many_request
import time


def getTokenBalance(wallet, contract, server):
    w3 = Web3(Web3.WebsocketProvider(config('NODE', server).format(config('MORALIS', 'DEFAULT')), websocket_timeout=900, websocket_kwargs={'max_size': 999999999}))
    with open(os.path.dirname(os.path.realpath(__file__)) + "/abis/erc20.json") as f:
        abi = json.load(f)
    try:
        w3Request = True
        while w3Request:
            try:
                contract = w3.toChecksumAddress(contract)
                w3Request = False
            except Exception as e:
                if not to_many_request(e):
                    raise Exception(str(e))
                else:
                    time.sleep(1)
        w3Request = True
        while w3Request:
            try:
                token = w3.eth.contract(address=contract, abi=abi)
                w3Request = False
            except Exception as e:
                if not to_many_request(e):
                    raise Exception(str(e))
                else:
                    time.sleep(1)
        w3Request = True
        while w3Request:
            try:
                wallet = w3.toChecksumAddress(wallet)
                w3Request = False
            except Exception as e:
                if not to_many_request(e):
                    raise Exception(str(e))
                else:
                    time.sleep(1)
        w3Request = True
        while w3Request:
            try:
                balance = token.functions.balanceOf(wallet).call()
                w3Request = False
            except Exception as e:
                if not to_many_request(e):
                    raise Exception(str(e))
                else:
                    time.sleep(1)
        w3Request = True
        while w3Request:
            try:
                balance = Decimal(str(balance)) / Decimal(str(10 ** token.functions.decimals().call()))
                w3Request = False
            except Exception as e:
                if not to_many_request(e):
                    raise Exception(str(e))
                else:
                    time.sleep(1)
        return {
            'status': 'success',
            'balance': str(balance)
        }
    except Exception as e:
        return {
            'status': 'fail',
            'message': str(e)
        }
