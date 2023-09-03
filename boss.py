# !/usr/bin/env python
# -*-coding:utf-8-*-
from sqlite import sqlite_get_first, sqlite_first, sqlite_update
from web3 import Web3
from web3.middleware import geth_poa_middleware
from config import config
import sys
import os
from datetime import datetime

network = sys.argv[1]
w3 = Web3(Web3.WebsocketProvider(config('NODE', network + config('NODE', 'CHAIN')).format(config('MORALIS', "FIND_BLOCK")), websocket_timeout=900, websocket_kwargs={'max_size': 999999999}))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
while True:
    try:
        latestBlock = w3.eth.getBlock('latest').number
        checkLastBlock = sqlite_first("bots", "WHERE network='{0}' AND status=1 ORDER BY block DESC".format(network))
        if checkLastBlock is None:
            blockNum = latestBlock
        else:
            blockNum = int(checkLastBlock['block']) + 1
        if latestBlock >= blockNum:
            checkFreeBot = sqlite_get_first("bots", "block", None)
            if checkFreeBot is not None:
                sqlite_update("bots", "block = {0}, network = '{1}', updated_at='{2}'".format(blockNum, network, datetime.now().strftime("%d/%m/%Y %H:%M:%S")), "bot", checkFreeBot['bot'])
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("error----------", e, exc_type, fname, exc_tb.tb_lineno)
