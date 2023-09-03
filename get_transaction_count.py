from web3 import Web3
from config import config

w3 = Web3(Web3.WebsocketProvider(config('NODE', "BSC_MAINNET").format(config('MORALIS', 'DEFAULT')), websocket_timeout=900, websocket_kwargs={'max_size': 999999999}))
print(w3.eth.getTransactionCount('WALLET'))
