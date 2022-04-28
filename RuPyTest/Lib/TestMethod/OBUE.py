import time
import numpy as np
from matplotlib import pyplot as plt
from Lib.Basic import LogConfig
from Lib.Driver import Instruments


class OBUE():
    def __init__(self,norm_rbw = 10e3, sampling_resolution=10e3):
        self.norm_rbw = norm_rbw
        self.sampling_resolution = sampling_resolution
        self.sample_mask = ((0.015e6, -14, 0.215e6, -14, 30e3),
                            (0.215e6, -14, 1.015e6, -26, 30e3),
                            (1.015e6, -26, 1.500e6, -26, 30e3),
                            (1.515e6, -13, 10.50e6, -13, 1e6),
                            (10.50e6, -15, 20.00e6, -15, 1e6))
        # (startf, start_p, stop_f,stop_p, rbw, swp_time)

    def get_rel_submask_limit(self, sub_mask):
        '''
        get frequency and power limit based on obue standard and sampling_resolution
        '''
        rbw = sub_mask[4]
        start_freq = sub_mask[0]
        start_power = sub_mask[1]-10*np.log10(rbw/self.norm_rbw)
        stop_freq = sub_mask[2]
        stop_power = sub_mask[3]-10*np.log10(rbw/self.norm_rbw)
        freq_arr = np.array([start_freq, stop_freq])
        power_arr = np.array([start_power, stop_power])
        freq = np.arange(start_freq, stop_freq, self.sampling_resolution)
        power = np.interp(freq, freq_arr, power_arr)
        freq_mirror = freq[::-1] * -1
        power_mirror = power[::-1]
        return [freq, power], [freq_mirror, power_mirror]

    def get_abs_submask(self, rel_submask, carrier_cf, carrier_bw):
        # rel_submask = [freq, power, rbw], [freq_mirror, power_mirror, rbw]
        return [rel_submask[0][0] + carrier_cf + carrier_bw / 2, rel_submask[0][1]], [
            rel_submask[-1][0] + carrier_cf - carrier_bw / 2, rel_submask[-1][1]]

    def get_abs_mask_1c(self, carrier_cf, carrier_bw, carrier_mask):
        mask_freq = []
        mask_freq_mirror = []
        mask_power = []
        mask_power_mirror = []
        for submask in carrier_mask:
            rel_sub_mask = self.get_rel_submask_limit(submask)
            abs_sub_mask = self.get_abs_submask(rel_sub_mask, carrier_cf, carrier_bw)
            mask_freq = mask_freq + list(abs_sub_mask[0][0])
            mask_freq_mirror = list(abs_sub_mask[-1][0]) + mask_freq_mirror
            mask_power = mask_power + list(abs_sub_mask[0][1])
            mask_power_mirror = list(abs_sub_mask[-1][1]) + mask_power_mirror
            mask = [mask_freq, mask_power]
            mask_mirror = [mask_freq_mirror, mask_power_mirror]
        return mask, mask_mirror

    def get_abs_carrier_mask_mc(self, carrriers_cf, carriers_bw, carrier_mask):
        # carriers MUST be listed from small to larger
        #Return mask by carrier
        index = range(len(carrriers_cf))
        mask = self.get_abs_mask_1c(carrriers_cf[0], carriers_bw[0], carrier_mask[0])[-1]
        freq = []
        power = []
        carrier_freq = mask[0]
        carrier_power = mask[1]

        for i in index[1::]:
            center = (carrriers_cf[i - 1] + carriers_bw[i - 1] / 2 + carrriers_cf[i] - carriers_bw[i] / 2) / 2
            mask_l = self.get_abs_mask_1c(carrriers_cf[i - 1], carriers_bw[i - 1], carrier_mask[i-1])[0]
            if mask_l[0][-1] <= center:
                carrier_freq = carrier_freq + mask_l[0]
                carrier_power = carrier_power + mask_l[1]
            elif (mask_l[0][0] <= center) and (mask_l[0][-1] >= center):
                sub_index = np.where(np.array(mask_l[0]) <= center)
                carrier_freq =carrier_freq + list(np.array(mask_l[0])[sub_index])
                carrier_power =carrier_power + list(np.array(mask_l[1])[sub_index])
            freq.append(carrier_freq)
            power.append(carrier_power)

            mask_r = self.get_abs_mask_1c(carrriers_cf[i], carriers_bw[i], carrier_mask[i])[-1]
            if mask_r[0][0] >= center:
                carrier_freq = mask_r[0]
                carrier_power = mask_r[1]
            elif (mask_r[0][0] <= center) and (mask_r[0][-1] >= center):
                sub_index = np.where(np.array(mask_r[0]) >= center)
                carrier_freq =list(np.array(mask_r[0])[sub_index])
                carrier_power =list(np.array(mask_r[1])[sub_index])

        mask = self.get_abs_mask_1c(carrriers_cf[-1], carriers_bw[-1], carrier_mask[-1])[0]
        carrier_freq = carrier_freq + mask[0]
        carrier_power = carrier_power + mask[1]
        freq.append(carrier_freq)
        power.append(carrier_power)
        return freq, power

    def get_abs_mask_mc(self, carrriers_cf, carriers_bw, carrier_mask):
        # carriers MUST be listed from small to larger
        #Return mask by carrier
        index = range(len(carrriers_cf))
        mask = self.get_abs_mask_1c(carrriers_cf[0], carriers_bw[0], carrier_mask[0])[-1]
        freq = []
        power = []
        freq.append(mask[0])
        power.append(mask[1])


        for i in index[1::]:
            center = (carrriers_cf[i - 1] + carriers_bw[i - 1] / 2 + carrriers_cf[i] - carriers_bw[i] / 2) / 2
            mask_l = self.get_abs_mask_1c(carrriers_cf[i - 1], carriers_bw[i - 1], carrier_mask[i-1])[0]
            if mask_l[0][-1] <= center:
                freq.append(mask_l[0])
                power.append(mask_l[1])
            elif (mask_l[0][0] <= center) and (mask_l[0][-1] >= center):
                sub_index = np.where(np.array(mask_l[0]) <= center)
                freq.append(list(np.array(mask_l[0])[sub_index]))
                power.append(list(np.array(mask_l[1])[sub_index]))

            mask_r = self.get_abs_mask_1c(carrriers_cf[i], carriers_bw[i], carrier_mask[i])[-1]
            if mask_r[0][0] >= center:
                freq.append(mask_r[0])
                power.append(mask_r[1])
            elif (mask_r[0][0] <= center) and (mask_r[0][-1] >= center):
                sub_index = np.where(np.array(mask_r[0]) >= center)
                freq.append(list(np.array(mask_r[0])[sub_index]))
                power.append(list(np.array(mask_r[1])[sub_index]))

        mask = self.get_abs_mask_1c(carrriers_cf[-1], carriers_bw[-1], carrier_mask[-1])[0]
        freq.append(mask[0])
        power.append(mask[1])
        return freq, power






    def normalize_abs_mask_rbw(self, mask, rbw):
        for i in range(len(mask)):
            mask[i][1] = mask[i][1]-10*np.log10(mask[i][2]/rbw)
            mask[i][2] = rbw
        return mask


if __name__ == '__main__':

    LogConfig.init_logger()
    testlog = LogConfig.get_logger()


    center_freq = 2140e6
    tx_bandwidth = 70e6
    obue_mask_BC1 = ((0.015e6, -14, 0.215e6, -14, 30e3),
                     (0.215e6, -14, 1.015e6, -26, 30e3),
                     (1.015e6, -26, 1.500e6, -26, 30e3),
                     (1.515e6, -13, 10.50e6, -13, 1e6))

    obue = OBUE(obue_mask=obue_mask_BC1, sampling_resolution=0.005e6)
    carriers_cf = [990e6, 1010e6]
    carriers_bw = [5e6, 5e6]
    test_mask = obue.get_mask_combined(carriers_cf, carriers_bw, 30e3)




# obue.get_mask_limit()


'''
vsa = Keysignt_N9020('TCPIP0::192.168.0.82::hislip0::INSTR')
vsa.send(':SYSTem:PRESet')
vsa.set_freq_center(center_freq)
vsa.set_freq_span(tx_bandwidth)
vsa.set_RBW(30000)
vsa.send(':POW:ATT 18')
vsa.set_sweep_point(1001)
vsa.send(':SWE:TIME 2 s')
vsa.send(':DETector:TRACe AVERage')
vsa.set_data_format(3)


time.sleep(0.5)

time.sleep(2)
data = vsa.query(':FETCh:SAN1?')
print(data)
'''
