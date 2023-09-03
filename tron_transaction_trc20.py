import requests
from config import config
import json
from tronpy.abi import trx_abi
from decimal import Decimal

headers = {"Accept": "application/json", "Content-Type": "application/json", "TRON-PRO-API-KEY": "251db50f-89f1-4200-8878-6285a46c6d14"}


def tronTransactionTRC20(from_address, private_key, to_address, contract_address, fee_limit, value, server):
    try:
        tokenDecimal = requests.get(config('NODE', server + "_SCAN") + "/contract?contract=" + contract_address).json()['data'][0]['tokenInfo']['tokenDecimal']
        value = int(Decimal(value) * Decimal(str(10 ** int(tokenDecimal))))
        return broadcastTransaction(transactionSign(triggerSmartContract(from_address, to_address, contract_address, fee_limit, value, server), private_key, server), server)
    except Exception as e:
        return {
            "status": "fail",
            "message": str(e)
        }


def triggerSmartContract(owner_address, to_address, contract_address, fee_limit, value, server):
    global headers
    try:
        prmtEncode = parameterEncode(to_address, value)
        if 'status' in prmtEncode and prmtEncode['status'] == 'fail':
            return prmtEncode
        url = config('NODE', server) + "/wallet/triggersmartcontract"
        response = requests.request("POST", url, json={
            "owner_address": owner_address,
            "contract_address": contract_address,
            "function_selector": 'transfer(address,uint256)',
            "call_value": 0,
            "parameter": prmtEncode,
            "fee_limit": fee_limit,
            "visible": True,
        }, headers=headers).json()
        if 'Error' in response:
            print("er-1")
            return {
                "status": "fail",
                "message": str(response['Error'])
            }
        return response['transaction']
    except Exception as e:
        print("er-2")
        return {
            "status": "fail",
            "message": str(e)
        }


def parameterEncode(to_address, amount):
    try:
        return trx_abi.encode_abi(['address', 'uint256'], [to_address, amount]).hex()
    except:
        return {
            "status": "fail",
            "message": "wrong_address"
        }


def transactionSign(transaction, private_key, server):
    global headers
    if 'status' in transaction and transaction['status'] == 'fail':
        print("err-878")
        return transaction
    try:
        url = config('NODE', 'TRX_PUBLIC_NODE') + "/wallet/gettransactionsign"
        response = requests.request("POST", url, json={
            "transaction": transaction,
            "privateKey": private_key
        }, headers=headers)
        if 'Error' in response.json():
            print("err-848")
            return {
                "status": "fail",
                "message": str(response.json()['Error'])
            }
        print(response.text)
        return response.text
    except Exception as e:
        print("a4")
        return {
            "status": "fail",
            "message": str(e)
        }


def broadcastTransaction(payload, server):
    global headers
    if 'status' in payload and payload['status'] == 'fail':
        return payload
    try:
        url = config('NODE', server) + "/wallet/broadcasttransaction"
        response = requests.request("POST", url, json=json.loads(payload), headers=headers).json()
        print("ok")
        return {
            'status': 'success',
            'txh': response['txid'],
        }
    except Exception as e:
        print("a5")
        return {
            "status": "fail",
            "message": str(e)
        }
