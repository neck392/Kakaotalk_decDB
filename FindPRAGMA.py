import chardet
import base64

def detectEncoding(filePath):
    with open(filePath, 'rb') as file:
        rawData = file.read(1024)
    result = chardet.detect(rawData)
    return result['encoding']

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

filePath = '3000str.txt'
pragmas = findPragmas(filePath)

for substring in pragmas:
    print(substring)
