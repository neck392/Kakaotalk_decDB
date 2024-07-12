import winreg
import re
import chardet
import base64
import hashlib
from collections import Counter
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# ----------------------------------------------------------------------
def detectEncoding(filePath):
    with open(filePath, 'rb') as file:
        rawData = file.read(1024)
        encodingInfo = chardet.detect(rawData)
        encoding = encodingInfo['encoding']
    return encoding

def readNtNumbers(filePath, encoding):
    ntNumbers = []
    with open(filePath, 'r', encoding=encoding) as file:
        for line in file:
            ntNumbers.extend(re.findall(r'nt\s+(\d{5,10})', line))
    ntNumbers = [num for num in ntNumbers if num != '0']
    return ntNumbers

def readEqualNumbers(filePath, encoding):
    equalNumbers = []
    with open(filePath, 'r', encoding=encoding) as file:
        for line in file:
            equalNumbers.extend(re.findall(r'==(\d{5,10})', line))
    equalNumbers = [num for num in equalNumbers if num != '0']
    return equalNumbers

def readUserIdNumbers(filePath, encoding):
    userIdNumbers = []
    with open(filePath, 'r', encoding=encoding) as file:
        for line in file:
            userIdNumbers.extend(re.findall(r'"user_id":(\d{5,10})', line))
    userIdNumbers = [num for num in userIdNumbers if num != '0']
    return userIdNumbers

def readFromNumbers(filePath, encoding):
    fromNumbers = []
    with open(filePath, 'r', encoding=encoding) as file:
        for line in file:
            fromNumbers.extend(re.findall(r'"from":"(\d{5,10})"', line))
    fromNumbers = [num for num in fromNumbers if num != '0']
    return fromNumbers

def findMostCommonNumberWithWeights(totalNumbers, weights, *numberLists):
    combinedCounts = Counter()
    for key, numbers in zip(weights.keys(), numberLists):
        if numbers:
            weightedCounts = Counter({num: count * weights[key] for num, count in Counter(numbers).items()})
            combinedCounts.update(weightedCounts)

    if not combinedCounts:
        return None, 0, 0

    mostCommonNumber, weightedCount = combinedCounts.most_common(1)[0]
    totalCount = sum(Counter(totalNumbers).values())
    actualCount = Counter(totalNumbers)[mostCommonNumber]
    probability = actualCount / totalCount if totalCount else 0

    return mostCommonNumber, actualCount, probability

def findFallbackNumber(totalNumbers, weights, fromNumbers, userIdNumbers):
    fromCounter = Counter(fromNumbers)
    userIdCounter = Counter(userIdNumbers)
    commonNumbers = fromCounter & userIdCounter

    if commonNumbers:
        mostCommonNumber = commonNumbers.most_common(1)[0]
        totalCount = sum(Counter(totalNumbers).values())
        actualCount = Counter(totalNumbers)[mostCommonNumber[0]]
        probability = actualCount / totalCount if totalCount else 0
        return mostCommonNumber[0], actualCount, probability
    else:
        mostCommonNumber = fromCounter.most_common(1)[0]
        totalCount = sum(Counter(totalNumbers).values())
        actualCount = Counter(totalNumbers)[mostCommonNumber[0]]
        probability = actualCount / totalCount if totalCount else 0
        return mostCommonNumber[0], actualCount, probability

def findMostCommonInCombinedLists(totalNumbers, weights, *numberLists):
    combinedCounter = Counter()
    for numbers in numberLists:
        combinedCounter.update(Counter(numbers))
    mostCommonNumber, mostCommonCount = combinedCounter.most_common(1)[0]
    totalCount = sum(Counter(totalNumbers).values())
    actualCount = Counter(totalNumbers)[mostCommonNumber]
    probability = actualCount / totalCount if totalCount else 0
    return mostCommonNumber, actualCount, probability
# ----------------------------------------------------------------------

def generateKeyAndIv(pragma, userId):
    key = pragma + userId
    while len(key) < 512:
        key += key
    key = key[:512]
    keyHash = hashlib.md5(key.encode()).digest()
    iv = hashlib.md5(base64.b64encode(keyHash)).digest()
    return keyHash, iv

def isBase64(s):
    try:
        return base64.b64encode(base64.b64decode(s)).decode() == s
    except Exception:
        return False

def findPragmas(filePath):
    encoding = detectEncoding(filePath)
    pragmas = set() 
    try:
        with open(filePath, 'r', encoding=encoding) as file:
            content = file.read()

        searchStr = "=="
        searchLen = len(searchStr)
        pragmaLen = 88

        idx = 0
        while idx < len(content):
            idx = content.find(searchStr, idx)
            if idx == -1:
                break

            startIdx = idx - 1
            filteredPrefix = []

            while len(filteredPrefix) < (pragmaLen - searchLen) and startIdx >= 0:
                if content[startIdx] not in ['\n', ' ']:
                    filteredPrefix.insert(0, content[startIdx])
                startIdx -= 1

            filteredPrefix = ''.join(filteredPrefix)

            pragma = filteredPrefix + searchStr

            if len(pragma) == pragmaLen and isBase64(pragma):
                pragmas.add(pragma)  

            idx += searchLen

    except FileNotFoundError:
        print(f"File {filePath} not found.")
    except Exception as e:
        print(f"Error occurred: {e}")

    return list(pragmas)

def getKakaoTalkDevId():
    devIdList = []
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Kakao\KakaoTalk\DeviceInfo")
        
        i = 0
        while True:
            try:
                subkeyName = winreg.EnumKey(key, i)
                subkeyPath = f"Software\Kakao\KakaoTalk\DeviceInfo\{subkeyName}"
                
                subkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, subkeyPath)
                
                devId, regType = winreg.QueryValueEx(subkey, "dev_id")
                devIdList.append(devId.strip())
                
                winreg.CloseKey(subkey)
                i += 1
            except OSError:
                break
        
        winreg.CloseKey(key)
    except Exception as e:
        print(f"An error occurred: {e}")

    return devIdList

def findFinalPragma(devIds, pragmas):
    for pragma in pragmas:
        for devId in devIds:
            if devId in pragma:
                print(f"\nFind final pragma: {pragma}\n")
                return pragma
    print("No matching pragma found.")
    return None

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
        header = f.read(16)
    return b'SQLite format 3\x00' in header

#------------------INPUT DATA---------------------------
inputFilename = "chatListInfo.edb"
filePath = 'pid2820str.txt'
#------------------INPUT DATA---------------------------

detectedEncoding = detectEncoding(filePath)
print(f"Encoding format: {detectedEncoding}")

ntResult = readNtNumbers(filePath, detectedEncoding)
print("NT Processed result:")
print(ntResult)

equalResult = readEqualNumbers(filePath, detectedEncoding)
print("Equal Processed result:")
print(equalResult)

userIdResult = readUserIdNumbers(filePath, detectedEncoding)
print("User ID Processed result:")
print(userIdResult)

fromResult = readFromNumbers(filePath, detectedEncoding)
print("From Processed result:")
print(fromResult)

weights = {
    'from': 0.9,
    'user_id': 0.6,
    'nt': 0.15,
    'equal': 0.1
}

totalNumbers = fromResult + userIdResult + ntResult + equalResult

commonNumbers = set(fromResult) & set(userIdResult) & set(ntResult) & set(equalResult)
if commonNumbers:
    mostCommonNumber, mostCommonCount, probability = findMostCommonNumberWithWeights(totalNumbers, weights, list(commonNumbers), list(commonNumbers), list(commonNumbers), list(commonNumbers))
else:
    commonNumbers = set(fromResult) & set(userIdResult)
    if commonNumbers:
        mostCommonNumber, mostCommonCount, probability = findMostCommonNumberWithWeights(totalNumbers, weights, list(commonNumbers), list(commonNumbers))
    else:
        if fromResult:
            mostCommonNumber, mostCommonCount, probability = findMostCommonNumberWithWeights(totalNumbers, weights, fromResult, [], [], [])
        else:
            commonNumbers = set(ntResult) & set(equalResult) & set(userIdResult)
            if commonNumbers:
                mostCommonNumber, mostCommonCount, probability = findMostCommonNumberWithWeights(totalNumbers, weights, [], list(commonNumbers), list(commonNumbers), list(commonNumbers))
            else:
                commonNumbers = set(userIdResult) & set(ntResult)
                if commonNumbers:
                    mostCommonNumber, mostCommonCount, probability = findMostCommonNumberWithWeights(totalNumbers, weights, [], list(commonNumbers), list(commonNumbers), [])
                else:
                    commonNumbers = set(userIdResult) & set(equalResult)
                    if commonNumbers:
                        mostCommonNumber, mostCommonCount, probability = findMostCommonNumberWithWeights(totalNumbers, weights, [], list(commonNumbers), [], list(commonNumbers))
                    else:
                        if userIdResult:
                            mostCommonNumber, mostCommonCount, probability = findMostCommonNumberWithWeights(totalNumbers, weights, [], userIdResult, [], [])
                        else:
                            if ntResult:
                                mostCommonNumber, mostCommonCount, probability = findMostCommonNumberWithWeights(totalNumbers, weights, [], [], ntResult, [])
                            else:
                                if equalResult:
                                    mostCommonNumber, mostCommonCount, probability = findMostCommonNumberWithWeights(totalNumbers, weights, [], [], [], equalResult)
                                else:
                                    mostCommonNumber, mostCommonCount, probability = findMostCommonNumberWithWeights(totalNumbers, weights, fromResult, userIdResult, ntResult, equalResult)

userId = mostCommonNumber

print(f"\nFind UserId: {mostCommonNumber} (Frequency: {mostCommonCount}, Probability: {probability:.2%})")

pragmas = findPragmas(filePath)
print("\nFound pragmas:")
for substring in pragmas:
    print(substring)
print()

devIds = getKakaoTalkDevId()
findFinalPragma(devIds, pragmas)

encDb = readEncryptedDataFromFile(inputFilename)
validSqliteFiles = []

for i, pragma in enumerate(pragmas):
    key, iv = generateKeyAndIv(pragma, userId)
    
    decDb = decryptDatabase(key, iv, encDb)
    outputFilename = f'{inputFilename}_dec_{i+1}.db'
    saveToFile(decDb, outputFilename)

    if checkSqliteFormat(outputFilename):
        validSqliteFiles.append(outputFilename)
        print(f"Number {i+1}:")
        print(f"Pragma: {pragma}")
        print(f"Key: {key.hex()}")
        print(f"IV: {iv.hex()}")
        print(f"Saved to: {outputFilename}\n")
    else:
        with open(outputFilename, 'rb') as f:
            header = f.read(16)
        print(f"Number {i+1}:")
        print(f"Pragma: {pragma}")
        print(f"Key: {key.hex()}")
        print(f"IV: {iv.hex()}")
        print(f"Saved to: {outputFilename}")
        print(f"Header of {outputFilename}: {header.hex()}\n")

print("\nValid SQLite3 database files:")
for file in validSqliteFiles:
    print(file)
