import time

import web3.eth
from web3 import Web3
from decimal import Decimal
from config import config
from helper import to_many_request


def transaction(from_address, from_address_private, to_address, value, nonce=0, multiply=1, server=False):
    w3 = Web3(Web3.WebsocketProvider(config('NODE', server).format(config('MORALIS', 'DEFAULT')), websocket_timeout=900, websocket_kwargs={'max_size': 999999999}))
    try:
        w3Request = True
        while w3Request:
            try:
                from_address = web3.eth.ChecksumAddress(from_address)
                w3Request = False
            except Exception as e:
                if not to_many_request(e):
                    raise Exception(str(e))
                else:
                    time.sleep(1)

        w3Request = True
        while w3Request:
            try:
                to_address = web3.eth.ChecksumAddress(to_address)
                w3Request = False
            except Exception as e:
                if not to_many_request(e):
                    raise Exception(str(e))
                else:
                    time.sleep(1)

        w3Request = True
        while w3Request:
            try:
                estimate = w3.eth.estimateGas({'to': to_address, 'from': from_address, 'value': w3.toWei(Decimal(str(value)), 'ether')})
                w3Request = False
            except Exception as e:
                if not to_many_request(e):
                    raise Exception(str(e))
                else:
                    time.sleep(1)

        w3Request = True
        while w3Request:
            try:
                estimate = int(estimate * float(multiply))
                w3Request = False
            except Exception as e:
                if not to_many_request(e):
                    raise Exception(str(e))
                else:
                    time.sleep(1)

        w3Request = True
        while w3Request:
            try:
                signed_txn = w3.eth.account.sign_transaction(dict(
                    nonce=(w3.eth.get_transaction_count(from_address) + int(nonce)),
                    # maxFeePerGas=3000000000,
                    # maxPriorityFeePerGas=2000000000,
                    gas=estimate,
                    gasPrice=w3.eth.gasPrice,
                    to=to_address,
                    value=w3.toWei(Decimal(value), 'ether'),
                    data=b'',
                    chainId=int(config('NODE', server + "_CHAIN")),
                ),
                    from_address_private,
                )
                w3Request = False
            except Exception as e:
                if not to_many_request(e):
                    raise Exception(str(e))
                else:
                    time.sleep(1)

        w3Request = True
        while w3Request:
            try:
                trans = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                w3Request = False
            except Exception as e:
                if not to_many_request(e):
                    raise Exception(str(e))
                else:
                    time.sleep(1)

        return {
            "status": "success",
            "txh": w3.toHex(trans)
        }
    except Exception as e:
        return {
            "status": "fail",
            "message": str(e)
        }
