def crcChar(crc, data):
    data = ord(data)
    DATA_0 = 0
    BCC_0 = 0
    BCC_1 = 0
    BCC_14 = 0
    X2 = 0
    X15 = 0
    X16 = 0
    BCC = crc
    for j in range(0,8):
        DATA_0 = (data >> j) & 0x0001
        BCC_0  = (BCC) & 0x0001
        BCC_1  = (BCC >>  1) & 0x0001
        BCC_14 = (BCC >> 14) & 0x0001     
        X16 = (BCC_0  ^ DATA_0) & 0x0001
        X15 = (BCC_1  ^ X16) & 0x0001
        X2  = (BCC_14 ^ X16) & 0x0001     
        BCC = BCC >> 1
        BCC = BCC & 0x5FFE
        BCC = BCC | X15
        BCC = BCC | (X2  << 13)
        BCC = BCC | (X16 << 15)
    return BCC
    
def crcStr(str):
    crc = 0
    for char in str:
        crc = crcChar(crc, char)
    return crc
    
def crcCheck(str):
    crc = crcStr(str)
    high = crc >> 8
    low = crc & 0xFF
    diff = crcStr(str + chr(low) + chr(high))
    return diff
   