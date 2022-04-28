import time
import numpy as np
from matplotlib import pyplot as plt
from Lib.Driver.Instruments import VectorSpectrumAnalyser
from Lib.TestMethod import OBUE, PathLoss, TRDC
from Lib.Driver.Ericsson import RRU
from Lib.Basic import LogConfig
from Lib.Driver.Ericsson.RUMA import TCA

###############set carrier pamameter###################
obue_mask0 = ((0.015e6, -14, 0.215e6, -14, 30e3),
              (0.215e6, -14, 1.015e6, -26, 30e3),
              (1.015e6, -26, 1.500e6, -26, 30e3),
              (1.515e6, -13, 10.50e6, -13, 1e6),
              (10.50e6, -15, 20.00e6, -15, 1e6)
              )
obue_mask1 = ((0.015e6, -14, 1.500e6, -26, 30e3),
              (1.515e6, -15, 20.00e6, -15, 1e6))

carriers_setup_string = ['L4p60_753.9e6_P-3.0dB','L50tm3p1_788.5e6_P-3.0dB']

carriers_cf = [753.9e6, 788.5e6]
carriers_bw = [0.4e6,5e6]
carrier_mask = [obue_mask0,obue_mask0]
pathLoss_txa_spec = PathLoss.PathLoss(port_from='TXA', port_to='SPEC')
rbw_normalized = 10e3
resolution = 1e3
att = 20
swp_time = 0.02
ave_num = 50
margin = 10
freq_buff = 0.1e6
######################Set DRT Parameter##############################
D = range(-10,10)
A = range(-9,10)
trdc_on_time = 30

###############init test########################
LogConfig.init_logger()
testlog = LogConfig.get_logger()
tca = TCA()
Com = "COM12"
ru = RRU.DutSerial(portx = Com, bps = 115200, timex = 5)
ru.openCom()
trdc_tx = TRDC.TRDC_DL(branches =[0], rru=ru, tca=tca, carriers_setup_string=carriers_setup_string)
obue = OBUE.OBUE(norm_rbw=rbw_normalized, sampling_resolution=resolution)
freq_mask, power_mask = obue.get_abs_mask_mc(carriers_cf, carriers_bw, carrier_mask)
vsa = VectorSpectrumAnalyser.VectorSpectrumAnalyzer('TCPIP0::192.168.0.22::hislip0::INSTR', timeout=20)





#trdc_tx.del_all_carrier()
#trdc_tx.set_up_DL_carrier_init()
tca.StartPlayBack()
trdc_tx.trdc_release_all()
with open('DRT log.txt', 'w') as f:
    f.write('{:<20}{:<20}{:<20}\n'.format('D', 'A', 'Margin'))
for d in D:
    for a in A:
        vsa.send(':SYSTem:PRESet')
        trdc_tx.trdc_release_all()

        ru.sendWait('db write /trxCtrl/param/KRC161971_1/R1A/section1/xLut1  0 {} {} 0 0'.format(d, a))
        trdc_tx.send_trdc_commond()
        trdc_tx.trdc_on_all()

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
            data = vsa.get_trace().split(',')
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
            plt.show()
            '''
        with open('DRT log.txt', 'a') as f:
            f.write('{:<20}{:<20}{:<20}\n'.format(d, a, min(spur_vsa)))






