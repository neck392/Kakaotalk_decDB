import chardet
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def generateKeyAndIv(pragma, userId):
    key = pragma + userId
    while len(key) < 512:
        key += key
    key = key[:512]
    keyHash = hashlib.md5(key.encode()).digest()
    iv = hashlib.md5(base64.b64encode(keyHash)).digest()
    return keyHash, iv

def detectEncoding(filePath):
    with open(filePath, 'rb') as file:
        rawData = file.read(1024)
    result = chardet.detect(rawData)
    return result['encoding']

def findPragmas(filePath):
    encoding = detectEncoding(filePath)
    pragmas = []
    
    try:
        with open(filePath, 'r', encoding=encoding) as file:
            content = file.read()
        
        searchStr = "=="
        searchLen = len(searchStr)
        prefixLen = 86

        idx = 0
        while idx < len(content):
            idx = content.find(searchStr, idx)
            if idx == -1:
                break

            startIdx = max(0, idx - prefixLen)
            endIdx = idx + searchLen
            pragmas.append(content[startIdx:endIdx].replace('\n', ''))            
            idx = endIdx

    except FileNotFoundError:
        print(f"File {filePath} not found.")
    except Exception as e:
        print(f"Error occurred: {e}")
    
    return pragmas

def decryptDatabase(key, iv, encDb):
    decDb = b''
    i = 0
    while i < len(encDb):
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decryptedData = cipher.decrypt(encDb[i:i+4096])
        decDb += decryptedData
        i += 4096
    return decDb

def readEncryptedDataFromFile(inputFilename):
    with open(inputFilename, 'rb') as f:
        encDb = f.read()
    return encDb

def saveToFile(decDb, outputFilename):
    with open(outputFilename, 'wb') as f:
        f.write(decDb)

def checkSqliteFormat(filePath):
    with open(filePath, 'rb') as f:
        header = f.read(128)
    return b'SQLite' in header

userId = "188939636"
inputFilename = 'chatLogs_133748894318006.edb'

filePath = '3000str.txt'
pragmas = findPragmas(filePath)
pragmas = [substring for substring in pragmas if len(substring) == 88]

print("Found pragmas:")
for substring in pragmas:
    print(substring)

encDb = readEncryptedDataFromFile(inputFilename)
validSqliteFiles = []

for i, pragma in enumerate(pragmas):
    key, iv = generateKeyAndIv(pragma, userId)
    
    decDb = decryptDatabase(key, iv, encDb)
    outputFilename = f'chatLogs_133748894318006_pragma_dec_{i+1}.db'
    saveToFile(decDb, outputFilename)

    print(f"Number {i+1}:")
    print(f"Pragma: {pragma}")
    print(f"Key: {key.hex()}")
    print(f"IV: {iv.hex()}")
    print(f"Saved to: {outputFilename}")

    if checkSqliteFormat(outputFilename):
        validSqliteFiles.append(outputFilename)
    else:
        with open(outputFilename, 'rb') as f:
            header = f.read(128)
        print(f"Header of {outputFilename}: {header.hex()}\n")

print("\nValid SQLite3 database files:")
for file in validSqliteFiles:
    print(file)
