import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

#def generate_pragma(uuid, modelName, serialNumber, key):
#    iv = bytes([0] * 16)
#    pragma = f"{uuid}|{modelName}|{serialNumber}"
#    cipher = AES.new(key, AES.MODE_CBC, iv)
#    encrypted_pragma = cipher.encrypt(pad(pragma.encode(), AES.block_size))
#    hashed_pragma = hashlib.sha512(encrypted_pragma).digest()
#    encoded_hashed_pragma = base64.b64encode(hashed_pragma)
#    return encoded_hashed_pragma.decode()

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

userId = "188939636"
input_filename = 'chatLogs_133748894318006.edb'

# Pragma values
pragmas = [
    "zzbNM7FzwRS0RKih4nYIC4z5gmMzhHNQm1s+gKVhMg4RlZC4RFBE0J4evgDIrxiheX58HAAAAABJRU5ErkJggg==", 
    "z6yh+a0Uz64sYZEs2ZfhWQ2xdt7qMhebaJrlqPdCd3KPPheAf+R+jXA0IDbPccmFhZ9i+NQzMEel7wf/bAtVtQ==", 
    "yIdGmtEut62Sgrg6TN6aeBqCKWFqpZutBnIB1TRSZt3x1sdshZ5jfNN74UbOCvHSMW0K2YLiC4utrc2hebrI6A==", 
    "SHS5F6dbOQQxVqBRU4pvqjbCDoh950qPcWbs+09Dpwbk\/3IDQNTvUqRnMQ0HgNBu4l+9GlyppU1Vybqwo6Kdg==", 
    "8SHS5F6dbOQQxVqBRU4pvqjbCDoh950qPcWbs+09Dpwbk/3IDQNTvUqRnMQ0HgNBu4l+9GlyppU1Vybqwo6Kdg==", 
    "JcuHbKLzQhwGEfKfTOe7QDZsM5wvB0YWDRzJebSdjFVoyZtzwXkpvAj1OloVyB_Z0ft1y3bwWdM3Qea5ZRBhGg==", 
]

encDB = read_encrypted_data_from_file(input_filename)

for i, pragma in enumerate(pragmas):
    key, iv = generate_key_and_iv(pragma, userId)
    print(f"Number {i+1}:")
    print(f"Pragma: {pragma}")
    print(f"Key: {key.hex()}")
    print(f"IV: {iv.hex()}")
    
    decDB = decrypt_database(key, iv, encDB)
    output_filename = f'chatLogs_133748894318006_pragma_dec_{i+1}.db'
    save_to_file(decDB, output_filename)
    print(f"Decrypted data saved to: {output_filename}\n")
