from charm.toolbox.pairinggroup import *
from maabe_class import *
import block_int
import mpc_setup
from decouple import config
import io
import sqlite3
import time
from charm.core.engine.util import objectToBytes, bytesToObject
import ipfshttpclient

process_instance_id_env = config('PROCESS_INSTANCE_ID')

authority4_address = config('AUTHORITY4_ADDRESS')
authority4_private_key = config('AUTHORITY4_PRIVATEKEY')

authority1_address = config('AUTHORITY1_ADDRESS')
authority2_address = config('AUTHORITY2_ADDRESS')
authority3_address = config('AUTHORITY3_ADDRESS')

authorities_list = [authority1_address, authority2_address, authority3_address, authority4_address]
authorities_names = ['UT', 'OU', 'OT', 'TU']

# Connection to SQLite3 authority4 database
conn = sqlite3.connect('files/authority4/authority4.db')
x = conn.cursor()


def save_authorities_names(api, process_instance_id):
    start = time.time()
    f = io.StringIO()
    for i, addr in enumerate(authorities_list):
        f.write('process_instance: ' + str(process_instance_id) + '\n')
        f.write('identification: ' + 'authority ' + str(i + 1) + '\n')
        f.write('name: ' + str(authorities_names[i]) + '\n')
        f.write('address: ' + addr + '\n\n')
    f.seek(0)

    file_to_str = f.read()
    hash_file = api.add_json(file_to_str)
    print(f'ipfs hash: {hash_file}')
    generate_hash_file_time = time.time()

    block_int.send_authority_names(authority4_address, authority4_private_key, process_instance_id, hash_file)
    blockchain_execution = time.time()

    x.execute("INSERT OR IGNORE INTO authority_names VALUES (?,?,?)",
              (str(process_instance_id), hash_file, file_to_str))
    conn.commit()
    local_saving = time.time()

    print('The time for hash file generation by authority 4 is :', (generate_hash_file_time - start) * 10 ** 3, 'ms')
    print('The time for blockchain execution by authority 4 is :',
          (blockchain_execution - generate_hash_file_time) * 10 ** 3, 'ms')
    print('The time for local saving by authority 4 is :', (local_saving - blockchain_execution) * 10 ** 3, 'ms')


def initial_parameters_hashed(groupObj, process_instance_id):
    start = time.time()
    g1_4 = groupObj.random(G1)
    g2_4 = groupObj.random(G2)
    elements_generation = time.time()
    (h1_4, h2_4) = mpc_setup.commit(groupObj, g1_4, g2_4)
    elements_hashing = time.time()

    block_int.sendHashedElements(authority4_address, authority4_private_key, process_instance_id, (h1_4, h2_4))
    blockchain_execution = time.time()

    x.execute("INSERT OR IGNORE INTO h_values VALUES (?,?,?)", (str(process_instance_id), h1_4, h2_4))
    conn.commit()

    g1_4_bytes = groupObj.serialize(g1_4)
    g2_4_bytes = groupObj.serialize(g2_4)

    x.execute("INSERT OR IGNORE INTO g_values VALUES (?,?,?)", (str(process_instance_id), g1_4_bytes, g2_4_bytes))
    conn.commit()
    local_saving = time.time()

    print('The time for elements generation by authority 4 is :', (elements_generation - start) * 10 ** 3, 'ms')
    print('The time for elements hashing by authority 4 is :', (elements_hashing - elements_generation) * 10 ** 3, 'ms')
    print('The time for blockchain execution by authority 4 is :', (blockchain_execution - elements_hashing) * 10 ** 3,
          'ms')
    print('The time for local saving by authority 4 is :', (local_saving - blockchain_execution) * 10 ** 3, 'ms')


def initial_parameters(process_instance_id):
    start = time.time()
    x.execute("SELECT * FROM g_values WHERE process_instance=?", (str(process_instance_id),))
    result = x.fetchall()
    g1_4_bytes = result[0][1]
    g2_4_bytes = result[0][2]
    local_retrieve = time.time()

    block_int.sendElements(authority4_address, authority4_private_key, process_instance_id, (g1_4_bytes, g2_4_bytes))
    blockchain_execution = time.time()
    print('The time for local retrieve by authority 4 is :', (local_retrieve - start) * 10 ** 3, 'ms')
    print('The time for blockchain execution by authority 4 is :', (blockchain_execution - local_retrieve) * 10 ** 3,
          'ms')


def generate_public_parameters(groupObj, maabe, api, process_instance_id):
    start = time.time()
    x.execute("SELECT * FROM g_values WHERE process_instance=?", (str(process_instance_id),))
    result = x.fetchall()
    g1_4_bytes = result[0][1]
    g1_4 = groupObj.deserialize(g1_4_bytes)
    g2_4_bytes = result[0][2]
    g2_4 = groupObj.deserialize(g2_4_bytes)

    x.execute("SELECT * FROM h_values WHERE process_instance=?", (str(process_instance_id),))
    result = x.fetchall()
    h1 = result[0][1]
    h2 = result[0][2]
    retrieve_auth4_parameters_time = time.time()

    ####################
    #######AUTH1########
    ####################
    g1g2_1_hashed = block_int.retrieveHashedElements(authority1_address, process_instance_id)

    g1g2_1 = block_int.retrieveElements(authority1_address, process_instance_id)
    g1_1 = g1g2_1[0]
    g1_1 = groupObj.deserialize(g1_1)
    g2_1 = g1g2_1[1]
    g2_1 = groupObj.deserialize(g2_1)
    retrieve_auth1_parameters_time = time.time()

    ####################
    #######AUTH2########
    ####################
    g1g2_2_hashed = block_int.retrieveHashedElements(authority2_address, process_instance_id)

    g1g2_2 = block_int.retrieveElements(authority2_address, process_instance_id)
    g1_2 = g1g2_2[0]
    g1_2 = groupObj.deserialize(g1_2)
    g2_2 = g1g2_2[1]
    g2_2 = groupObj.deserialize(g2_2)
    retrieve_auth2_parameters_time = time.time()

    ####################
    #######AUTH3########
    ####################
    g1g2_3_hashed = block_int.retrieveHashedElements(authority3_address, process_instance_id)

    g1g2_3 = block_int.retrieveElements(authority3_address, process_instance_id)
    g1_3 = g1g2_3[0]
    g1_3 = groupObj.deserialize(g1_3)
    g2_3 = g1g2_3[1]
    g2_3 = groupObj.deserialize(g2_3)
    retrieve_auth3_parameters_time = time.time()

    #############################
    ##########VALUES#############
    #############################
    hashes1 = [g1g2_1_hashed[0], g1g2_2_hashed[0], g1g2_3_hashed[0], h1]
    hashes2 = [g1g2_1_hashed[1], g1g2_2_hashed[1], g1g2_3_hashed[1], h2]
    com1 = [g1_1, g1_2, g1_3, g1_4]
    com2 = [g2_1, g2_2, g2_3, g2_4]
    (value1, value2) = mpc_setup.generateParameters(groupObj, hashes1, hashes2, com1, com2)
    generate_values_time = time.time()

    public_parameters = maabe.setup(value1, value2)
    generate_parameters_time = time.time()
    public_parameters_reduced = dict(list(public_parameters.items())[0:3])
    pp_reduced = objectToBytes(public_parameters_reduced, groupObj)

    file_to_str = pp_reduced.decode('utf-8')
    hash_file = api.add_json(file_to_str)
    print(f'ipfs hash: {hash_file}')
    generate_hash_file_time = time.time()

    block_int.send_parameters_link(authority4_address, authority4_private_key, process_instance_id, hash_file)
    blockchain_execution = time.time()

    x.execute("INSERT OR IGNORE INTO public_parameters VALUES (?,?,?)",
              (str(process_instance_id), hash_file, file_to_str))
    conn.commit()
    local_saving = time.time()

    print('The time to retrieve auth4 elements by authority 4 is :', (retrieve_auth4_parameters_time - start) * 10 ** 3,
          'ms')
    print('The time to retrieve auth1 elements by authority 4 is :',
          (retrieve_auth1_parameters_time - retrieve_auth4_parameters_time) * 10 ** 3, 'ms')
    print('The time to retrieve auth2 elements by authority 4 is :',
          (retrieve_auth2_parameters_time - retrieve_auth1_parameters_time) * 10 ** 3, 'ms')
    print('The time to retrieve auth3 elements by authority 4 is :',
          (retrieve_auth3_parameters_time - retrieve_auth2_parameters_time) * 10 ** 3, 'ms')
    print('The time to generate values by authority 4 is :',
          (generate_values_time - retrieve_auth3_parameters_time) * 10 ** 3, 'ms')
    print('The time to generate parameters by authority 4 is :',
          (generate_parameters_time - generate_values_time) * 10 ** 3, 'ms')
    print('The time to generate hash file by authority 4 is :',
          (generate_hash_file_time - generate_parameters_time) * 10 ** 3, 'ms')
    print('The time for blockchain execution by authority 4 is :',
          (blockchain_execution - generate_hash_file_time) * 10 ** 3, 'ms')
    print('The time for local saving by authority 4 is :', (local_saving - blockchain_execution) * 10 ** 3, 'ms')


def retrieve_public_parameters(process_instance_id):
    x.execute("SELECT * FROM public_parameters WHERE process_instance=?", (str(process_instance_id),))
    result = x.fetchall()
    public_parameters = result[0][2].encode()
    return public_parameters


def generate_pk_sk(groupObj, maabe, api, process_instance_id):
    start = time.time()
    response = retrieve_public_parameters(process_instance_id)
    public_parameters = bytesToObject(response, groupObj)
    H = lambda x: self.group.hash(x, G2)
    F = lambda x: self.group.hash(x, G2)
    public_parameters["H"] = H
    public_parameters["F"] = F
    local_params_retrieve = time.time()

    # authsetup 2AA
    (pk4, sk4) = maabe.authsetup(public_parameters, 'TU')
    generation_keys_time = time.time()
    pk4_bytes = objectToBytes(pk4, groupObj)
    sk4_bytes = objectToBytes(sk4, groupObj)

    file_to_str = pk4_bytes.decode('utf-8')
    hash_file = api.add_json(file_to_str)
    print(f'ipfs hash: {hash_file}')
    generate_hash_file_time = time.time()

    block_int.send_publicKey_link(authority4_address, authority4_private_key, process_instance_id, hash_file)
    blockchain_execution = time.time()

    x.execute("INSERT OR IGNORE INTO private_keys VALUES (?,?)", (str(process_instance_id), sk4_bytes))
    conn.commit()

    x.execute("INSERT OR IGNORE INTO public_keys VALUES (?,?,?)", (str(process_instance_id), hash_file, pk4_bytes))
    conn.commit()
    local_saving = time.time()

    print('The time to local retrieve by authority 4 is :', (local_params_retrieve - start) * 10 ** 3, 'ms')
    print('The time to generate keys by authority 4 is :', (generation_keys_time - local_params_retrieve) * 10 ** 3,
          'ms')
    print('The time to generate hash file by authority 4 is :',
          (generate_hash_file_time - generation_keys_time) * 10 ** 3, 'ms')
    print('The time for blockchain execution by authority 4 is :',
          (blockchain_execution - generate_hash_file_time) * 10 ** 3, 'ms')
    print('The time for local saving by authority 4 is :', (local_saving - blockchain_execution) * 10 ** 3, 'ms')


def main():
    groupObj = PairingGroup('SS512')
    maabe = MaabeRW15(groupObj)
    api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
    process_instance_id = int(process_instance_id_env)

    ###########
    ###########
    ###LINES###
    ###########
    ###########
    # save_authorities_names(api, process_instance_id)
    # initial_parameters_hashed(groupObj, process_instance_id)
    # initial_parameters(process_instance_id)
    # generate_public_parameters(groupObj, maabe, api, process_instance_id)
    generate_pk_sk(groupObj, maabe, api, process_instance_id)


if __name__ == '__main__':
    main()
