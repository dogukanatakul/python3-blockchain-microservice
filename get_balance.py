#!/usr/bin/env python
# -*-coding:utf-8-*-
from web3 import Web3
from config import config


def getBalance(wallet, server):
    w3 = Web3(Web3.WebsocketProvider(config('NODE', server).format(config('MORALIS', 'DEFAULT')), websocket_timeout=900, websocket_kwargs={'max_size': 999999999}))
    try:
        balance = w3.eth.get_balance(wallet)
        balance = Web3.fromWei(balance, 'ether')
        return {
            'status': 'success',
            'balance': str(balance)
        }
    except Exception as e:
        return {
            'status': 'fail',
            'message': str(e)
        }
