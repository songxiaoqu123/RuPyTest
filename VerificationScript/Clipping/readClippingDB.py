import time
import numpy as np
from Lib.Driver.Ericsson import RRU
from Lib.Basic import LogConfig
from Lib.Driver import Instruments
import re

LogConfig.init_logger()
testlog = LogConfig.get_logger()


Com = "COM11"
dutSerial = RRU.DutSerial(portx = Com, bps = 115200, timex = 30)
dutSerial.openCom()

db_name =r'/716/id_ruType_1.25.x/BandI/discouragedConfigAdjust'
output_filename = 'clipping db_4417_old.txt'

db_len = 18
#db_name =r'/716/id_ruType_1.25.x/BandI/discouragedConfigAdjust'

data = dutSerial.sendWait('db list {}'.format(db_name))
data = data.split('\n')
data = data[4:-2:]
d= ' '.join(data)
d = d.replace('\r','')
d = d.replace(' ','')
d = d.replace(' ','')
d = d.split(',')
with open(output_filename, 'w') as f:
    j = 0
    for i in d:
        f.write('{:10}'.format(i))
        j = j+1
        if(j == db_len):
            f.write('\n')
            j=0

'''

    data = dutSerial.sendWait('te log read')
    f.write(data)
    dutSerial.sendWait('te log clear')
'''




dutSerial.closeCom()

