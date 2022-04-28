import time
from Lib.Driver.Ericsson import RRU
from Lib.Basic import LogConfig
from Lib.Driver.Instruments import PowerSourceUnit as PSU
from Lib.Driver.Ericsson.RUMA import TCA
import numpy as np
import os


LogConfig.init_logger()
testlog = LogConfig.get_logger()

#############Test Setup##########
dut_sn = 'DY3E000001'
psu = PSU.PowerSourceUnit('GPIB0::1::INSTR')
Com = 'COM12'
num_of_port = 2
num_of_average = 10
waveform_file = r'C:\RuxTest\DLDataDrasp\main\LteWarp3p0_10G\LteWarp3p0_10G_T14.cdl3'
Tx1_freqs = [758e6]
Tx2_freqs = [783e6]
Tx_Bandwidth = 10e6

Rx_freqs = [730.5e6, 725.5e6]
Rx_Bandwidth = 5e6
rx_gain = 151.4


###############INIT TEST################
acx_size = Tx_Bandwidth/2.5e6
axc_step = Tx_Bandwidth/2.5e6 * 3.84

start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
rru = RRU.DutSerial(portx=Com, bps=115200, timex=5)
tca = TCA()
start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
log_file_name = r'{}-PIM-{}.txt'.format(dut_sn, start_time)

fail_flag = False

with open(log_file_name, 'w') as f:
    f.write('Rx_Gain = {}\n\n'.format(rx_gain))


#############Start Test##################
#########RU power on###############

tca.SetLineRate(lineRate='LR2_5')
tca.SetCpriVersion(version='VER1')
psu.set_output(state='OFF', after_delay=1)
psu.set_voltage(voltage=54)
psu.set_current(current=20)
psu.set_output(state='ON', before_delay=1, after_delay=1)
time.sleep(50)
rru.openCom()
rru.send('restart 1')
rru.closeCom()
time.sleep(90)
tca.SetLineRate(lineRate='LR9_8')
tca.SetCpriVersion(version='VER2')
time.sleep(15)
########Carrier setup############
for Tx1_freq in Tx1_freqs:
    for Tx2_freq in Tx2_freqs:
        tca.DeleteAllCarriers()
        for i in num_of_port:
            tca.TX_add_carrier(cpriPorts='1A', axc_cont=acx_size*i, carrier_id=i+1, tech='LTE', freq=axc_step, fs_hf=149, fs_bf=147,
                               fs_adr=1, Gain=0)
        for Rx_freq in Rx_freqs:
            with open(log_file_name, 'w') as f:
                f.write('TX1 = {:10} TX2 = {:10} RX{} = {:10}'.format(Tx1_freq, Tx2_freq, Rx_freq))


            tca.IQFileClearAll()
            tca.IQFileAdd(waveform_file, cpriPorts='1A')
            tca.IQFileSetCurrentByName(waveform_file, cpriPorts='1A')
            tca.StartPlayBack()


rru.openCom()
rru.sendWait('trdc setup3 1 0 1 758000 0 0 -30 10000 0 0 -30 1 0 0 15360 1 0 1 1 0 0')
rru.sendWait('trdc setup3 2 0 0 730500 0 0 0 5000 0 0 0 1 0 0 7680 1 0 11 1 0 0')
rru.sendWait('trdc setup3 3 0 1 783000 0 0 -30 10000 0 0 -30 1 0 0 15360 1 0 1 1 4 0')
rru.sendWait('trdc setup3 4 0 0 725500 0 0 0 5000 0 0 0 1 0 0 7680 1 0 11 1 2 0')
rru.sendWait('trdc setup3 5 0 1 758000 0 0 -30 10000 0 1 -30 1 0 0 15360 1 0 1 1 8 0')
rru.sendWait('trdc setup3 6 0 0 730500 0 0 0 5000 0 1 0 1 0 0 7680 1 0 11 1 4 0')
rru.sendWait('trdc setup3 7 0 1 783000 0 0 -30 10000 0 1 -30 1 0 0 15360 1 0 1 1 12 0')
rru.sendWait('trdc setup3 8 0 0 725500 0 0 0 5000 0 1 0 1 0 0 7680 1 0 11 1 6 0')
rru.sendWait('trdc on 1')
rru.sendWait('trdc on 2')
rru.sendWait('trdc on 3')
rru.sendWait('trdc on 4')
rru.sendWait('trdc on 5')
rru.sendWait('trdc on 6')
rru.sendWait('trdc on 7')
rru.sendWait('trdc on 8')
time.sleep(5)
#############Read rx power with Tx ON############

with open(log_file_name, 'a') as f:
    f.write('TX1 ON, TX2 ON\n')
    f.write('{:<20}{:<20}{:<20}{:<20}\n'.format('A_RX1', 'A_RX2', 'B_RX1', 'B_RX2'))
for i in range(10):
    rx_ipwr = rru.get_rxipwr()
    A_Rx1 = rx_ipwr[0]-rx_gain
    A_Rx2 = rx_ipwr[1]-rx_gain
    B_Rx1 = rx_ipwr[12]-rx_gain
    B_Rx2 = rx_ipwr[13]-rx_gain
    A_Rx1_Tx_11.append(A_Rx1)
    A_Rx2_Tx_11.append(A_Rx2)
    B_Rx1_Tx_11.append(B_Rx1)
    B_Rx2_Tx_11.append(B_Rx2)
    with open(log_file_name, 'a') as f:
        f.write('{:<20}{:<20}{:<20}{:<20}\n'.format(A_Rx1, A_Rx2, B_Rx1, B_Rx2))
    time.sleep(1)
A_Rx1_Tx_11_ave = np.array(A_Rx1_Tx_11).mean()
A_Rx2_Tx_11_ave = np.array(A_Rx2_Tx_11).mean()
B_Rx1_Tx_11_ave = np.array(B_Rx1_Tx_11).mean()
B_Rx2_Tx_11_ave = np.array(B_Rx2_Tx_11).mean()
with open(log_file_name, 'a') as f:
    f.write('{:<20}{:<20}{:<20}{:<20}\n'.format('A_RX1_AVE', 'A_RX2_AVE', 'B_RX1_AVE', 'B_RX2_AVE'))
    f.write('{:<20}{:<20}{:<20}{:<20}\n'.format(A_Rx1_Tx_11_ave, A_Rx2_Tx_11_ave, B_Rx1_Tx_11_ave, B_Rx2_Tx_11_ave))
    f.write('\n\n')






#############Read rx power with Tx OFF############
rru.sendWait('trdc off 1')
rru.sendWait('trdc off 3')
rru.sendWait('trdc off 5')
rru.sendWait('trdc off 7')
time.sleep(3)
with open(log_file_name, 'a') as f:
    f.write('TX1 OFF, TX2 OFF\n')
    f.write('{:<20}{:<20}{:<20}{:<20}\n'.format('A_RX1', 'A_RX2', 'B_RX1', 'B_RX2'))
for i in range(10):
    rx_ipwr = rru.get_rxipwr()
    A_Rx1 = rx_ipwr[0]-rx_gain
    A_Rx2 = rx_ipwr[1]-rx_gain
    B_Rx1 = rx_ipwr[12]-rx_gain
    B_Rx2 = rx_ipwr[13]-rx_gain
    A_Rx1_Tx_00.append(A_Rx1)
    A_Rx2_Tx_00.append(A_Rx2)
    B_Rx1_Tx_00.append(B_Rx1)
    B_Rx2_Tx_00.append(B_Rx2)
    with open(log_file_name, 'a') as f:
        f.write('{:<20}{:<20}{:<20}{:<20}\n'.format(A_Rx1, A_Rx2, B_Rx1, B_Rx2))
    time.sleep(1)
A_Rx1_Tx_00_ave = np.array(A_Rx1_Tx_00).mean()
A_Rx2_Tx_00_ave = np.array(A_Rx2_Tx_00).mean()
B_Rx1_Tx_00_ave = np.array(B_Rx1_Tx_00).mean()
B_Rx2_Tx_00_ave = np.array(B_Rx2_Tx_00).mean()
with open(log_file_name, 'a') as f:
    f.write('{:<20}{:<20}{:<20}{:<20}\n'.format('A_RX1_AVE', 'A_RX2_AVE', 'B_RX1_AVE', 'B_RX2_AVE'))
    f.write('{:<20}{:<20}{:<20}{:<20}\n'.format(A_Rx1_Tx_00_ave, A_Rx2_Tx_00_ave, B_Rx1_Tx_00_ave, B_Rx2_Tx_00_ave))
    f.write('\n\n')
if (A_Rx1_Tx_11_ave - A_Rx1_Tx_00_ave > 1):
    with open(log_file_name, 'a') as f:
        f.write('A_Rx1 FAIL\n')
if (A_Rx2_Tx_11_ave - A_Rx2_Tx_00_ave > 1):
    with open(log_file_name, 'a') as f:
        f.write('A_Rx2 FAIL\n')
if (B_Rx1_Tx_11_ave - B_Rx1_Tx_00_ave > 1):
    with open(log_file_name, 'a') as f:
        f.write('B_Rx1 FAIL\n')
if (B_Rx2_Tx_11_ave - B_Rx2_Tx_00_ave > 1):
    with open(log_file_name, 'a') as f:
        f.write('B_Rx2 FAIL\n')


##########release all###############
rru.sendWait('trdc release 1')
rru.sendWait('trdc release 2')
rru.sendWait('trdc release 3')
rru.sendWait('trdc release 4')
rru.sendWait('trdc release 5')
rru.sendWait('trdc release 6')
rru.sendWait('trdc release 7')
rru.sendWait('trdc release 8')

time.sleep(5)
rru.closeCom()

