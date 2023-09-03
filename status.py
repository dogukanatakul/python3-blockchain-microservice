# !/usr/bin/env python
# -*-coding:utf-8-*-
from web3 import Web3
from web3.middleware import geth_poa_middleware
from config import config
from sqlite import sqlite_first


def statusNode():
    try:
        # BSC
        w3 = Web3(Web3.WebsocketProvider(config('NODE', "BSC" + config('NODE', 'CHAIN')).format(config('MORALIS', 'DEFAULT')), websocket_timeout=900, websocket_kwargs={'max_size': 999999999}))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        setJson = {'BSC_BLOCK_LATEST': int(w3.eth.getBlock('latest').number)}
        checkLastBlock = sqlite_first("bots", "WHERE network='{0}' AND status=1 ORDER BY block DESC".format("BSC"))
        if checkLastBlock is not None:
            setJson['BSC_BLOCK'] = checkLastBlock['block']
        else:
            setJson['BSC_BLOCK'] = 0
        setJson['BSC_DIFF'] = setJson['BSC_BLOCK_LATEST'] - setJson['BSC_BLOCK']

        # ETH
        w3 = Web3(Web3.WebsocketProvider(config('NODE', "ETH" + config('NODE', 'CHAIN')).format(config('MORALIS', 'DEFAULT')), websocket_timeout=900, websocket_kwargs={'max_size': 999999999}))
        setJson['ETH_BLOCK_LATEST'] = int(w3.eth.getBlock('latest').number)
        checkLastBlock = sqlite_first("bots", "WHERE network='{0}' AND status=1 ORDER BY block DESC".format("ETH"))
        if checkLastBlock is not None:
            setJson['ETH_BLOCK'] = checkLastBlock['block']
        else:
            setJson['ETH_BLOCK'] = 0
        setJson['ETH_DIFF'] = setJson['ETH_BLOCK_LATEST'] - setJson['ETH_BLOCK']
        return {
            'status': 'success',
            'remote_site': config('REMOTE', 'SITE'),
            'block': setJson,
            'chain': str(config('NODE', 'CHAIN'))
        }
    except Exception as e:
        return {
            'status': 'fail',
            'message': str(e)
        }
