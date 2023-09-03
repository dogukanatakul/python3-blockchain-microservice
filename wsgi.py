#!/usr/bin/env python
# -*-coding:utf-8-*-
from flask import Flask, request, json
from get_balance import getBalance
from get_token_balance import getTokenBalance
from get_transaction import getTransaction
from create_wallet import createWallet
from transaction import transaction
from token_transaction import tokenTransaction
from fee_calculator import feeCalculator
from tron_create_wallet import tronCreateWallet
from tron_transaction_trc20 import tronTransactionTRC20
from tron_transaction_trc10 import tronTransactionTRC10
from tron_transaction import tronTransaction
from status import statusNode

app = Flask(__name__)


@app.route("/")
def home():
    return "Bak vallahi 155'i ararım, biz kürtaj yapayoruz burda, vatan haini..."


@app.route("/status", methods=['GET'])
def status():
    if request.method == "GET":
        response = app.response_class(
            response=json.dumps(
                statusNode()
            ),
            status=200,
            mimetype='application/json'
        )
        return response


@app.route("/<server>/get_balance", methods=['GET', 'POST'])
def get_balance(server):
    if request.method == "POST":
        params = request.json
        if 'contract' in params:
            response = app.response_class(
                response=json.dumps(
                    getTokenBalance(params['wallet'], params['contract'], server)
                ),
                status=200,
                mimetype='application/json'
            )
        else:
            response = app.response_class(
                response=json.dumps(
                    getBalance(params['wallet'], server)
                ),
                status=200,
                mimetype='application/json'
            )
        return response


@app.route("/<server>/get_transaction", methods=['GET', 'POST'])
def get_transaction(server):
    params = request.json
    if 'txh' in params:
        response = app.response_class(
            response=json.dumps(
                getTransaction(params['txh'], server)
            ),
            status=200,
            mimetype='application/json'
        )
        return response


@app.route("/<server>/create_wallet", methods=['GET', 'POST'])
def create_wallet(server):
    if server == 'TRX_TESTNET' or server == 'TRX_MAINNET':
        response = app.response_class(
            response=json.dumps(
                tronCreateWallet(server)
            ),
            status=200,
            mimetype='application/json'
        )
    else:
        response = app.response_class(
            response=json.dumps(
                createWallet()
            ),
            status=200,
            mimetype='application/json'
        )

    return response


@app.route("/<server>/set_transaction", methods=['POST'])
def set_transaction(server):
    response = False
    params = request.json
    if server == 'TRX_TESTNET' or server == 'TRX_MAINNET' or server == 'TRX_PUBLIC_NODE':
        if 'token_type' in params and params['token_type'] == 'trc20':
            response = app.response_class(
                response=json.dumps(
                    tronTransactionTRC20(params['from_address'], params['from_address_private'], params['to_address'], params['contract_address'], params['fee_limit'], params['value'], server)
                ),
                status=200,
                mimetype='application/json'
            )
        elif 'token_type' in params and params['token_type'] == 'trc10':
            response = app.response_class(
                response=json.dumps(
                    tronTransactionTRC10(params['from_address'], params['from_address_private'], params['to_address'], params['asset_name'], params['value'], server)
                ),
                status=200,
                mimetype='application/json'
            )
        else:
            response = app.response_class(
                response=json.dumps(
                    tronTransaction(params['from_address'], params['from_address_private'], params['to_address'], params['value'], server)
                ),
                status=200,
                mimetype='application/json'
            )
    else:
        if 'nonce' not in params:
            params['nonce'] = 0
        if 'multiply' not in params:
            params['multiply'] = 1
        if 'contract_address' in params and 'token_type' in params:
            response = app.response_class(
                response=json.dumps(
                    tokenTransaction(params['from_address'], params['from_address_private'], params['to_address'], params['value'], params['contract_address'], params['nonce'], params['token_type'], params['multiply'], server)
                ),
                status=200,
                mimetype='application/json'
            )
        else:
            response = app.response_class(
                response=json.dumps(
                    transaction(params['from_address'], params['from_address_private'], params['to_address'], params['value'], params['nonce'], params['multiply'], server)
                ),
                status=200,
                mimetype='application/json'
            )
    return response


@app.route("/<server>/fee_calculator", methods=['POST'])
def fee_calculator(server):
    if request.method == "POST":
        params = request.json
        response = app.response_class(
            response=json.dumps(
                feeCalculator(params['value'], params['from_address'], params['to_address'], server)
            ),
            status=200,
            mimetype='application/json'
        )
        return response


if __name__ == "__main__":
    # app.run(host='185.254.94.202', port=1625, debug=True, threaded=True)
    app.run(host='127.0.0.1', port=1625, debug=True, threaded=True)
