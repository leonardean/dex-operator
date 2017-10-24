import dexcrc16
import serial
from time import sleep

SOH = chr(0x01)
STX = chr(0x02)
ETX = chr(0x03)
EOT = chr(0x04)
DLE = chr(0x10)
ENQ = chr(0x05)
NAK = chr(0x15)
ETB = chr(0x17)
ACK0 = '0'
ACK1 = '1'
BLOCK_SIZE = 245

def printReceivedData(data):
    print "Received data:",data,"=",data.encode('hex')

def chunkstring(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))

class MasterReader:
    def __init__(self, serialPath, communicationID):
        self.serialPath = serialPath
        self.communicationID = communicationID
        print "opening connection to " + self.serialPath
        self.ser = serial.Serial(self.serialPath, 9600, timeout=0.01)

    def read(self):
        handshaker = Handshaker(self.ser, self.communicationID)
        dataExchanger = DataExchanger(self.ser)
        handshaker.firstHandshakeDCMaster("READ")
        sleep(0.1)
        handshaker.secondHandshakeVMDMaster()
        sleep(0.1)
        return dataExchanger.VMD2DCExchange()

# class SlaveReader:

class MasterWriter:
    def __init__(self, serialPath, communicationID):
        self.serialPath = serialPath
        self.communicationID = communicationID
        print "opening connection to " + self.serialPath
        self.ser = serial.Serial(self.serialPath, 9600, timeout=0.01)

    def write(self, content):
        handshaker = Handshaker(self.ser, self.communicationID)
        dataExchanger = dataExchanger(self.ser)
        handshaker.firstHandshakeDCMaster("SEND")
        sleep(0.1)
        handshaker.secondHandshakeVMDMaster()
        sleep(0.1)
        dataExchanger.DC2VMDExchange(content)

class Handshaker:
    def __init__(self, ser, communicationID):
        self.ser = ser
        self.communicationID = communicationID

    def firstHandshakeDCMaster(self, operation):
        print "Entering First Handshake DC as Master"
        state = 0
        retries = 5
        self.ser.flushInput()
        self.ser.write(ENQ)
        self.ser.flush()
        while retries > 0:
            x = self.ser.read()
            printReceivedData(x)
            if len(x) > 0:
                printReceivedData(x)
                retries = 5
                if state == 0:
                    print "State 0: Expecting DLE"
                    if x == DLE:
                        print "Got DLE"
                        state = 1
                    if x == ENQ:
                        print "Got ENQ. TODO: slave handshake"
                        # start slaveHandshake
                    else:
                        print "Got something else. Sending ENQ to restart master handshake"
                        sleep(0.01)
                        self.ser.write(ENQ)
                        self.ser.flush()
                elif state == 1:
                    print "State 1: Expecting '0'"
                    if x == '0':
                        print "Got second half of DLE"
                        print "Sending DLE"
                        sleep(0.01)
                        self.ser.write(DLE)
                        print "Sending SOH"
                        self.ser.write(SOH)
                        print "Sending communication ID"
                        for char in self.communicationID:
                            self.ser.write(char)
                        print "Sending Operation Request"
                        if operation == "READ":
                            self.ser.write("R")
                        elif operation == "SEND":
                            self.ser.write("S")
                        print "Sending DLE"
                        self.ser.write(DLE)
                        print "Sending ETX"
                        self.ser.write(ETX)
                        print "Sending CRC"
                        crc = dexcrc16.crcStr(self.communicationID + ETX)
                        self.ser.write(chr(crc & 0xFF))
                        self.ser.write(chr(crc >> 8))
                        self.flush()
                        state = 2
                    else:
                        print "Something Wrong. Sending ENQ to restart master handshake"
                        sleep(0.01)
                        self.ser.write(ENQ)
                        self.ser.flush()
                        state = 0
                elif state == 2:
                    print "State 2: Expecting DLE"
                    if x == DLE:
                        print "Got DLE"
                        state = 3
                    else:
                        print "Got something other than DLE. Bad"
                        return False
                elif state == 3:
                    print "State 3: Expecting '1' or '0'"
                    if x == '1' or x == '0':
                        print "Got second half of DLE. Sending EOT"
                        sleep(0.01)
                        self.ser.write(EOT)
                        self.ser.flush()
                        print "First Handshake DC as Master completed"
                        return True
                    else:
                        print "Got something wrong. Sending NAK"
                        sleep(0.01)
                        self.ser.write(NAK)
                        self.ser.flush()
                        state = 0
            else:
                retries = retries - 1
                sleep(0.01)
                print "trying again"
        print "First Handshake DC as Master gave up"
        return False

    def secondHandshakeVMDMaster(self):
        print "Entering Second Handshake VMD as Master"
        self.ser.flushInput()
        state = 0
        retries = 5
        receivedData = ""
        while retries > 0:
            x = self.ser.read()
            if len(x) > 0:
                printReceivedData(x)
                retries = 5
                if state == 0:
                    print "State 0: Waiting for Command"
                    if x == ENQ:
                        print "Got ENQ. Replying with DLE '0'"
                        sleep(0.01)
                        self.ser.write(DLE)
                        self.ser.write('0')
                        self.flush()
                    elif x == EOT:
                        print "Second Handshake VMD as Master Completed"
                        return True
                    elif x == DLE:
                        print "Got DLE. Receiving data now"
                        state = 1
                elif state == 1:
                    print "State 1: Expecting SOH"
                    if x == SOH:
                        print "Got SOH"
                        receivedData = ""
                        state = 2
                elif state == 2:
                    print "State 2: Receiving data"
                    if x == DLE:
                        print "Got DLE. End of Data"
                        state = 3
                    else:
                        receivedData += x
                elif state == 3:
                    print "State 3: Expecting ETX"
                    if x == ETX:
                        print "Got ETX"
                        receivedData += x
                        state = 4
                    else:
                        print "Got Something else. Resetting"
                        state = 0
                elif state == 4:
                    print "State 4: Receiving first CRC byte"
                    receivedData += x
                    state = 5
                elif state == 5:
                    print "State 5: Receiving second CRC byte"
                    receivedData += x
                    crc = dexcrc16.crcStr(receivedData)
                    print "Calculated crc=",crc
                    if crc == 0:
                        print "CRC is good. Sending DLE,1"
                        sleep(0.01)
                        self.ser.write(DLE)
                        self.ser.write('1')
                        self.ser.flush()
                    else:
                        print "CRC failed. Sending NAK"
                        self.ser.write(NAK)
                        self.ser.flush()
                    state = 0
            else:
                retries = retries - 1
                sleep(0.01)
                print "trying again"
        print "Second Handshake VMD as Master Gave up"
        return False

class DataExchanger:
    def __init__(self, ser):
        self.ser = ser
        self.content = ""

    def VMD2DCExchange(self):
        print "Exchanging data VMD to DC"
        receivedData = ""
        block = ""
        state = 0
        retries = 5
        currentAck = ACK0
        self.ser.flushInput()

        while retries > 0:
            x = self.ser.read()
            printReceivedData(x)
            if len(x) > 0:
                retries = 5
                if state == 0:
                    print "State 0: Expecting ENQ"
                    if x == ENQ:
                        print "Got ENQ. Replying ACK"
                        sleep(0.01)
                        self.ser.write(DLE)
                        self.ser.write(currentAck)
                        self.ser.flush()
                        if currentAck == ACK0:
                            currentAck = ACK1
                        elif currentAck == ACK1:
                            currentAck = ACK0
                    elif x == DLE:
                        print "Got DLE. Start of block"
                        state = 1
                elif state == 1:
                    print "State 1: Expecting STX"
                    if x == STX:
                        print "Got STX. Start block receiving"
                        state = 2
                        receivedData = ""
                        block = ""
                elif state == 2:
                    print "State 2: Receiving data block"
                    if x == DLE:
                        print "Got DLE. end of data"
                        state = 3
                    else:
                        receivedData += x
                        block += x
                elif state == 3:
                    print "State 3: waiting for end of block"
                    if x == ETB:
                        print "Got ETB, end of current block"
                        receivedData += x
                        state = 4
                    elif x == ETX:
                        print "Got ETX, end of last block"
                        receivedData += x
                        state = 6
                    else:
                        print "Got something other than end of block"
                        self.ser.write(NAK)
                        state = 0
                elif state == 4:
                    print "State 4 - Waiting for first half of CRC"
                    receivedData += x
                    state = 5
                elif state == 5:
                    print "State 5 - Waiting for second half of CRC"
                    receivedData += x
                    crc = dexcrc16.crcStr(receivedData)
                    print "Got all data, crc=",crc
                    if crc == 0:
                        print "CRC is good"
                        self.content += block
                        sleep(0.01)
                        self.ser.write(DLE)
                        self.ser.write(currentAck)
                        self.ser.flush()
                        if currentAck == ACK0:
                            currentAck = ACK1
                        elif currentAck == ACK1:
                            currentAck = ACK0
                        state = 0
                    else:
                        print "CRC failed"
                        sleep(0.01)
                        self.ser.write(NAK)
                        self.ser.flush()
                        state = 0
                elif state == 6:
                    print "State 6 - Waiting for first half of CRC"
                    receivedData += x
                    state = 7
                elif state == 7:
                    print "State 7 - Waiting for second half of CRC"
                    receivedData += x
                    crc = dexcrc16.crcStr(receivedData)
                    print "Got all data, crc=",crc
                    if crc == 0:
                        print "CRC is good"
                        self.content += block
                        self.ser.write(DLE)
                        self.ser.write(currentAck)
                        state = 8
                        self.ser.flush()
                        if currentAck == ACK0:
                            currentAck = ACK1
                        elif currentAck == ACK1:
                            currentAck = ACK0
                    else:
                        print "CRC failed"
                        self.ser.write(NAK)
                        state = 0
                elif state == 8:
                    print "State 8 - waiting for EOT"
                    if x == EOT:
                        print "Got EOT, End of data exchange"
                        return self.content
                    else:
                        print "Got something else."
                        sleep(0.01)
                        self.ser.write(NAK)
                        self.ser.flush()
                        state = 0
            else:
                retries = retries - 1
                sleep(0.01)
                print "trying again"
        print "Exchanging data VMD to DC Gave Up"
        return False

    def DC2VMDExchange(self, content):
        print "Exchanging data DC to VMD"
        blocks = chunkstring(content, BLOCK_SIZE)
        blockIterator = -0
        state = 0
        retries = 5
        self.ser.flushInput()
        self.ser.write(ENQ)
        self.ser.flush()
        while retries > 0:
            x = self.ser.read()
            if len(x) > 0:
                printReceivedData(x)
                retries = 5
                if state == 0:
                    print "State 0: Expecting DLE"
                    if x == DLE:
                        print "Got DLE"
                        state = 1
                    else:
                        print "Got something else. Sending ENQ to restart data exchange"
                        sleep(0.01)
                        self.ser.write(ENQ)
                        self.ser.flush()
                elif state == 1:
                    print "State 1: Expecting second half of DLE"
                    if x == '0' or x == '1':
                        if blockIterator == len(blocks) - 1:
                            print "Reached end of content"
                            sleep(0.01)
                            self.ser.write(EOT)
                            self.ser.flush()
                            print "Data exchange DC to VMD completed"
                            return True
                        else:
                            print "Got second half of DLE. Sending next block"
                            blockIterator += 1
                    else:
                        print "Got something else. Resending block"
                    sleep(0.01)
                    self.ser.write(DLE)
                    self.ser.write(STX)
                    self.ser.write(blocks[blockIterator])
                    if blockIterator < (len(blocks) - 1):
                        state == 2
                    elif blockIterator == (len(blocks) - 1):
                        state == 3
                elif state == 2:
                    print "State 2: Sending block end"
                    self.ser.write(DLE)
                    self.ser.write(ETB)
                    crc = dexcrc16.crcStr(self.communicationID + ETB)
                    self.ser.write(chr(crc & 0xFF))
                    self.ser.write(chr(crc >> 8))
                    self.flush()
                    state = 0
                elif state == 3:
                    print "State 3: Sending content end"
                    self.ser.write(DLE)
                    self.ser.write(ETX)
                    crc = dexcrc16.crcStr(self.communicationID + ETX)
                    self.ser.write(chr(crc & 0xFF))
                    self.ser.write(chr(crc >> 8))
                    self.flush()
                    state = 0
            else:
                retries = retries - 1
                sleep(0.01)
                print "tring again"
        print "Exchanging data DC to VMD Gave Up"
        return False
