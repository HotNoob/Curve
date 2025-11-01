#pip install pycryptodome 
#conda install conda-forge::pycryptodome


from classes.APIClient import APIClient


import binascii



apiClient : APIClient = APIClient()
if apiClient.login('test_user', 'testing1234'):
    result = apiClient.request('check_session')
    print(result)
else:
    print('failed to login')


quit()
# Example usage:
message = "Hello, World!"
key_base64 = 'ux1ONSVRCXTSHKNz/8A7mZ3NmvQjZDQpOcqmDNKsH3M='
key = base64.b64decode(key_base64)  
password = hashlib.md5('test password'.encode()).hexdigest()

#key = get_random_bytes(32) # aes-256
key_base64 = base64.b64encode(key).decode('utf-8')
print("Key B64:", key_base64)

encrypted_message = encrypt_message(message, password, key)
print("Encrypted message:", encrypted_message)

decrypted_message = decrypt_message(encrypted_message, password, key)
print("Decrypted message:", decrypted_message)

php_encrypted_message = 'K9bR4Q4c5aHzyVdid0hV3vaI05XuBLsVmkYMkZmdNes='

php_decrypted_message = decrypt_message(php_encrypted_message, password, key)
print("PHP Decrypted message:", php_decrypted_message)


#make request to to login
import requests

salt = '38grn6yF4f8N7Ku7ijglK'
username = "test_user"
password = "testing1234"+salt
password = hashlib.md5(password.encode()).hexdigest()
timestamp = int(time.time()) 


url = 'http://localhost:8080/curvewebserver/api/login.php'
myobj = { 'username': username, 'time' : timestamp }

payload = json.dumps(myobj)
encrypted_payload = encrypt_message(payload, password, key)
print(payload)
data = { 'username' : username, 'payload': encrypted_payload }

response = requests.post(url, data=data)
print(response.text)

#decrypt payload
jsonData = json.loads(response.text)
if 'payload' not in jsonData:
    print('failed to login')
    quit()

payload_json = decrypt_message(jsonData['payload'], password, key)
payload_json = json.loads(payload_json)
print(payload_json)

session_key = payload_json["key"]
session_value = payload_json["value"]
session_encryption_key = payload_json['encryption_key']+salt
session_encryption_key = hashlib.md5(session_encryption_key.encode()).hexdigest()

#check session
url = 'http://localhost:8080/curvewebserver/api/check_session.php'

timestamp = int(time.time()) 
myobj = { 'username': username, 'time' : timestamp }

payload = json.dumps(myobj)
encrypted_payload = encrypt_message(payload, session_encryption_key, key)
print(payload)
data = { 'payload': encrypted_payload }

response = requests.post(url, data=data)