import time
from Lib.Basic import LogConfig
from Lib.Driver.Ericsson import RRU
from Lib.Driver import Instruments
from Lib.Driver.Instruments.SignalGenerator import Keysignt_E4438C
LogConfig.init_logger()
testlog = LogConfig.get_logger()
from Lib.Driver.SwitchBox import HRSM
from Lib.Driver.ComComponent import Serial485

########Tset Setup######################################################
dut_com = ['COM11', 'COM12']
port = ['A', 'B']

UL_pathloss = 30
DL_pathloss = 30
output_path = 'Logs\\'
totall_cycle = 1500
heat_time = 1200
heat_fan_speed = 0
cool_time = 1100
cool_fan_speed = 100
sample_period = 0.1



tx_norm = 46
tx_freq = 772e6
tx_pathloss = [-31.47, -31.26, -31.48, -31.31]

rx_norm = -60
rx_gain_norm = 151.4
rx_freq = 717e6
rx_pathloss = [-31.69, -31.47, -31.66, -31.49]

rx_pwr_index = [0, 12, 0, 12]

trdc_command = ['trdc setup3 1 0 1 772000 0 0 -0 5000 0 0 -0 1 0 0 7680 1 0 1 1 0 0',
                'trdc setup3 2 0 0 717000 0 0 0 5000 0 0 0 1 0 0 7680 1 0 11 1 0 0',
                'trdc setup3 3 0 1 772000 0 0 -0 5000 0 1 -0 1 0 0 7680 1 0 1 1 2 0',
                'trdc setup3 4 0 0 717000 0 0 0 5000 0 1 0 1 0 0 7680 1 0 11 1 2 0']

sg = Keysignt_E4438C('TCPIP0::192.168.0.63::inst0::INSTR')
#pm = Instruments.load_instrument('PM')
pm = Instruments.PowerMeter('USB0::0x0AAD::0x00E2::107227::INSTR')

##########Init Test######################################################
dut_index = range(len(dut_com))
port_index = range(len(port))
switch_matrix = HRSM.HRSM()
ser485 = Serial485.Serial485()

starttime = time.strftime("%Y%m%d%H%M%S", time.localtime())
state = 'Cooling'
sample = 0
outputfile = []
dut = []
for i in dut_index:
    dut.append(RRU.DutSerial(portx=dut_com[i], bps=115200, timex=5))
    for j in port_index:
        outputfile.append('{}DUT{}-PORT{}-{}.txt'.format(output_path, i, port[j], starttime))

        with open(outputfile[i*len(port)+j], 'w') as f:
            f.write(starttime)
            dut[i].openCom()
            f.write(dut[i].sendWait('par get'))
            f.write('\n')
            f.write('{:20}{:20}{:20}{:20}{:20}{:20}{:20}{:20}{:20}{:30}'.format('Sample', 'Cycle', 'State', 'Tx-norm', 'TxPower', 'TxDeltaPower', 'Rx-norm', 'RxPower', 'RxDeltaPower', 'StartTime'))

            ts_data = dut[i].get_ts()
            for d in ts_data[0::2]:
                d = 'ts-{}(C)'.format(d)
                f.write('{:20}'.format(d))
            vs_data = dut[i].get_vs()
            for d in vs_data[0::2]:
                d = 'vs-{}(V)'.format(d)
                f.write('{:20}'.format(d))
            cs_data = dut[i].get_cs()
            for d in cs_data[0::2]:
                d = 'cs-{}(A)'.format(d)
                f.write('{:20}'.format(d))
            rvc_data = dut[i].get_rvc()
            for d in rvc_data[0::2]:
                d = 'rvc-{}'.format(d)
                f.write('{:30}'.format(d))
            txpower_data = dut[i].get_trxpower(port=port_index[j])
            for d in txpower_data[0:-2:2]:
                d = 'TxPower-{}'.format(d)
                f.write('{:40}'.format(d))
            dut[i].closeCom()

            f.write('{:30}'.format('dpd restart count'))
            f.write('{:40}'.format('fm_fault'))
            f.write('\n')

#########StartTest###################################################
while True:
    try:
        for cycle in range(totall_cycle):
            cycle_start_time = time.time()

            while(time.time()-cycle_start_time < heat_time + cool_time):


                if (time.time()-cycle_start_time < heat_time) & (state == 'Cooling'):
                    state = 'Heating'
                    for i in dut_index:
                        ser485.set_electric_relay(11, 0, 1)
                        time.sleep(0.5)
                        ser485.set_electric_relay(11, 1, 1)
                        time.sleep(0.5)
                        ser485.set_fan_js48_speed(i, heat_fan_speed)
                        dut[i].openCom()
                        for j in range(2*len(port)):
                            dut[i].sendWait(trdc_command[j])
                            dut[i].sendWait('trdc on {}'.format(j+1))
                        dut[i].closeCom()
                    time.sleep(5)

                if (time.time()-cycle_start_time > heat_time) & (state == 'Heating'):
                    state = 'Cooling'
                    for i in dut_index:
                        ser485.set_fan_js48_speed(i, cool_fan_speed)
                        time.sleep(0.5)
                        ser485.set_electric_relay(11, 0, 0)
                        time.sleep(0.5)
                        ser485.set_electric_relay(11, 1, 0)
                        dut[i].openCom()
                        for j in range(2 * len(port)):
                            dut[i].sendWait('trdc release {}'.format(j+1))

                        dut[i].closeCom()
                    time.sleep(5)

                for i in dut_index:
                    for j in port_index:
                        test_index = i*len(port)+j
                        switch_matrix.set_path(switch_matrix.path1[test_index])
                        time.sleep(5)
                        #tx_power = 46.0
                        tx_power = pm.read_power() - tx_pathloss[test_index]

                        switch_matrix.set_path(switch_matrix.path2[test_index])

                        sg.set_freq(rx_freq)
                        sg.set_amp(rx_norm - rx_pathloss[test_index])
                        sg.set_rf_state('ON')
                        time.sleep(0.5)
                        dut[i].openCom()
                        rx_power = dut[i].get_rxipwr()

                        rx_power = rx_power[rx_pwr_index[test_index]]

                        rx_power = rx_power - rx_gain_norm
                        with open(outputfile[test_index], 'a') as f:
                            f.write('\n')
                            test_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                            f.write('{: <20d}{: <20d}{:20}{: <20f}{: <20f}{: <20f}{: <20f}{: <20f}{: <20f}{:30}'.format(sample, cycle, state, tx_norm, tx_power, tx_power-tx_norm, rx_norm, rx_power, rx_power-rx_norm, test_time))


                            ts_data = dut[i].get_ts()
                            for d in ts_data[1::2]:
                                d = d[:-1]
                                d = '{}'.format(d)
                                f.write('{:20}'.format(d))
                            vs_data = dut[i].get_vs()
                            for d in vs_data[1::2]:
                                d = d[:-1]
                                d = '{}'.format(d)
                                f.write('{:20}'.format(d))
                            cs_data = dut[i].get_cs()
                            for d in cs_data[1::2]:
                                d = d[:-1]
                                d = '{}'.format(d)
                                f.write('{:20}'.format(d))
                            rvc_data = dut[i].get_rvc()
                            for d in rvc_data[1::2]:
                                d = '{}'.format(d)
                                f.write('{:30}'.format(d))
                            txpower_data = dut[i].get_trxpower(port=port_index[j])
                            for d in txpower_data[1:-1:2]:
                                d = d.strip(',')
                                d = '{}'.format(d)
                                f.write('{:40}'.format(d))

                            restart_count = dut[i].get_dpdRestartCount(port=port_index[j])
                            f.write('{:30}'.format(restart_count))
                            fm_fault = dut[i].get_fmfault()
                            f.write('{:40}'.format(fm_fault))

                            dut[i].closeCom()


                            sg.set_rf_state('OFF')

                sample = sample+1
                time.sleep(sample_period)

    except:
        ser485.set_electric_relay(11, 0, 0)
        ser485.set_electric_relay(11, 1, 0)
        for i in dut_index:
            dut[i].openCom()
            for j in range(2 * len(port)):
                dut[i].sendWait('trdc release {}'.format(j + 1))
            dut[i].closeCom()
        ser485.set_fan_js48_speed(255, 100)
        time.sleep(1200)

