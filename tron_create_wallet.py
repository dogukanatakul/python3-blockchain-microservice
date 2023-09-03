import requests
from config import config


def tronCreateWallet(server):
    try:
        url = config('NODE', server) + "/wallet/generateaddress"
        response = requests.get(url).json()
        return {
            "status": "success",
            "address": response['address'],
            "address_hex": response['hexAddress'],
            "private_key": response['privateKey'],
        }
    except Exception as e:
        return {
            "status": "fail",
            "message": str(e)
        }
