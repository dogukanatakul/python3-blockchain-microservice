from eth_account import Account
import secrets


def createWallet():
    priv = secrets.token_hex(32)
    private_key = "0x" + priv
    wallet = Account.from_key(private_key)
    return {
        "status": "success",
        "address": wallet.address,
        "private_key": private_key
    }

# SAVE BUT DO NOT SHARE THIS: 0x22706fcc4f3c1bb5b0fd7cd12f99a8b8c301f527619dfeb5a804c0a209a31711
# Address: 0x914c69916f0621b1350edbdb86c634b54955E44d
