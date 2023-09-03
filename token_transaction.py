from web3 import Web3
from decimal import Decimal
import json
import math
from config import config
import os
from helper import to_many_request
import time


def tokenTransaction(from_address, from_address_private, to_address, value, contract_address, nonce=0, token_type='', multiply=1, server=''):
    try:
        with open(os.path.dirname(os.path.realpath(__file__)) + "/abis/" + token_type + ".json") as f:
            abi = json.load(f)
        w3 = Web3(Web3.WebsocketProvider(config('NODE', server).format(config('MORALIS', 'DEFAULT')), websocket_timeout=900, websocket_kwargs={'max_size': 999999999}))

        w3Request = True
        while w3Request:
            try:
                from_address = Web3.toChecksumAddress(from_address)
                w3Request = False
            except Exception as e:
                if not to_many_request(e):
                    raise Exception(str(e))
                else:
                    time.sleep(1)

        w3Request = True
        while w3Request:
            try:
                to_address = Web3.toChecksumAddress(to_address)
                w3Request = False
            except Exception as e:
                if not to_many_request(e):
                    raise Exception(str(e))
                else:
                    time.sleep(1)

        w3Request = True
        while w3Request:
            try:
                contract_address = Web3.toChecksumAddress(contract_address)
                w3Request = False
            except Exception as e:
                if not to_many_request(e):
                    raise Exception(str(e))
                else:
                    time.sleep(1)
        w3Request = True
        while w3Request:
            try:
                contract = w3.eth.contract(address=contract_address, abi=abi)
                w3Request = False
            except Exception as e:
                if not to_many_request(e):
                    raise Exception(str(e))
                else:
                    time.sleep(1)

        w3Request = True
        while w3Request:
            try:
                gas_price = w3.eth.gas_price
                w3Request = False
            except Exception as e:
                if not to_many_request(e):
                    raise Exception(str(e))
                else:
                    time.sleep(1)

        if server == 'ETH_TESTNET' or server == 'ETH_MAINNET':
            try:
                w3Request = True
                while w3Request:
                    try:
                        estimate = w3.eth.estimateGas({'to': to_address, 'from': from_address, 'value': w3.toWei(Decimal(str(value)), 'ether')})
                        estimate = int(estimate * float(multiply))
                        w3Request = False
                    except Exception as e:
                        if not to_many_request(e):
                            raise Exception(str(e))
                        else:
                            time.sleep(1)
            except:
                w3Request = True
                while w3Request:
                    try:
                        estimate = w3.eth.estimateGas({'to': to_address, 'from': from_address, 'value': 0})
                        estimate = int(estimate * float(multiply))
                        w3Request = False
                    except Exception as e:
                        if not to_many_request(e):
                            raise Exception(str(e))
                        else:
                            time.sleep(1)
        else:
            try:
                w3Request = True
                while w3Request:
                    try:
                        estimate = w3.eth.estimateGas({'to': contract_address, 'from': from_address, 'value': w3.toWei(Decimal(str(value)), 'ether')})
                        estimate = int(estimate * float(multiply))
                        w3Request = False
                    except Exception as e:
                        if not to_many_request(e):
                            raise Exception(str(e))
                        else:
                            time.sleep(1)

            except:
                w3Request = True
                while w3Request:
                    try:
                        estimate = w3.eth.estimateGas({'to': to_address, 'from': from_address, 'value': 0})
                        estimate = int(estimate * float(multiply))
                        w3Request = False
                    except Exception as e:
                        if not to_many_request(e):
                            raise Exception(str(e))
                        else:
                            time.sleep(1)
        # Build a transaction that invokes this contract's function, called transfer

        w3Request = True
        while w3Request:
            try:
                token_txn = contract.functions.transfer(
                    to_address,
                    w3.toWei(Decimal(value), 'ether'),
                ).buildTransaction({
                    'chainId': w3.eth.chainId,
                    'gas': math.floor(estimate),
                    'gasPrice': gas_price,
                    'nonce': (w3.eth.getTransactionCount(from_address) + int(nonce)),
                })
                w3Request = False
            except Exception as e:
                if not to_many_request(e):
                    raise Exception(str(e))
                else:
                    time.sleep(1)

        w3Request = True
        while w3Request:
            try:
                signed_txn = w3.eth.account.signTransaction(token_txn, private_key=from_address_private)
                w3Request = False
            except Exception as e:
                if not to_many_request(e):
                    raise Exception(str(e))
                else:
                    time.sleep(1)

        w3Request = True
        while w3Request:
            try:
                trans = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
                w3Request = False
            except Exception as e:
                if not to_many_request(e):
                    raise Exception(str(e))
                else:
                    time.sleep(1)

        return {
            "status": "success",
            "txh": w3.toHex(trans),
            "gas_price": gas_price
        }
    except Exception as e:
        return {
            "status": "fail",
            "message": str(e)
        }

# print(tokenTransaction("0x914c69916f0621b1350edbdb86c634b54955E44d", "0x22706fcc4f3c1bb5b0fd7cd12f99a8b8c301f527619dfeb5a804c0a209a31711", "0xcD4B7f4507101B0f11d0e3423ab8B0c00F689497", "0", "0xc5c720f82082a7cdbf3c6f5fdaecf922749d56e3"))
# 0xa36fe7cb81e97b3394731200310156cfd4eac4810ac796b9f8cb1c0ce5dfb8a7
