import DexOperator

masterReader = DexOperator.MasterReader("/dev/tty.usbserial", "NEC1234567RR01L01")
data = masterReader.read()

slaveReader = DexOperator.SlaveReader("/dev/tty.usbserial")
data = slaveReader.read()

masterWriter = DexOperator.MasterWriter("/dev/tty.usbserial", "NEC1234567RR01L01")
