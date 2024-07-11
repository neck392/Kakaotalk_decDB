import winreg

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

pragmas = ["result of findpragmas"]
devIds = getKakaoTalkDevId()

findFinalPragma(devIds, pragmas)
