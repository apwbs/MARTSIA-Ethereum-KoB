import time

from charm.toolbox.pairinggroup import *
from charm.core.engine.util import objectToBytes, bytesToObject
import cryptocode
import block_int
from decouple import config
import ipfshttpclient
import json
from maabe_class import *
from datetime import datetime
import random
import sqlite3

authority1_address = config('AUTHORITY1_ADDRESS')
authority2_address = config('AUTHORITY2_ADDRESS')
authority3_address = config('AUTHORITY3_ADDRESS')
authority4_address = config('AUTHORITY4_ADDRESS')

dataOwner_address = config('DATAOWNER_MANUFACTURER_ADDRESS')
dataOwner_private_key = config('DATAOWNER_MANUFACTURER_PRIVATEKEY')

process_instance_id_env = config('PROCESS_INSTANCE_ID')

# Connection to SQLite3 data_owner database
conn = sqlite3.connect('files/data_owner/data_owner.db')
x = conn.cursor()


def retrieve_data(authority_address, process_instance_id):
    start = time.time()
    authorities = block_int.retrieve_authority_names(authority_address, process_instance_id)
    retrieve_auth_names_time = time.time()
    print('The time to retrieve auth names from blockchain is :', (retrieve_auth_names_time - start) * 10 ** 3, 'ms')
    public_parameters = block_int.retrieve_parameters_link(authority_address, process_instance_id)
    retrieve_pub_params_time = time.time()
    print('The time to retrieve pub params from blockchain is :', (retrieve_pub_params_time - retrieve_auth_names_time) * 10 ** 3, 'ms')
    public_key = block_int.retrieve_publicKey_link(authority_address, process_instance_id)
    retrieve_pub_keys_time = time.time()
    print('The time to retrieve pub keys from blockchain is :', (retrieve_pub_keys_time - retrieve_pub_params_time) * 10 ** 3, 'ms')
    return authorities, public_parameters, public_key


def generate_pp_pk(process_instance_id):
    check_authorities = []
    check_parameters = []

    data = retrieve_data(authority1_address, process_instance_id)
    start_local_save_1 = time.time()
    check_authorities.append(data[0])
    check_parameters.append(data[1])
    pk1 = api.cat(data[2])
    pk1 = pk1.decode('utf-8').rstrip('"').lstrip('"')
    pk1 = pk1.encode('utf-8')
    x.execute("INSERT OR IGNORE INTO authorities_public_keys VALUES (?,?,?,?)",
              (str(process_instance_id), 'Auth-1', data[2], pk1))
    conn.commit()
    end_local_save_1 = time.time()
    print('The time for local saving 1 is :', (end_local_save_1 - start_local_save_1) * 10 ** 3, 'ms')
    print()

    data = retrieve_data(authority2_address, process_instance_id)
    start_local_save_2 = time.time()
    check_authorities.append(data[0])
    check_parameters.append(data[1])
    pk2 = api.cat(data[2])
    pk2 = pk2.decode('utf-8').rstrip('"').lstrip('"')
    pk2 = pk2.encode('utf-8')
    x.execute("INSERT OR IGNORE INTO authorities_public_keys VALUES (?,?,?,?)",
              (str(process_instance_id), 'Auth-2', data[2], pk2))
    conn.commit()
    end_local_save_2 = time.time()
    print('The time for local saving 2 is :', (end_local_save_2 - start_local_save_2) * 10 ** 3, 'ms')
    print()

    data = retrieve_data(authority3_address, process_instance_id)
    start_local_save_3 = time.time()
    check_authorities.append(data[0])
    check_parameters.append(data[1])
    pk3 = api.cat(data[2])
    pk3 = pk3.decode('utf-8').rstrip('"').lstrip('"')
    pk3 = pk3.encode('utf-8')
    x.execute("INSERT OR IGNORE INTO authorities_public_keys VALUES (?,?,?,?)",
              (str(process_instance_id), 'Auth-3', data[2], pk3))
    conn.commit()
    end_local_save_3 = time.time()
    print('The time for local saving 3 is :', (end_local_save_3 - start_local_save_3) * 10 ** 3, 'ms')
    print()

    data = retrieve_data(authority4_address, process_instance_id)
    start_local_save_4 = time.time()
    check_authorities.append(data[0])
    check_parameters.append(data[1])
    pk4 = api.cat(data[2])
    pk4 = pk4.decode('utf-8').rstrip('"').lstrip('"')
    pk4 = pk4.encode('utf-8')
    x.execute("INSERT OR IGNORE INTO authorities_public_keys VALUES (?,?,?,?)",
              (str(process_instance_id), 'Auth-4', data[2], pk4))
    conn.commit()
    end_local_save_4 = time.time()
    print('The time for local saving 4 is :', (end_local_save_4 - start_local_save_4) * 10 ** 3, 'ms')
    print()

    start_local_save_5 = time.time()
    if len(set(check_authorities)) == 1 and len(set(check_parameters)) == 1:
        getfile = api.cat(check_parameters[0])
        getfile = getfile.decode('utf-8').rstrip('"').lstrip('"')
        getfile = getfile.encode('utf-8')
        x.execute("INSERT OR IGNORE INTO public_parameters VALUES (?,?,?)",
                  (str(process_instance_id), check_parameters[0], getfile))
        conn.commit()
        end_local_save_5 = time.time()
        print('The time for local saving 5 is :', (end_local_save_5 - start_local_save_5) * 10 ** 3, 'ms')


def retrieve_public_parameters(process_instance_id):
    x.execute("SELECT * FROM public_parameters WHERE process_instance=?", (str(process_instance_id),))
    result = x.fetchall()
    public_parameters = result[0][2]
    return public_parameters


def main(groupObj, maabe, api, process_instance_id):
    start = time.time()
    response = retrieve_public_parameters(process_instance_id)
    public_parameters = bytesToObject(response, groupObj)
    H = lambda x: self.group.hash(x, G2)
    F = lambda x: self.group.hash(x, G2)
    public_parameters["H"] = H
    public_parameters["F"] = F
    retrieve_pub_params_time = time.time()
    print('The time to retrieve pub params locally is :', (retrieve_pub_params_time - start) * 10 ** 3, 'ms')


    x.execute("SELECT * FROM authorities_public_keys WHERE process_instance=? AND authority_name=?",
              (str(process_instance_id), 'Auth-1'))
    result = x.fetchall()
    pk1 = result[0][3]
    pk1 = bytesToObject(pk1, groupObj)

    x.execute("SELECT * FROM authorities_public_keys WHERE process_instance=? AND authority_name=?",
              (str(process_instance_id), 'Auth-2'))
    result = x.fetchall()
    pk2 = result[0][3]
    pk2 = bytesToObject(pk2, groupObj)

    x.execute("SELECT * FROM authorities_public_keys WHERE process_instance=? AND authority_name=?",
              (str(process_instance_id), 'Auth-3'))
    result = x.fetchall()
    pk3 = result[0][3]
    pk3 = bytesToObject(pk3, groupObj)

    x.execute("SELECT * FROM authorities_public_keys WHERE process_instance=? AND authority_name=?",
              (str(process_instance_id), 'Auth-4'))
    result = x.fetchall()
    pk4 = result[0][3]
    pk4 = bytesToObject(pk4, groupObj)

    # public keys authorities
    pk = {'UT': pk1, 'OU': pk2, 'OT': pk3, 'TU': pk4}

    retrieve_pub_keys_time = time.time()
    print('The time to retrieve pub keys locally is :', (retrieve_pub_keys_time - retrieve_pub_params_time) * 10 ** 3, 'ms')

    f = open('files/data.json')
    data = json.load(f)
    # access_policy = ['(5892541979347588342@UT and 5892541979347588342@OU and 5892541979347588342@OT and '
    #                  '5892541979347588342@TU) and (MANUFACTURER@UT or SUPPLIER@OU)',
    #                  '(5892541979347588342@UT and 5892541979347588342@OU and 5892541979347588342@OT and '
    #                  '5892541979347588342@TU) and (MANUFACTURER@UT or (SUPPLIER@OU and ELECTRONICS@OT)',
    #                  '(5892541979347588342@UT and 5892541979347588342@OU and 5892541979347588342@OT and '
    #                  '5892541979347588342@TU) and (MANUFACTURER@UT or (SUPPLIER@OU and MECHANICS@TU)']
    #
    # entries = [['ID', 'SortAs', 'GlossTerm'], ['Acronym', 'Abbrev'], ['Specs', 'Dates']]

    access_policy = ['(5892541979347588342@UT and 5892541979347588342@OU '
                     'and 5892541979347588342@OT and 5892541979347588342@TU) '
                     'and (MANUFACTURER@UT or SUPPLIER@OU)']

    entries = [list(data.keys())]

    if len(access_policy) != len(entries):
        print('ERROR: The number of policies and entries is different')
        exit()

    keys = []
    header = []
    for i in range(len(entries)):
        key_group = groupObj.random(GT)
        key_encrypt = groupObj.serialize(key_group)
        keys.append(key_encrypt)
        key_encrypt_deser = groupObj.deserialize(key_encrypt)

        start_ma_encryption_time = time.time()
        ciphered_key = maabe.encrypt(public_parameters, pk, key_encrypt_deser, access_policy[i])
        end_ma_encryption_time = time.time()
        print('The time for ma encryption is :', (end_ma_encryption_time - start_ma_encryption_time) * 10 ** 3, 'ms')

        ciphered_key_bytes = objectToBytes(ciphered_key, groupObj)
        ciphered_key_bytes_string = ciphered_key_bytes.decode('utf-8')

        ## Possibility to clean the code here. This check can be done outside the 'for loop'
        if len(access_policy) == len(entries) == 1:
            dict_pol = {'CipheredKey': ciphered_key_bytes_string, 'Fields': entries[i]}
            header.append(dict_pol)
        else:
            now = datetime.now()
            now = int(now.strftime("%Y%m%d%H%M%S%f"))
            random.seed(now)
            slice_id = random.randint(1, 2 ** 64)
            dict_pol = {'Slice_id': slice_id, 'CipheredKey': ciphered_key_bytes_string, 'Fields': entries[i]}
            print(f'slice id {i}: {slice_id}')
            header.append(dict_pol)

    json_file_ciphered = {}
    for i, entry in enumerate(entries):
        ciphered_fields = []
        for field in entry:
            start_symmetric_encryption_field_time = time.time()
            cipher_field = cryptocode.encrypt(field, str(keys[i]))
            end_symmetric_encryption_field_time = time.time()
            print('The time symmetric field encryption is :', (end_symmetric_encryption_field_time - start_symmetric_encryption_field_time) * 10 ** 3, 'ms')
            ciphered_fields.append(cipher_field)
            start_symmetric_encryption_time = time.time()
            cipher = cryptocode.encrypt(data[field], str(keys[i]))
            end_symmetric_encryption_time = time.time()
            print('The time symmetric encryption is :', (end_symmetric_encryption_time - start_symmetric_encryption_time) * 10 ** 3, 'ms')
            json_file_ciphered[cipher_field] = cipher
        header[i]['Fields'] = ciphered_fields

    now = datetime.now()
    now = int(now.strftime("%Y%m%d%H%M%S%f"))
    random.seed(now)
    message_id = random.randint(1, 2 ** 64)
    metadata = {'sender': dataOwner_address, 'process_instance_id': int(process_instance_id),
                'message_id': message_id}
    print(f'message id: {message_id}')

    json_total = {'metadata': metadata, 'header': header, 'body': json_file_ciphered}

    # encoded = cryptocode.encrypt("Ciao Marzia!", str(key_encrypt1))

    hash_file = api.add_json(json_total)
    print(f'ipfs hash: {hash_file}')
    generate_hash_file_time = time.time()

    block_int.send_MessageIPFSLink(dataOwner_address, dataOwner_private_key, message_id, hash_file)
    blockchain_execution = time.time()
    print('The time for blockchain execution is :', (blockchain_execution - generate_hash_file_time) * 10 ** 3, 'ms')

    x.execute("INSERT OR IGNORE INTO messages VALUES (?,?,?,?)",
              (str(process_instance_id), str(message_id), hash_file, str(json_total)))
    conn.commit()
    local_saving = time.time()
    print('The time for local saving is :', (local_saving - blockchain_execution) * 10 ** 3, 'ms')
    print('Total time for the run is :', (local_saving - start) * 10 ** 3, 'ms')


if __name__ == '__main__':
    groupObj = PairingGroup('SS512')
    maabe = MaabeRW15(groupObj)
    api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
    process_instance_id = int(process_instance_id_env)

    # generate_pp_pk(process_instance_id)
    main(groupObj, maabe, api, process_instance_id)
