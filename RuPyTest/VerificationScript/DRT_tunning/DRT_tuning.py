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
              (10.50e6, -15, 20.00e6, -15, 1e6))
obue_mask = ((0.015e6, -14, 1.500e6, -26, 30e3),
             (1.515e6, -15, 20.00e6, -15, 1e6))
carriers_cf = [770e6, 780e6]
carriers_bw = [5e6, 5e6]
pathLoss_txa_spec = PathLoss.PathLoss(folder='..\\..\\Calibration', port_from='TXA', port_to='SPEC')

###############init test########################
obue = OBUE.OBUE(obue_mask=obue_mask, sampling_resolution=0.01e6)
mask = obue.get_abs_carrier_mask_mc(carriers_cf, carriers_bw)
vsa = VectorSpectrumAnalyser.VectorSpectrumAnalyzer('TCPIP0::192.168.0.22::hislip0::INSTR', timeout=10)
vsa.send(':SYSTem:PRESet')
vsa.send(':POW:ATT 18')
vsa.send(':SWE:TIME 1 s')
vsa.send(':DETector:TRACe AVERage')
vsa.set_data_format(3)

##############start test###################


vsa.send(':SENS:FREQ:START {}'.format(carriers_cf[0] - carriers_bw[0] - 10e6))
vsa.send(':SENS:FREQ:STOP {}'.format(carriers_cf[-1] + carriers_bw[-1] + 10e6))
data = vsa.query(':FETCh:SAN1?', delay=3).split(',')

freq_vsa = np.array(data[0::2], dtype=float)
loss_txa_spec = pathLoss_txa_spec.get_path_loss(freq_vsa)
power_vsa = np.array(data[1::2], dtype=float)
power_vsa = power_vsa - loss_txa_spec
plt.plot(freq_vsa, power_vsa, color='r')

for sub_mask in mask:
    freq_mask = sub_mask[0]
    power_mask = sub_mask[1]
    rbw = sub_mask[2]
    loss_txa_spec = pathLoss_txa_spec.get_path_loss(freq_mask)
    num_of_points = len(freq_mask)
    vsa.set_sweep_point(num_of_points)
    vsa.set_RBW(rbw)
    vsa.send(':SENS:FREQ:START {}'.format(sub_mask[0][0]))
    vsa.send(':SENS:FREQ:STOP {}'.format(sub_mask[0][-1]))
    time.sleep(2)
    data = vsa.query(':FETCh:SAN1?', delay=3).split(',')
    freq_vsa = np.array(data[0::2], dtype=float)
    power_vsa = np.array(data[1::2], dtype=float)
    power_vsa = power_vsa - loss_txa_spec
    plt.plot(freq_mask, power_mask, color='g')
    plt.plot(freq_vsa, power_vsa, color='b')
    # plt.plot(freq_mask, power_mask-power_vsa, color = 'r')

plt.show()
print(1)
