import requests
from config import config
import json
from decimal import Decimal

headers = {"Accept": "application/json", "Content-Type": "application/json", "TRON-PRO-API-KEY": "251db50f-89f1-4200-8878-6285a46c6d14"}


def tronTransaction(from_address, from_address_private, to_address, value, server):
    value = int(Decimal(value) * Decimal(1000000))
    try:
        return broadcastTransaction(transactionSign(transaction(from_address, to_address, value, server), from_address_private, server), server)
    except Exception as e:
        return {
            "status": "fail",
            "message": str(e)
        }


def transaction(from_address, to_address, value, server):
    global headers
    try:
        url = config('NODE', server) + "/wallet/createtransaction"
        payload = {
            "to_address": to_address,
            "owner_address": from_address,
            "visible": True,
            "amount": value
        }
        response = requests.post(url, json=payload, headers=headers)
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


def transactionSign(transaction, from_address_private, server):
    global headers
    if 'status' in transaction and transaction['status'] == 'fail':
        return transaction
    try:
        url = config('NODE', 'TRX_PUBLIC_NODE') + "/wallet/gettransactionsign"
        response = requests.post(url, json={
            "transaction": transaction,
            "privateKey": from_address_private
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
            'txh': str(response['txid']),
        }
    except Exception as e:
        return {
            "status": "fail",
            "message": str(e)
        }
