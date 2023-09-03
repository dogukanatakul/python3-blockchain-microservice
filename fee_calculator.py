# !/usr/bin/env python
# -*-coding:utf-8-*-
from web3 import Web3
from decimal import Decimal
from config import config


def feeCalculator(value, from_address, to_address, server):
    w3 = Web3(Web3.WebsocketProvider(config('NODE', server).format(config('MORALIS', 'DEFAULT')), websocket_timeout=900, websocket_kwargs={'max_size': 999999999}))
    from_address = Web3.toChecksumAddress(from_address)
    to_address = Web3.toChecksumAddress(to_address)
    try:
        estimate = w3.eth.estimateGas({'to': to_address, 'from': from_address, 'value': w3.toWei(Decimal(str(value)), 'ether')})
        return {
            'status': 'success',
            'gas': str(estimate),
            'gas_price': str(w3.eth.gasPrice),
            'bnb': str(w3.fromWei(w3.fromWei(w3.eth.gasPrice, 'gwei') * estimate, 'gwei'))
        }
    except Exception as e:
        return {
            'status': 'fail',
            'response': str(e)
        }
