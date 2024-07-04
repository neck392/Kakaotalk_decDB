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

def findMostCommonNumber(ntNumbers, equalNumbers, userIdNumbers):
    ntCount = Counter(ntNumbers)
    equalCount = Counter(equalNumbers)
    userIdCount = Counter(userIdNumbers)
    
    commonNumbers = ntCount & equalCount & userIdCount  
    
    combinedCount = {num: ntCount[num] + equalCount[num] + userIdCount[num] for num in commonNumbers}
    
    filteredCount = {num: count for num, count in combinedCount.items() if 5 <= len(num) <= 10}
    
    totalCount = len(ntNumbers) + len(equalNumbers) + len(userIdNumbers)
    
    if filteredCount:
        mostCommonNumber = max(filteredCount, key=filteredCount.get)
        mostCommonCount = filteredCount[mostCommonNumber]
        probability = mostCommonCount / totalCount
    else:
        mostCommonNumber = None
        mostCommonCount = 0
        probability = 0
    
    return mostCommonNumber, mostCommonCount, probability

# input file path
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

mostCommonNumber, mostCommonCount, probability = findMostCommonNumber(ntResult, equalResult, userIdResult)
print()  
print(f"Find USERID: {mostCommonNumber} (Frequency: {mostCommonCount}, Probability: {probability:.2%})")
