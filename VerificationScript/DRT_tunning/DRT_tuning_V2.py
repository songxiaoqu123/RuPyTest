import time
import numpy as np
from matplotlib import pyplot as plt
from Lib.Driver.Instruments import VectorSpectrumAnalyser
from Lib.TestMethod import OBUE, PathLoss

###############set pamameter###################
obue_mask0 = ((0.015e6, -14, 0.215e6, -14, 30e3),
              (0.215e6, -14, 1.015e6, -26, 30e3),
              (1.015e6, -26, 1.500e6, -26, 30e3),
              (1.515e6, -13, 10.50e6, -13, 1e6),
              (10.50e6, -15, 20.00e6, -15, 1e6)
              )
obue_mask1 = ((0.015e6, -14, 1.500e6, -26, 30e3),
              (1.515e6, -15, 20.00e6, -15, 1e6))
carriers_cf = [755.5e6,788.5e6]
carriers_bw = [5e6,5e6]
carrier_mask = [obue_mask0,obue_mask0]
pathLoss_txa_spec = PathLoss.PathLoss(port_from='TXA', port_to='SPEC')
rbw_normalized = 30e3
resolution = 1e3
att = 20
swp_time = 0.1
margin = 10

###############init test########################
obue = OBUE.OBUE(norm_rbw=rbw_normalized, sampling_resolution=resolution)
freq_mask, power_mask = obue.get_abs_carrier_mask_mc(carriers_cf, carriers_bw, carrier_mask)
vsa = VectorSpectrumAnalyser.VectorSpectrumAnalyzer('TCPIP0::192.168.0.22::hislip0::INSTR', timeout=10)
vsa.send(':SYSTem:PRESet')
spur_vsa = []
for i in range(len(freq_mask)):
    # init vsa for each carrier
    start_freq = freq_mask[i][0]
    stop_freq = freq_mask[i][-1]
    num_of_points = (stop_freq - start_freq) / resolution + 1
    vsa.set_sweep_point(num_of_points)
    vsa.set_freq_start(start_freq)
    vsa.set_freq_stop(stop_freq)
    vsa.set_att(att)
    vsa.set_RBW(rbw_normalized)
    vsa.set_sweep_time(swp_time)
    vsa.set_trace_type(1)  # average mode
    vsa.set_ave_num(10)
    vsa.set_data_format(3)  # ASCii
    vsa.init()
    time.sleep(2)
    ##############start test for each carrier###################
    data = vsa.query(':FETCh:SAN1?', delay=swp_time+2).split(',')
    freq_vsa = np.array(data[0::2], dtype=float)
    loss_txa_spec = pathLoss_txa_spec.get_path_loss(freq_vsa)
    power_vsa = np.array(data[1::2], dtype=float)
    power_vsa = power_vsa - loss_txa_spec
    index_mask = np.searchsorted(freq_vsa, freq_mask[i])

    margin_vsa = np.array(power_mask[i]) - power_vsa[index_mask]
    spur_vsa.append(min(list(margin_vsa)))

    plt.scatter(freq_mask[i], margin_vsa, color='green', marker='.', s=1)
    plt.scatter(freq_mask[i], power_mask[i], color='orange', marker='.', s=1)
    plt.scatter(freq_vsa, power_vsa, color='blue', marker='.', s=1)

print(max(spur_vsa))
plt.show()



