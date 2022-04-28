import time
import numpy as np
from Lib.Basic import LogConfig
from Lib.Driver.Ericsson import RRU
from Lib.Driver import Instruments
from Lib.Driver.Instruments import VectorSpectrumAnalyser as VSA


LogConfig.init_logger()
testlog = LogConfig.get_logger()

cen_freq = 772e6
band_width = 5e6
vsa_addr = 'TCPIP0::192.168.0.22::hislip0::INSTR'
sem_mask = [[0.015e6, 0.215e6, -14, -14, 30e3], [0.215e6, 1.015e6, -14, -26, 30e3], [1.015e6, 1.5e6, -26, -26, 30e3]]
Com = "COM12"

vsa = VSA.VectorSpectrumAnalyzer(vsa_addr)
vsa.reset()



Com = "COM12"
dutSerial = RRU.DutSerial(portx = Com, bps = 115200, timex = 5)
dutSerial.openCom()


D_list = range(-100,100,100)
A_list = range(-100,100,100)
center_freq = 772e6
tx_bandwidth = 10e6

#vsa.set_RBW('1000')
vsa.set_data_format(3)
try:
    with open('../DPD trace.txt', 'w') as f:
        for D in D_list:
            for A in A_list:
                '''
                dutSerial.sendWait('db write /trxCtrl/param/KRC161970_2/R1A/section3/xLut4 0, {}, {}, 400, 40'.format(D, A))
                time.sleep(2)
                dutSerial.sendWait('db list /trxCtrl/param/KRC161970_2/R1A/section3/xLut4 ')
                time.sleep(1)
                dutSerial.sendWait('trdc on 1')
                time.sleep(2)
                
                if (int(pm.read_power())< 40):
                    raise Exception
                '''
                time.sleep(2)
                vsa.set_freq_center(center_freq)
                time.sleep(0.5)
                vsa.set_freq_span(tx_bandwidth)
                time.sleep(2)
                vsa.set_data_format(3)
                vsa.init()
                data = vsa.get_trace()
                data = np.array(data.split(','))
                data = data[1::2]
                data = data.astype(float)

                data = np.max(data)
                f.write('{}\t{}\t{}\n'.format(D,A,data))


                '''
                dutSerial.sendWait('trdc off 1')
                time.sleep(2)
                '''



    dutSerial.closeCom()
except:
    print('error, COM closed')
    '''
    dutSerial.sendWait('trdc off 1')
    dutSerial.closeCom()
    '''