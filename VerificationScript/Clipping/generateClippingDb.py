import time
import numpy as np
from Lib.Driver.Ericsson import RRU
from Lib.Basic import LogConfig
from Lib.Driver import Instruments
import re

input_filename = 'clipping db_updated4417.txt'
output_filename = 'write clipping db.txt'
db_name = '/716/id_ruType_1.25.x/BandI/discouragedConfigAdjust'
WriteToUnit = True
Com = "COM12"
db_name =r'/716/id_ruType_1.25.x/BandI/discouragedConfigAdjust'


with open(input_filename, 'r') as f:
    data = f.readlines()
    data = ' '.join(data)
    data = data.replace('\n', '')
    for i in range(30):
        data = data.replace('  ', ' ')
    d = data.split(' ')
    size = len(d) -1

with open(output_filename, 'w') as f:
    f.write('db add {} -t S16 0\n'.format(db_name))
    f.write('db prod copy {}\n'.format(db_name))
    f.write('db resize {} {}\n'.format(db_name, size))
    f.write('db write {} {}\n'.format(db_name, data))
    f.write('db prod save')


if WriteToUnit:
    LogConfig.init_logger()
    testlog = LogConfig.get_logger()
    dutSerial = RRU.DutSerial(portx=Com, bps=115200, timex=30)
    dutSerial.openCom()
    dutSerial.sendWait('db add {} -t S16 0\n'.format(db_name))
    dutSerial.sendWait('db prod copy {}'.format(db_name))
    dutSerial.sendWait('db resize {} {}'.format(db_name, size))
    dutSerial.sendWait('db write {} {}'.format(db_name, data))
    dutSerial.closeCom()
