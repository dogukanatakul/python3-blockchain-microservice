import requests
from config import config
import json
from tronpy.abi import trx_abi
from decimal import Decimal

headers = {"Accept": "application/json", "Content-Type": "application/json", "TRON-PRO-API-KEY": "251db50f-89f1-4200-8878-6285a46c6d14"}


def tronTransactionTRC10(from_address, from_address_private, to_address, asset_name, value, server):
    try:
        tokenDecimal = requests.post(config('NODE', server) + "/wallet/getassetissuebyid", json={
            "value": asset_name
        }).json()['precision']
        value = int(Decimal(str(value)) * Decimal(str(10 ** int(tokenDecimal))))
        return broadcastTransaction(transactionSign(transferAssetContract(from_address, to_address, asset_name, value, server), from_address_private, server), server)
    except Exception as e:
        return {
            "status": "fail",
            "message": str(e)
        }


def transferAssetContract(from_address, to_address, asset_name, value, server):
    global headers
    try:
        url = config('NODE', server) + "/wallet/transferasset"
        response = requests.post(url, json={
            "owner_address": from_address,
            "to_address": to_address,
            "asset_name": asset_name,
            "amount": value,
            "permission_id": None,
            "visible": True,
        }, headers=headers)
        if 'Error' in response.json():
            return {
                "status": "fail",
                "message": str(response.json()['Error'])
            }
        return response.text
    except Exception as e:
        return {
            "status": "fail",
            "message": str(e)
        }


def transactionSign(transaction, private_key, server):
    global headers
    if 'status' in transaction and transaction['status'] == 'fail':
        return transaction
    try:
        url = config('NODE', server) + "/wallet/gettransactionsign"
        response = requests.post(url, json={
            "transaction": transaction,
            "privateKey": private_key
        }, headers=headers)
        if 'Error' in response.json():
            return {
                "status": "fail",
                "message": str(response.json()['Error'])
            }
        return response.text
    except Exception as e:
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
        response = requests.post(url, json=json.loads(payload), headers=headers).json()
        return {
            'status': 'success',
            'txh': response['txid'],
        }
    except Exception as e:
        return {
            "status": "fail",
            "message": str(e)
        }
