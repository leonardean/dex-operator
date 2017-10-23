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

@staticmethod
def printReceivedData(data):
    print "Received data:",data,"=",data.encode('hex')

class MasterReader:
    def __init__(self, serialPath, communicationID):
        self.serialPath = serialPath
        self.communicationID = communicationID
        self.content = ""
        print "opening connection to " + self.serialPath
        self.ser = serial.Serial(self.serialPath, 9600, timeout=0.01)

    def read(self):
        handshaker = Handshaker()
        handshaker.masterHandshake("READ")
        sleep(0.1)
        handshaker.slaveHandshake("READ")
        sleep(0.1)

class SlaveReader:

class MasterWriter:
    def __init__(self, serialPath, communicationID):
        self.serialPath = serialPath
        self.communicationID = communicationID
        self.ser = None

    def write(self, content):

class Handshaker:
    def firstHandshakeDCMaster(self, operation):
        print "Entering First Handshake DC as Master"
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
                    if x == ENQ:
                        print "Got ENQ"
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
