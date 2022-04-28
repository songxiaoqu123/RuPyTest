import time
import numpy as np
from Lib.Driver.Ericsson import RRU
from Lib.Basic import LogConfig
from Lib.Driver import Instruments

LogConfig.init_logger()
testlog = LogConfig.get_logger()


Com = "COM11"
dutSerial = RRU.DutSerial(portx = Com, bps = 115200, timex = 30)
dutSerial.openCom()

try:
    with open('telog.txt', 'w') as f:
        data = dutSerial.sendWait('te log read')
        f.write(data)
        dutSerial.sendWait('te log clear')





    dutSerial.closeCom()
except:
    dutSerial.closeCom()
    print('error, COM closed')

