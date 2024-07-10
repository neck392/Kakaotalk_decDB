import re
import chardet
from collections import Counter

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

def findMostCommonNumber(*numberLists):
    validLists = [Counter(numbers) for numbers in numberLists if numbers]

    if not validLists:
        return None, 0, 0
    
    commonNumbers = validLists[0]
    for count in validLists[1:]:
        commonNumbers &= count
    
    combinedCount = {num: sum(count[num] for count in validLists) for num in commonNumbers}
    
    filteredCount = {num: count for num, count in combinedCount.items() if 5 <= len(num) <= 10}
    
    totalCount = sum(len(numbers) for numbers in numberLists)
    
    if filteredCount:
        mostCommonNumber = max(filteredCount, key=filteredCount.get)
        mostCommonCount = filteredCount[mostCommonNumber]
        probability = mostCommonCount / totalCount
    else:
        mostCommonNumber = None
        mostCommonCount = 0
        probability = 0
    
    return mostCommonNumber, mostCommonCount, probability

filePath = '3000str.txt'

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

mostCommonNumber, mostCommonCount, probability = findMostCommonNumber(ntResult, equalResult, userIdResult, fromResult)
userId = mostCommonNumber
print(f"\nFind most common number: {mostCommonNumber} (Frequency: {mostCommonCount}, Probability: {probability:.2%})")
