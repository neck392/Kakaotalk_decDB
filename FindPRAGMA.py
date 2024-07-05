def FindPragmas(filename):
    try:
        with open(filename, 'r', encoding='utf-16') as file:
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
        print(f"File {filename} not found.")
    except Exception as e:
        print(f"Error occurred: {e}")
    
    return pragmas

# Input file path
filename = '3000str.txt'
pragmas = FindPragmas(filename)
pragmas = [substring for substring in pragmas if len(substring) == 88]

for substring in pragmas:
    print(substring)
