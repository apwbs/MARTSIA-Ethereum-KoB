import time
from charm.toolbox.pairinggroup import *
from maabe_class import *
from decouple import config
from charm.core.engine.util import objectToBytes, bytesToObject
import ipfshttpclient
import block_int
import sqlite3
import json


def retrieve_public_parameters(process_instance_id):
    # Connection to SQLite3 authority1 database
    conn = sqlite3.connect('files/authority1/authority1.db')
    x = conn.cursor()

    x.execute("SELECT * FROM public_parameters WHERE process_instance=?", (str(process_instance_id),))
    result = x.fetchall()
    public_parameters = result[0][2].encode()
    return public_parameters


def generate_user_key(gid, process_instance_id, reader_address):
    groupObj = PairingGroup('SS512')
    maabe = MaabeRW15(groupObj)
    api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

    start = time.time()
    # Connection to SQLite3 authority1 database
    conn = sqlite3.connect('files/authority1/authority1.db')
    x = conn.cursor()

    response = retrieve_public_parameters(process_instance_id)
    public_parameters = bytesToObject(response, groupObj)
    H = lambda x: self.group.hash(x, G2)
    F = lambda x: self.group.hash(x, G2)
    public_parameters["H"] = H
    public_parameters["F"] = F
    retrieve_pub_params_time = time.time()
    print('The time to retrieve pub params locally is :', (retrieve_pub_params_time - start) * 10 ** 3, 'ms')

    x.execute("SELECT * FROM private_keys WHERE process_instance=?", (str(process_instance_id),))
    result = x.fetchall()
    sk1 = result[0][1]
    sk1 = bytesToObject(sk1, groupObj)
    retrieve_priv_key_time = time.time()
    print('The time to retrieve priv key locally is :', (retrieve_priv_key_time - retrieve_pub_params_time) * 10 ** 3, 'ms')

    # keygen Bob
    attributes_ipfs_link = block_int.retrieve_users_attributes(process_instance_id)
    retrieve_usr_attr_time = time.time()
    print('The time to retrieve user attr is :', (retrieve_usr_attr_time - retrieve_priv_key_time) * 10 ** 3, 'ms')
    getfile = api.cat(attributes_ipfs_link)
    getfile = getfile.replace(b'\\', b'')
    getfile = getfile.decode('utf-8').rstrip('"').lstrip('"')
    getfile = getfile.encode('utf-8')
    getfile = getfile.split(b'####')
    attributes_dict = json.loads(getfile[1].decode('utf-8'))
    user_attr1 = attributes_dict[reader_address]
    user_attr1 = [k for k in user_attr1 if k.endswith('@UT')]
    start_ma_keygen_time = time.time()
    user_sk1 = maabe.multiple_attributes_keygen(public_parameters, sk1, gid, user_attr1)
    end_ma_keygen_time = time.time()
    print('The time to generate a key is :', (end_ma_keygen_time - start_ma_keygen_time) * 10 ** 3, 'ms')
    user_sk1_bytes = objectToBytes(user_sk1, groupObj)
    return user_sk1_bytes
