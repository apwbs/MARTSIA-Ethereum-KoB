import json
import time
from datetime import datetime
import random
import block_int
from decouple import config
import io
import sqlite3
import ipfshttpclient

api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

attribute_certifier_address = config('ATTRIBUTE_CERTIFIER_ADDRESS')
private_key = config('ATTRIBUTE_CERTIFIER_PRIVATEKEY')

manufacturer_address = config('DATAOWNER_MANUFACTURER_ADDRESS')
supplier1_address = config('READER_ADDRESS_SUPPLIER1')
supplier2_address = config('READER_ADDRESS_SUPPLIER2')

# Connection to SQLite3 attribute_certifier database
conn = sqlite3.connect('files/attribute_certifier/attribute_certifier.db')
x = conn.cursor()


def generate_attributes():
    start = time.time()
    now = datetime.now()
    now = int(now.strftime("%Y%m%d%H%M%S%f"))
    random.seed(now)
    process_instance_id = random.randint(1, 2 ** 64)
    print(f'process instance id: {process_instance_id}')

    dict_users = {
        manufacturer_address: [str(process_instance_id) + '@UT', str(process_instance_id) + '@OU',
                               str(process_instance_id) + '@OT', str(process_instance_id) + '@TU', 'MANUFACTURER@UT'],

        supplier1_address: [str(process_instance_id) + '@UT', str(process_instance_id) + '@OU',
                            str(process_instance_id) + '@OT', str(process_instance_id) + '@TU', 'SUPPLIER@OU',
                            'ELECTRONICS@OT'],

        supplier2_address: [str(process_instance_id) + '@UT', str(process_instance_id) + '@OU',
                            str(process_instance_id) + '@OT', str(process_instance_id) + '@TU', 'SUPPLIER@OU',
                            'MECHANICS@TU']
    }
    attributes_certification_time = time.time()

    f = io.StringIO()
    dict_users_dumped = json.dumps(dict_users)
    f.write('"process_instance_id": ' + str(process_instance_id) + '####')
    f.write(dict_users_dumped)
    f.seek(0)

    file_to_str = f.read()

    hash_file = api.add_json(file_to_str)
    print(f'ipfs hash: {hash_file}')
    generate_hash_file_time = time.time()

    block_int.send_users_attributes(attribute_certifier_address, private_key, process_instance_id, hash_file)
    blockchain_execution = time.time()

    x.execute("INSERT OR IGNORE INTO user_attributes VALUES (?,?,?)",
              (str(process_instance_id), hash_file, file_to_str))
    conn.commit()
    local_saving = time.time()

    print('The time for the attribute certification is :', (attributes_certification_time - start) * 10 ** 3, 'ms')
    print('The time for hash file generation is :', (generate_hash_file_time - attributes_certification_time) * 10 ** 3,
          'ms')
    print('The time for blockchain execution is :', (blockchain_execution - generate_hash_file_time) * 10 ** 3, 'ms')
    print('The time for local saving is :', (local_saving - blockchain_execution) * 10 ** 3, 'ms')


if __name__ == "__main__":
    generate_attributes()
