from web3 import Web3
from helper import _parseValue
from config import config
from helper import to_many_request
import time


def getTransaction(txh, server):
    w3 = Web3(Web3.WebsocketProvider(config('NODE', server).format(config('MORALIS', 'DEFAULT')), websocket_timeout=900, websocket_kwargs={'max_size': 999999999}))
    # get_raw_transaction = w3.eth.get_raw_transaction(txh)
    try:
        w3Request = True
        while w3Request:
            try:
                transaction = w3.eth.get_transaction(txh)
                w3Request = False
            except Exception as e:
                if not to_many_request(e):
                    raise Exception(str(e))
                else:
                    time.sleep(1)
        w3Request = True
        while w3Request:
            try:
                transaction_receipt = w3.eth.get_transaction_receipt(txh)
                w3Request = False
            except Exception as e:
                if not to_many_request(e):
                    raise Exception(str(e))
                else:
                    time.sleep(1)

        return {
            'status': 'success',
            'transaction': _parseValue(transaction),
            'transaction_receipt': _parseValue(transaction_receipt)
        }
    except Exception as e:
        return {
            "status": "fail",
            "message": str(e)
        }
