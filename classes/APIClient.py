import hashlib
import json
import os
import time

import requests

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import unpad
from Crypto.Util.Padding import pad
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2

import base64


class APIClient:
    server_url : str = 'https://euky.ca/'

    base_key : bytes 
    ''' one part of encryption key '''

    salt : str = '38grn6yF4f8N7Ku7ijglK'


    session_key : str = ''
    session_value : str = ''
    session_encryption_key : str = ''
    session_password : str = ''

    username : str = ''

    def __init__(self) -> None:
        self.base_key = base64.b64decode('ux1ONSVRCXTSHKNz/8A7mZ3NmvQjZDQpOcqmDNKsH3M=')

    def save_session(self):
        ''' save session info to file only for debugging '''
        with open('session.json', 'w') as f:
            f.write(json.dumps({
                'username' : self.username,
                'session_key' : self.session_key,
                'session_value' : self.session_value,
                'session_encryption_key' : self.session_encryption_key,
                'session_password' : self.session_password
            }))

    def load_session(self) -> bool:
        ''' load session info from file only for debugging '''
        if os.path.exists('session.json') == False:
            return False
        with open('session.json', 'r') as f:
            data = json.loads(f.read())

            self.username = data['username']
            self.session_key = data['session_key']
            self.session_value = data['session_value']
            self.session_encryption_key = data['session_encryption_key']
            self.session_password = data['session_password']
        
        return True

    def login(self, username : str, password : str) -> bool:

        self.username = username
        url = self.server_url + '`login'

        password = password+self.salt
        password = hashlib.md5(password.encode()).hexdigest()
        timestamp = int(time.time()) 

        payload = json.dumps({ 'username': username, 'time' : timestamp })

        encrypted_payload = self.encrypt_message(payload, password, self.base_key)

        #payload
        data = { 'username' : username, 'payload': encrypted_payload }

        #send payload
        response = requests.post(url, data=data)

        #decrypt payload
        jsonData = json.loads(response.text)
        if 'payload' not in jsonData:
            return False

        payload_json = self.decrypt_message(jsonData['payload'], password, self.base_key)
        payload_json = json.loads(payload_json)
        
        if 'key' not in payload_json or 'value' not in payload_json or 'encryption_key' not in payload_json:
            return False
        
        #set session info for encrypted api
        self.session_password = password
        self.session_key = payload_json["key"]
        self.session_value = payload_json["value"]
        self.session_encryption_key = payload_json['encryption_key']+self.salt
        self.session_encryption_key = hashlib.md5(self.session_encryption_key.encode()).hexdigest()

        return True

    def request(self, path : str, payload : dict = {}):
        ''' makes an encrypted api request with server '''
        url = self.server_url+'`'+path

        timestamp = int(time.time()) 

        payload_json = json.dumps(payload)
        encrypted_payload = self.encrypt_message(payload_json, self.session_encryption_key, self.base_key)
        data = { 'payload': encrypted_payload }
        data[self.session_key] = self.session_value


        response = requests.post(url, data=data)

        jsonData = json.loads(response.text)
        if 'payload' not in jsonData:
            return False

        payload_json = self.decrypt_message(jsonData['payload'], self.session_password, self.base_key)
        payload_json = json.loads(payload_json)

        return payload_json


    def encrypt_message(self, message, password, key):
        key = PBKDF2(password, key, count=1000, dkLen=32, hmac_hash_module=SHA256)  # Derive a 256-bit key using PBKDF2
        cipher = AES.new(key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(message.encode(), AES.block_size))
        print("KEY: " +  base64.b64encode(key).decode('utf-8'))
        print("IV: " +  base64.b64encode(cipher.iv).decode('utf-8'))
        print("CT: " +  base64.b64encode(ct_bytes).decode('utf-8'))

        return base64.b64encode(cipher.iv + ct_bytes ).decode('utf-8')

    def decrypt_message(self, encrypted_message, password, key):
        key = PBKDF2(password, key, count=1000, dkLen=32, hmac_hash_module=SHA256)  # Derive a 256-bit key using PBKDF2
        #print("KEY: ", password)
        #print("PASSWORD: ", password)
        #print("DECRYPT KEY: ", base64.b64encode(key).decode('utf-8'))
        iv_and_ct = base64.b64decode(encrypted_message)
        iv = iv_and_ct[:AES.block_size]
        ct_bytes = iv_and_ct[AES.block_size:]

        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_message = unpad(cipher.decrypt(ct_bytes), AES.block_size)
        return decrypted_message.decode('utf-8')