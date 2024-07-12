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

filePath = 'pid2820str.txt'  # input filepath

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
