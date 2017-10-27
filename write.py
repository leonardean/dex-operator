import DexOperator

dumdata = "DXS*NEC0000000*VA*V0/6*1\nST*001*0001\nPC1*2*5\nPC1*3*10\nG85*12234\nSE*1*0001\nDXE*1*1\n"

masterWriter = DexOperator.MasterWriter("/dev/ttyUSB0", "NEC1234567RR01L01")
result = masterWriter.write(dumdata)
print result
