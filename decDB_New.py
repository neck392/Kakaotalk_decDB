import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def generate_pragma(uuid, modelName, serialNumber, key):
    iv = bytes([0] * 16)
    pragma = f"{uuid}|{modelName}|{serialNumber}"
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_pragma = cipher.encrypt(pad(pragma.encode(), AES.block_size))
    hashed_pragma = hashlib.sha512(encrypted_pragma).digest()
    encoded_hashed_pragma = base64.b64encode(hashed_pragma)
    return encoded_hashed_pragma.decode()

def generate_key_and_iv(pragma, userId):
    key = pragma + userId
    while len(key) < 512:
        key += key
    key = key[:512]
    key_hash = hashlib.md5(key.encode()).digest()
    iv = hashlib.md5(base64.b64encode(key_hash)).digest()
    return key_hash, iv

def decrypt_database(key, iv, encDB):
    decDB = b''
    i = 0
    while i < len(encDB):
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_data = cipher.decrypt(encDB[i:i+4096])
        decDB += decrypted_data
        i += 4096
    return decDB

def read_encrypted_data_from_file(input_filename):
    with open(input_filename, 'rb') as f:
        encDB = f.read()
    return encDB

def save_to_file(decDB, output_filename):
    with open(output_filename, 'wb') as f:
        f.write(decDB)

# reg : HKEY_CURRENT_USER\Software\Kakao\KakaoTalk\DeviceInfo\20230613-224538-107
uuid = "54E23162-308C-D84D-AE3A-FBFD155A538E"
modelName = "KINGSTON RBUSNS8154P3256GJ"
serialNumber = "0026_B768_2E19_CD85."
userId = "188939636"
input_filename = 'chatLogs_365877719440833.edb'

# reg : HKLM\System\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\{c4def0e5-d3ee-4e8a-adf9-df1ba48a4f5a}
keys = [
    "1070fe58019a4d488a6ce02d9286aabb",
    "4a8c14e149954920b2ca88ea23f6f029",
    "60f533f580aa4a668f8a4a03fbaab3a5",
    "80714702d5cc49deb65ff5ff0ab048ac",
    "97b83a40292f4f54a2204b5cec7da166",
    "aa85c9df01f34ad6a909a6870ab80312",
    "b04f14d2ae334dcba785d40b51f70cf7",
    "b9c307637fbd4fd78e81aaa5e90e4fd6",
    "bf60d3f1089c4c6f829076e4c68617de",
    "c37150d489e147889dd2caa2dacde7c7",
    "c4def0e5d3ee4e8aadf9df1ba48a4f5a",
    "ce35ab8752b811eaa0ef806e6f6e6963",
    "d82c75b5c999406fa2235103ab900a07",
    "dec8c9b560b7474fb4f00ea7f7737764",
    "e15caf15e5c94e538804c755151840bc"
]

for i, hex_key in enumerate(keys):
    key = bytes.fromhex(hex_key)
    pragma = generate_pragma(uuid, modelName, serialNumber, key)
    key, iv = generate_key_and_iv(pragma, userId)
    print(f"Number {i+1}:")
    print(f"Pragma: {pragma}")
    print(f"Key: {key.hex()}")
    print(f"IV: {iv.hex()}")
    encDB = read_encrypted_data_from_file(input_filename)
    decDB = decrypt_database(key, iv, encDB)
    output_filename = f'chatLogs_365877719440833_dec_{i+1}.db'
    save_to_file(decDB, output_filename)
    print(f"Decrypted data saved to: {output_filename}\n")
