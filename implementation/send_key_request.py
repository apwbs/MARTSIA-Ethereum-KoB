from decouple import config
from web3 import Web3
import time
# from web3.middleware import geth_poa_middleware  # Avalanche

# Goerli
# web3 = Web3(Web3.HTTPProvider("https://goerli.infura.io/v3/059e54a94bca48d893f1b2d45470c002"))

# Mumbai
web3 = Web3(Web3.HTTPProvider("https://polygon-mumbai.g.alchemy.com/v2/vPOruPqyAIJXHPil7CE703mfy8_F4h8m"))

# Avalanche
# web3 = Web3(Web3.HTTPProvider("https://avalanche-fuji.infura.io/v3/059e54a94bca48d893f1b2d45470c002"))
# web3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Sepolia
# web3 = Web3(Web3.HTTPProvider("https://sepolia.infura.io/v3/059e54a94bca48d893f1b2d45470c002"))

process_instance_id = config('PROCESS_INSTANCE_ID')

authority1_address = config('AUTHORITY1_ADDRESS')
authority2_address = config('AUTHORITY2_ADDRESS')
authority3_address = config('AUTHORITY3_ADDRESS')
authority4_address = config('AUTHORITY4_ADDRESS')

manufacturer_address = config('DATAOWNER_MANUFACTURER_ADDRESS')
manufacturer_private_key = config('DATAOWNER_MANUFACTURER_PRIVATEKEY')
electronics_address = config('READER_ADDRESS_SUPPLIER1')
electronics_private_key = config('READER_PRIVATEKEY_SUPPLIER1')
mechanics_address = config('READER_ADDRESS_SUPPLIER2')
mechanics_private_key = config('READER_PRIVATEKEY_SUPPLIER2')

address_requesting = electronics_address
private_key_requesting = electronics_private_key
authority_address = authority4_address


def send_key_request():
    start = time.time()
    nonce = web3.eth.getTransactionCount(address_requesting)
    tx = {
        'chainId': 80001,     # Polygon testnet: Mumbai
        # 'chainId': 43113,       # Avalanche testnet: Fuji
        # 'chainId': 11155111,  # Ethereum testnet: Sepolia
        'nonce': nonce,
        'to': authority_address,
        'value': 0,
        'gas': 40000,
        'gasPrice': web3.toWei(web3.eth.gasPrice, 'wei'),  # Polygon testnet: Mumbai, Ethereum testnet: Sepolia
        # 'gasPrice': 25000000000,  # Avalanche testnet: Fuji
        'data': web3.toHex(b'generate your part of my key,bob,' + process_instance_id.encode())
    }

    signed_tx = web3.eth.account.sign_transaction(tx, private_key_requesting)

    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print(f'tx_hash: {web3.toHex(tx_hash)}')
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)
    print(tx_receipt)
    end = time.time()
    print('The time for sending a key request (blockchain execution) is :', (end - start) * 10 ** 3, 'ms')



if __name__ == "__main__":
    send_key_request()
    