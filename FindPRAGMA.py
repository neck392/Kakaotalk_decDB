def FindPragmas(filePath):
    try:
        with open(filePath, 'r', encoding='utf-16') as file:
            content = file.read()
        
        searchStr = "=="
        searchLen = len(searchStr)
        prefixLen = 86

        pragmas = []
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

filePath = '3000str.txt' # input file path
pragmas = FindPragmas(filePath)
pragmas = [substring for substring in pragmas if len(substring) == 88]

for substring in pragmas:
    print(substring)
