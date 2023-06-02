import time
from decouple import config
import authority4_keygeneration
import rsa
import block_int
from web3 import Web3
import io
import json
import base64
import ipfshttpclient
from web3.middleware import geth_poa_middleware  # Mumbai, Avalanche

api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

authority4_address = config('AUTHORITY4_ADDRESS')
authority4_private_key = config('AUTHORITY4_PRIVATEKEY')

# Goerli
# web3 = Web3(Web3.HTTPProvider("https://goerli.infura.io/v3/059e54a94bca48d893f1b2d45470c002"))

# Mumbai
web3 = Web3(Web3.HTTPProvider("https://polygon-mumbai.g.alchemy.com/v2/vPOruPqyAIJXHPil7CE703mfy8_F4h8m"))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Avalanche
# web3 = Web3(Web3.HTTPProvider("https://avalanche-fuji.infura.io/v3/059e54a94bca48d893f1b2d45470c002"))
# web3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Sepolia
# web3 = Web3(Web3.HTTPProvider("https://sepolia.infura.io/v3/059e54a94bca48d893f1b2d45470c002"))


def send_ipfs_link(reader_address, process_instance_id, hash_file):
    start = time.time()
    nonce = web3.eth.getTransactionCount(authority4_address)

    tx = {
        'chainId': 80001,  # Polygon testnet: Mumbai
        # 'chainId': 43113,  # Avalanche testnet: Fuji
        # 'chainId': 11155111,  # Ethereum testnet: Sepolia
        'nonce': nonce,
        'to': reader_address,
        'value': 0,
        'gas': 40000,
        'gasPrice': web3.toWei(web3.eth.gasPrice, 'wei'),  # Polygon testnet: Mumbai, Ethereum testnet: Sepolia
        # 'gasPrice': 25000000000,  # Avalanche testnet: Fuji
        'data': web3.toHex(hash_file.encode() + b',' + str(process_instance_id).encode())
    }

    signed_tx = web3.eth.account.sign_transaction(tx, authority4_private_key)

    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print(f'tx_hash: {web3.toHex(tx_hash)}')
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)
    print(tx_receipt)
    end = time.time()
    print('The time for blockchain execution is :', (end - start) * 10 ** 3, 'ms')


def generate_key(x):
    gid = bytes.fromhex(x['input'][2:]).decode('utf-8').split(',')[1]
    process_instance_id = int(bytes.fromhex(x['input'][2:]).decode('utf-8').split(',')[2])
    reader_address = x['from']
    key = authority4_keygeneration.generate_user_key(gid, process_instance_id, reader_address)
    cipher_generated_key(reader_address, process_instance_id, key)


def cipher_generated_key(reader_address, process_instance_id, generated_ma_key):
    start = time.time()
    public_key_ipfs_link = block_int.retrieve_publicKey_readers(reader_address)
    retrieve_pub_ke_time = time.time()
    print('The time to retrieve pub key is :', (retrieve_pub_ke_time - start) * 10 ** 3, 'ms')
    getfile = api.cat(public_key_ipfs_link)
    getfile = getfile.split(b'###')
    if getfile[0].split(b': ')[1].decode('utf-8') == reader_address:
        publicKey_usable = rsa.PublicKey.load_pkcs1(getfile[1].rstrip(b'"').replace(b'\\n', b'\n'))

        info = [generated_ma_key[i:i + 117] for i in range(0, len(generated_ma_key), 117)]

        f = io.BytesIO()
        start_rsa_encryption = time.time()
        for part in info:
            crypto = rsa.encrypt(part, publicKey_usable)
            f.write(crypto)
        end_rsa_encryption = time.time()
        print('The time for rsa encryption is :', (end_rsa_encryption - start_rsa_encryption) * 10 ** 3, 'ms')
        f.seek(0)

        file_to_str = f.read()
        j = base64.b64encode(file_to_str).decode('ascii')
        s = json.dumps(j)
        hash_file = api.add_json(s)
        print(f'ipfs hash: {hash_file}')

        send_ipfs_link(reader_address, process_instance_id, hash_file)


def transactions_monitoring():
    min_round = 36346599
    transactions = []
    note = 'generate your part of my key'
    while True:
        start = time.time()
        block = web3.eth.getBlock(min_round, True)
        get_block_time = time.time()
        print('The time for retrieving a block is :', (get_block_time - start) * 10 ** 3, 'ms')
        print(block.number)
        for transaction in block.transactions:
            if 'to' in transaction:
                if transaction['to'] == authority4_address and transaction['hash'] not in transactions \
                        and 'input' in transaction:
                    if bytes.fromhex(transaction['input'][2:]).decode('utf-8').split(',')[0] == note:
                        transactions.append(transaction)
        min_round = min_round + 1
        for x in transactions:
            generate_key(x)
            transactions.remove(x)
        end = time.time()
        print('Time for an entire run is: ', (end - start) * 10 ** 3, 'ms')
        time.sleep(5)


if __name__ == "__main__":
    transactions_monitoring()
