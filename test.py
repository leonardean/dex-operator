import DexOperator

masterReader = DexOperator.MasterReader("/dev/ttyUSB0", "NEC1234567RR01L01")
data = masterReader.read()
print data

# slaveReader = DexOperator.SlaveReader("/dev/tty.usbserial")
# data = slaveReader.read()
#
# masterWriter = DexOperator.MasterWriter("/dev/tty.usbserial", "NEC1234567RR01L01")
