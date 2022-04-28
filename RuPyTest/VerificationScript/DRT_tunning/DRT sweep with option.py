import time
import numpy as np
from Lib.Basic import LogConfig
from Lib.Driver.Ericsson import RRU
from Lib.Driver import Instruments
from Lib.Driver.Instruments import VectorSpectrumAnalyser as VSA

LogConfig.init_logger()
testlog = LogConfig.get_logger()

########TEST CONFIG#################
cen_freq = 772e6
band_width = 5e6
vsa_addr = 'TCPIP0::192.168.0.22::hislip0::INSTR'
sem_mask = [[0.015e6, 0.215e6, -14, -14, 30e3], [0.215e6, 1.015e6, -14, -26, 30e3], [1.015e6, 1.5e6, -26, -26, 30e3]]
Com = "COM12"
##########TEST INIT##################
vsa = VSA.VectorSpectrumAnalyzer(vsa_addr)
vsa.reset()
vsa.set_mode(23, 7)
vsa.set_sem_mask(sem_mask)


'''
rru = RRU.DutSerial(portx = Com, bps = 115200, timex = 5)
rru.openCom()
rru.sendWait("trdc release 1")
rru.trdc_single_carrier(id=1, F_id=1, type=0, direction=1, freq=2140e6, par5=0, par6=0, backoff=-7.8, par8=0,par9=1,branch=0, par12=0,par13=1,par14=0, par15=1, par16=1,axc_add1=0, axc_add2=0,AXC_size_id=4, par20=0)
rru.sendWait("trdc on 1")
'''
'''
Com = "COM11"
dutSerial = RRU.DutSerial(portx = Com, bps = 115200, timex = 5)
dutSerial.openCom()


D_list = range(-8,9)
A_list = range(-8,9)
center_freq = 2.14e9
tx_bandwidth = 5e6

#vsa.set_RBW('1000')
vsa.set_data_format(3)
try:
    with open('DPD trace.txt', 'w') as f:
        for D in D_list:
            for A in A_list:

                dutSerial.sendWait('db write /trxCtrl/param/KRC161970_2/R1A/section3/xLut4 0, {}, {}, 400, 40'.format(D, A))
                time.sleep(2)
                dutSerial.sendWait('db list /trxCtrl/param/KRC161970_2/R1A/section3/xLut4 ')
                time.sleep(1)
                dutSerial.sendWait('trdc on 1')
                time.sleep(2)
                if (int(pm.read_power())< 40):
                    raise Exception
                time.sleep(2)
                vsa.set_freq_center(center_freq + tx_bandwidth + 1e6)
                time.sleep(0.5)
                vsa.set_freq_span(tx_bandwidth)
                time.sleep(2)
                data = vsa.get_trace()
                data = np.array(data.split(','))
                data = data[1::2]
                data = data.astype(float)

                data = np.max(data)
                f.write('{}\t{}\t{}\n'.format(D,A,data))



                dutSerial.sendWait('trdc off 1')
                time.sleep(2)




    dutSerial.closeCom()
except:
    print('error, COM closed')
    dutSerial.sendWait('trdc off 1')
    dutSerial.closeCom()
'''
