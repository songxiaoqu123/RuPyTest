import time
from Lib.Driver.Ericsson import RRU
from Lib.Basic import LogConfig
from Lib.Driver.Instruments import PowerSourceUnit as PSU
from Lib.Driver.Ericsson.RUMA import TCA
import numpy as np
import os
import tkinter as tk
from ctypes import *


LogConfig.init_logger()
testlog = LogConfig.get_logger()
user32 = windll.LoadLibrary('user32.dll')

def pim_test(dut_sn):
    #############Test Setup##########
    psu = PSU.PowerSourceUnit('GPIB0::1::INSTR')
    Com = 'COM12'
    waveform_file = r'C:\RuxTest\DLDataDrasp\main\LteWarp3p0_10G\LteWarp3p0_10G_T14.cdl3'
    Tx1_freq = 758e6
    Tx2_freq = 783e6
    Rx1_freq = 730.5e6
    Rx2_freq = 725.5e6
    #dut_sn = 'DY3E000001'
    rx_gain = 151.4

    repeat_times = 5
    delay_per_sample = 0.2
    ###############INIT TEST################
    rru = RRU.DutSerial(portx=Com, bps=115200, timex=5)
    tca = TCA()

    start_time = time.strftime("%Y-%m-%d %H%M%S", time.localtime())
    log_file_name = r'{}-{}.txt'.format(dut_sn, start_time)
    with open(log_file_name, 'w') as f:
        f.write('{}\n'.format(start_time))
        f.write('TX1 = {:10} TX1 = {:10} RX1 = {:10} RX2 = {:10}\n'.format(Tx1_freq, Tx2_freq, Rx1_freq, Rx2_freq))
        f.write('Rx_Gain = {}\n\n'.format(rx_gain))
    A_Rx1_Tx_11 = []
    A_Rx1_Tx_00 = []
    A_Rx2_Tx_11 = []
    A_Rx2_Tx_00 = []
    B_Rx1_Tx_11 = []
    B_Rx1_Tx_00 = []
    B_Rx2_Tx_11 = []
    B_Rx2_Tx_00 = []
    fail_flag = False
    #############Start Test##################
    #########RU power on###############
    '''
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
    time.sleep(60)
    tca.SetLineRate(lineRate='LR9_8')
    tca.SetCpriVersion(version='VER2')
    time.sleep(15)
    tca.DeleteAllCarriers()
    tca.TX_add_carrier(cpriPorts='1A', axc_cont=0, carrier_id=1, tech='LTE', freq=15360, fs_hf=149, fs_bf=147, fs_adr=1, Gain=0)
    tca.TX_add_carrier(cpriPorts='1A', axc_cont=4, carrier_id=3, tech='LTE', freq=15360, fs_hf=149, fs_bf=147, fs_adr=1, Gain=0)
    tca.TX_add_carrier(cpriPorts='1A', axc_cont=8, carrier_id=5, tech='LTE', freq=15360, fs_hf=149, fs_bf=147, fs_adr=1, Gain=0)
    tca.TX_add_carrier(cpriPorts='1A', axc_cont=12, carrier_id=7, tech='LTE', freq=15360, fs_hf=149, fs_bf=147, fs_adr=1, Gain=0)
    tca.IQFileClearAll()
    tca.IQFileAdd(waveform_file, cpriPorts='1A')
    tca.IQFileSetCurrentByName(waveform_file, cpriPorts='1A')
    tca.StartPlayBack()
    '''
    ########Carrier setup############
    rru.openCom()
    rru.sendWait('trdc setup3 1 0 1 758000 0 0 -30 10000 0 0 -30 1 0 0 15360 1 0 1 1 0 0')
    rru.sendWait('trdc setup3 2 0 0 730500 0 0 0 5000 0 0 0 1 0 0 7680 1 0 11 1 0 0')
    rru.sendWait('trdc setup3 3 0 1 783000 0 0 -30 10000 0 0 -30 1 0 0 15360 1 0 1 1 4 0')
    rru.sendWait('trdc setup3 4 0 0 725500 0 0 0 5000 0 0 0 1 0 0 7680 1 0 11 1 2 0')
    rru.sendWait('trdc setup3 5 0 1 758000 0 0 -30 10000 0 1 -30 1 0 0 15360 1 0 1 1 8 0')
    rru.sendWait('trdc setup3 6 0 0 730500 0 0 0 5000 0 1 0 1 0 0 7680 1 0 11 1 4 0')
    rru.sendWait('trdc setup3 7 0 1 783000 0 0 -30 10000 0 1 -30 1 0 0 15360 1 0 1 1 12 0')
    rru.sendWait('trdc setup3 8 0 0 725500 0 0 0 5000 0 1 0 1 0 0 7680 1 0 11 1 6 0')
    #############Read rx power with Tx OFF############
    rru.sendWait('trdc on 2')
    rru.sendWait('trdc on 4')
    rru.sendWait('trdc on 6')
    rru.sendWait('trdc on 8')
    time.sleep(3)
    with open(log_file_name, 'a') as f:
        f.write('TX1 OFF, TX2 OFF\n')
        f.write('{:<30}{:<20}{:<20}{:<20}{:<20}{:<20}\n'.format('Time','RxTemp','A_RX1', 'A_RX2', 'B_RX1', 'B_RX2'))
    for i in range(10):
        Rx_temp = rru.sendWait('ts r Rx:A')[12:-6]
        rx_ipwr = rru.get_rxipwr()
        A_Rx1 = round(rx_ipwr[0]-rx_gain, 2)
        A_Rx2 = round(rx_ipwr[1]-rx_gain, 2)
        B_Rx1 = round(rx_ipwr[12]-rx_gain, 2)
        B_Rx2 = round(rx_ipwr[13]-rx_gain, 2)
        A_Rx1_Tx_00.append(A_Rx1)
        A_Rx2_Tx_00.append(A_Rx2)
        B_Rx1_Tx_00.append(B_Rx1)
        B_Rx2_Tx_00.append(B_Rx2)
        with open(log_file_name, 'a') as f:
            f.write('{:<30}{:<20}{:<20}{:<20}{:<20}{:<20}\n'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),Rx_temp, A_Rx1, A_Rx2, B_Rx1, B_Rx2))
        time.sleep(0.5)
    A_Rx1_Tx_00_ave = np.array(A_Rx1_Tx_00).mean()
    A_Rx2_Tx_00_ave = np.array(A_Rx2_Tx_00).mean()
    B_Rx1_Tx_00_ave = np.array(B_Rx1_Tx_00).mean()
    B_Rx2_Tx_00_ave = np.array(B_Rx2_Tx_00).mean()

    with open(log_file_name, 'a') as f:
        f.write('\n{:<20}{:<20}{:<20}{:<20}\n'.format('A_RX1_AVE', 'A_RX2_AVE', 'B_RX1_AVE', 'B_RX2_AVE'))
        f.write('{:<20}{:<20}{:<20}{:<20}\n'.format(A_Rx1_Tx_00_ave, A_Rx2_Tx_00_ave, B_Rx1_Tx_00_ave, B_Rx2_Tx_00_ave))
        f.write('\n\n')


    #############Read rx power with Tx1 ON TX2 OFF############

    rru.sendWait('trdc on 1')
    rru.sendWait('trdc on 3')
    rru.sendWait('trdc on 5')
    rru.sendWait('trdc on 7')
    time.sleep(5)
    A_tx_power_11 = float(rru.get_trxpower(0)[1].strip(','))
    B_tx_power_11 = float(rru.get_trxpower(1)[1].strip(','))
    with open(log_file_name, 'a') as f:
        f.write('TX1 ON, TX2 ON\n')
        f.write('TX_power_A={:<20} TX_power_B={:<20}\n'.format(A_tx_power_11, B_tx_power_11))
        f.write('{:<30}{:<20}{:<20}{:<20}{:<20}{:<20}\n'.format('Time','RxTemp','A_RX1', 'A_RX2', 'B_RX1', 'B_RX2'))
    for i in range(repeat_times):
        Rx_temp = rru.sendWait('ts r Rx:A')[12:-6]
        rx_ipwr = rru.get_rxipwr()
        A_Rx1 = round(rx_ipwr[0]-rx_gain, 2)
        A_Rx2 = round(rx_ipwr[1]-rx_gain, 2)
        B_Rx1 = round(rx_ipwr[12]-rx_gain, 2)
        B_Rx2 = round(rx_ipwr[13]-rx_gain, 2)
        A_Rx1_Tx_11.append(A_Rx1)
        A_Rx2_Tx_11.append(A_Rx2)
        B_Rx1_Tx_11.append(B_Rx1)
        B_Rx2_Tx_11.append(B_Rx2)
        with open(log_file_name, 'a') as f:
            f.write('{:<30}{:<20}{:<20}{:<20}{:<20}{:<20}\n'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),Rx_temp,A_Rx1, A_Rx2, B_Rx1, B_Rx2))
        time.sleep(delay_per_sample)
    ##########release all###############
    rru.sendWait('trdc release 1')
    rru.sendWait('trdc release 2')
    rru.sendWait('trdc release 3')
    rru.sendWait('trdc release 4')
    rru.sendWait('trdc release 5')
    rru.sendWait('trdc release 6')
    rru.sendWait('trdc release 7')
    rru.sendWait('trdc release 8')
    rru.closeCom()
    #psu.set_output(state='OFF')
    ##########Limit cal and check################
    A_Rx1_Tx_11_ave = np.array(A_Rx1_Tx_11).mean()
    A_Rx2_Tx_11_ave = np.array(A_Rx2_Tx_11).mean()
    B_Rx1_Tx_11_ave = np.array(B_Rx1_Tx_11).mean()
    B_Rx2_Tx_11_ave = np.array(B_Rx2_Tx_11).mean()
    A_Rx1_Tx_11_max = np.array(A_Rx1_Tx_11).max()
    A_Rx2_Tx_11_max = np.array(A_Rx2_Tx_11).max()
    B_Rx1_Tx_11_max = np.array(B_Rx1_Tx_11).max()
    B_Rx2_Tx_11_max = np.array(B_Rx2_Tx_11).max()
    with open(log_file_name, 'a') as f:
        f.write('\n{:<20}{:<20}{:<20}{:<20}\n'.format('A_RX1_AVE', 'A_RX2_AVE', 'B_RX1_AVE', 'B_RX2_AVE'))
        f.write('{:<20}{:<20}{:<20}{:<20}\n'.format(A_Rx1_Tx_11_ave, A_Rx2_Tx_11_ave, B_Rx1_Tx_11_ave, B_Rx2_Tx_11_ave))
        f.write('\n\n')

    if (A_Rx1_Tx_11_ave - A_Rx1_Tx_00_ave > 1):
        with open(log_file_name, 'a') as f:
            f.write('A_Rx1_AVE FAIL\n')
            fail_flag = True
    if (A_Rx2_Tx_11_ave - A_Rx2_Tx_00_ave > 1):
        with open(log_file_name, 'a') as f:
            f.write('A_Rx2_AVE FAIL\n')
            fail_flag = True
    if (B_Rx1_Tx_11_ave - B_Rx1_Tx_00_ave > 1):
        with open(log_file_name, 'a') as f:
            f.write('B_Rx1_AVE FAIL\n')
            fail_flag = True
    if (B_Rx2_Tx_11_ave - B_Rx2_Tx_00_ave > 1):
        with open(log_file_name, 'a') as f:
            f.write('B_Rx2_AVE FAIL\n')
            fail_flag = True

    if (A_Rx1_Tx_11_max - A_Rx1_Tx_00_ave > 1):
        with open(log_file_name, 'a') as f:
            f.write('A_Rx1_PEAK FAIL\n')
            fail_flag = True
    if (A_Rx2_Tx_11_max - A_Rx2_Tx_00_ave > 1):
        with open(log_file_name, 'a') as f:
            f.write('A_Rx2_PEAK FAIL\n')
            fail_flag = True
    if (B_Rx1_Tx_11_max - B_Rx1_Tx_00_ave > 1):
        with open(log_file_name, 'a') as f:
            f.write('B_Rx1_PEAK FAIL\n')
            fail_flag = True
    if (B_Rx2_Tx_11_max - B_Rx2_Tx_00_ave > 1):
        with open(log_file_name, 'a') as f:
            f.write('B_Rx2_PEAK FAIL\n')
            fail_flag = True

    if (abs(A_tx_power_11+8.5)>1):
        with open(log_file_name, 'a') as f:
            f.write('A TX POWER FAIL\n')
            fail_flag = True

    if (abs(B_tx_power_11+8.5)>1):
        with open(log_file_name, 'a') as f:
            f.write('B TX POWER FAIL\n')
            fail_flag = True





    if fail_flag:
        os.rename(log_file_name, 'FAIL-'+log_file_name)
        pop_window = tk.Tk()
        pop_window.title('Result')  # window name
        pop_window.geometry('300x300')  # window size
        tk.Label(pop_window, text='Fail', font=12, bg='red').pack(side='top')
        tk.Button(pop_window, text='OK', font=12, command=pop_window.destroy).pack(side='bottom')
        pop_window.mainloop()
    else:
        pop_window = tk.Tk()
        pop_window.title('Result')  # window name
        pop_window.geometry('300x200')  # window size
        label = tk.Label(pop_window, text='PASS', font=12, bg='green',width = 100,height = 100)

        label.pack(side='top')
        button = tk.Button(pop_window, text='OK', font=12, command=pop_window.destroy).pack(side='bottom')
        pop_window.mainloop()





######Set UI################
root = tk.Tk()  # create a window
root.title('Baltic PIM test')  # window name
root.geometry('500x100')  # window size
font = 12
snFrame = tk.Frame(root, width=500, height=50)
tk.Label(snFrame, text='Serial Number',font=font).pack(side='left')
ipVar = tk.StringVar()
tk.Entry(snFrame, textvariable=ipVar,font=font).pack(side='right')
snFrame.pack()

tk.Button(root, text='Start',font=font, command=lambda: pim_test(ipVar.get().strip('\n'))).pack()


root.mainloop()