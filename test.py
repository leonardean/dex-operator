import DexOperator
from time import sleep

def readData():
    masterReader = DexOperator.MasterReader("/dev/ttyUSB0", "NEC1234567RR01L01")
    data = masterReader.read()
    return data

def main():
    gotData = False
    while not gotData:
        result = readData()
        if result != False:
            gotData = True
            fileWriter = open("/home/pi/Documents/vendingCPDataBuffer/dexRaw/dex_data.txt", "w")
            fileWriter.write(result)
            fileWriter.close()
            print result

if __name__ == '__main__':
    main()

# slaveReader = DexOperator.SlaveReader("/dev/tty.usbserial")
# data = slaveReader.read()
#
# masterWriter = DexOperator.MasterWriter("/dev/tty.usbserial", "NEC1234567RR01L01")
