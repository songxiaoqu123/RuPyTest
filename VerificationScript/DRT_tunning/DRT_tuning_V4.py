import time
import numpy as np
from Lib.Driver.Instruments import VectorSpectrumAnalyser
from Lib.TestMethod import OBUE, PathLoss
from Lib.Driver.Ericsson import RRU
from Lib.Basic import LogConfig

###############set carrier pamameter###################
obue_mask0 = ((0.015e6, -14, 0.215e6, -14, 30e3),
              (0.215e6, -14, 1.015e6, -26, 30e3),
              (1.015e6, -26, 1.500e6, -26, 30e3),
              (1.515e6, -13, 10.50e6, -13, 1e6),
              (10.50e6, -15, 20.00e6, -15, 1e6)
              )
obue_mask1 = ((0.015e6, -14, 1.500e6, -26, 30e3),
              (1.515e6, -15, 20.00e6, -15, 1e6))

carriers_cf = [755.5e6, 788.5e6]
carriers_bw = [5e6,5e6]
carrier_mask = [obue_mask0,obue_mask0]
pathLoss_txa_spec = PathLoss.PathLoss(port_from='TXA', port_to='SPEC')
rbw_normalized = 30e3
resolution = 1e3
att = 18
swp_time = 0.001
ave_num = 100
margin = 10
freq_buff = 0.1e6
######################Set DRT Parameter##############################
D = range(-10,10)
A = range(-9,10)
trdc_on_time = 30

###############init test########################
LogConfig.init_logger()
testlog = LogConfig.get_logger()
obue = OBUE.OBUE(norm_rbw=rbw_normalized, sampling_resolution=resolution)
freq_mask, power_mask = obue.get_abs_mask_mc(carriers_cf, carriers_bw, carrier_mask)
vsa = VectorSpectrumAnalyser.VectorSpectrumAnalyzer('TCPIP0::192.168.0.22::hislip0::INSTR', timeout=10)
vsa.send(':SYSTem:PRESet')


Com = "COM12"
ru = RRU.DutSerial(portx = Com, bps = 115200, timex = 5)
ru.openCom()
with open('DRT log.txt', 'w') as f:
    f.write('{:<20}{:<20}{:<20}\n'.format('D', 'A', 'Margin'))
for d in D:
    for a in A:

        ru.sendWait('trdc release 1')
        ru.sendWait('trdc release 2')
        #ru.sendWait('trdc release 3')
        ru.sendWait('db write /trxCtrl/param/KRC161971_1/R1A/section1/xLut1  0 {} {} 0 0'.format(d, a))
        ru.sendWait('trdc setup3 1 0 1 755500 0 0 -30 5000 0 0 -30 1 0 0 7680 1 0 1 1 0 0')
        #ru.sendWait('trdc setup3 2 0 1 772000 0 0 -48 10000 0 0 -48 1 0 0 15360 1 0 1 1 2 0')
        ru.sendWait('trdc setup3 2 0 1 788500 0 0 -30 5000 0 0 -30 1 0 0 7680 1 0 1 1 2 0')
        ru.sendWait('trdc on 1')
        ru.sendWait('trdc on 2')
        #ru.sendWait('trdc on 3')
        time.sleep(trdc_on_time)
        spur_vsa = []
        for i in range(len(freq_mask)):
            # init vsa for each carrier
            start_freq = freq_mask[i][0]-freq_buff
            stop_freq = freq_mask[i][-1]+freq_buff
            num_of_points = (stop_freq - start_freq) / resolution + 1
            vsa.set_sweep_point(num_of_points)
            vsa.set_freq_start(start_freq)
            vsa.set_freq_stop(stop_freq)
            vsa.set_att(att)
            vsa.set_RBW(rbw_normalized)
            vsa.set_sweep_time(swp_time)
            vsa.set_trace_type(1)  # average mode
            vsa.set_detector_type(0)
            vsa.set_ave_num(ave_num)
            vsa.set_data_format(3)  # ASCii
            vsa.init()
            #time.sleep(3)

            ##############start test for each carrier###################
            data = vsa.query(':FETCh:SAN1?').split(',')
            freq_vsa = np.array(data[0::2], dtype=float)
            loss_txa_spec = pathLoss_txa_spec.get_path_loss(freq_vsa)
            power_vsa = np.array(data[1::2], dtype=float)
            power_vsa = power_vsa - loss_txa_spec
            index_mask = np.searchsorted(freq_vsa, freq_mask[i])

            margin_vsa = np.array(power_mask[i]) - power_vsa[index_mask]
            spur_vsa.append(min(list(margin_vsa)))
            '''
            plt.scatter(freq_mask[i], margin_vsa, color='green', marker='.', s=1)
            plt.scatter(freq_mask[i], power_mask[i], color='orange', marker='.', s=1)
            plt.scatter(freq_vsa, power_vsa, color='blue', marker='.', s=1)
            '''
        with open('DRT log.txt', 'a') as f:
            f.write('{:<20}{:<20}{:<20}\n'.format(d, a, min(spur_vsa)))






