import time
import numpy as np
from matplotlib import pyplot as plt
from Lib.Driver.Instruments import PowerMeter, SignalGenerator
from Lib.TestMethod import OBUE, PathLoss, TRDC
from Lib.Driver.Ericsson import RRU
from Lib.Basic import LogConfig
from Lib.Driver.Ericsson.RUMA import TCA
import math

###############setup pamameter###################
Com = "COM12"
branches = ['A', 'B']
rx_ipwr_FB = [0, 12]
tx_path_loss = -40
rx_path_loss = -40
tx_freq = 772e6
rx_freq = 717e6
mpa_table = [0, 1]
dpa_table = [0, 1, 2, 3]

temperature_range_trx = range(-400, 1100, 100)
temperature_norm_trx = 300
temperature_range_pa = range(-40, 110, 10)
temperature_norm_pa = 30
pa_prefix = '/pa/table'
trx_prefix = '/7xx/id_ruType_1.12.x/Band28F_68'
time_step = 1
time_total = 30
trdc_on_delay = 3
address_power_meter = 'GPIB0::9::INSTR'
address_signal_gen = 'TCPIP0::192.168.0.11::inst0::INSTR'
############init test###################
pm = PowerMeter.PowerMeter(address_power_meter, timeout=10)
pm.reset()
pm.set_dbm()
sg = SignalGenerator.SignalGenerator(address_signal_gen, timeout=10)
# set sg later
# sg.reset()
sg.set_freq(rx_freq)
# sg.set_waveform('E_UTRA_UL_5')
branch_index = range(len(branches))
tct_size = len(temperature_range_trx)
LogConfig.init_logger()
testlog = LogConfig.get_logger()
tca = TCA()

ru = RRU.DutSerial(portx=Com, bps=115200, timex=5)
ru.openCom()
trdc_tx = TRDC.TRDC_DL(branches=[0], rru=ru, tca=tca, carriers_setup_string=['L50tm3p1_{}_P-3.0dB'.format(tx_freq)])

###set TCT to 0###
tx_zero_tct_xy = ''
rx_zero_TCT_x = ''
rx_zero_TCT_y = ''
for t in temperature_range_trx:
    tx_zero_tct_xy = tx_zero_tct_xy + '{} 0 '.format(t)
    rx_zero_TCT_x = rx_zero_TCT_x + '{} '.format(t)
    rx_zero_TCT_y = rx_zero_TCT_y + '0 '.format(t)

rx_temp = []
rx_highgain_noatt = []
rx_highgain_att = []
rx_bypass_noatt = []
rx_bypass_att = []
tor_temp = []
tor_outputpower = []
pa_temp = []
pa_offset = []
'''
# set all trx TCT to 0
for i in branch_index:

    ru.sendWait('db resize {}/tx{}/tor/tempCorTab {}'.format(trx_prefix, branches[i], tct_size * 2))
    ru.sendWait('db resize {}/rx1{}/highGain/noAtt/gainTempCompTable_x {}'.format(trx_prefix, branches[i], tct_size))
    ru.sendWait('db resize {}/rx1{}/highGain/noAtt/gainTempCompTable_y {}'.format(trx_prefix, branches[i], tct_size))
    ru.sendWait('db resize {}/rx1{}/highGain/att/gainTempCompTable_x {}'.format(trx_prefix, branches[i], tct_size))
    ru.sendWait('db resize {}/rx1{}/highGain/att/gainTempCompTable_y {}'.format(trx_prefix, branches[i], tct_size))
    ru.sendWait('db resize {}/rx1{}/bypass/noAtt/gainTempCompTable_x {}'.format(trx_prefix, branches[i], tct_size))
    ru.sendWait('db resize {}/rx1{}/bypass/noAtt/gainTempCompTable_y {}'.format(trx_prefix, branches[i], tct_size))
    ru.sendWait('db resize {}/rx1{}/bypass/att/gainTempCompTable_x {}'.format(trx_prefix, branches[i], tct_size))
    ru.sendWait('db resize {}/rx1{}/bypass/att/gainTempCompTable_y {}'.format(trx_prefix, branches[i], tct_size))
    ru.sendWait('db resize {}/rx3{}/gainTempCompTable_x {}'.format(trx_prefix, branches[i], tct_size))
    ru.sendWait('db resize {}/rx3{}/gainTempCompTable_y {}'.format(trx_prefix, branches[i], tct_size))

    ru.sendWait('db write {}/tx{}/tor/tempCorTab {}'.format(trx_prefix, branches[i], tx_zero_tct_xy))
    ru.sendWait('db write {}/rx1{}/highGain/noAtt/gainTempCompTable_x {}'.format(trx_prefix, branches[i], rx_zero_TCT_x))
    ru.sendWait('db write {}/rx1{}/highGain/noAtt/gainTempCompTable_y {}'.format(trx_prefix, branches[i], rx_zero_TCT_y))
    ru.sendWait('db write {}/rx1{}/highGain/att/gainTempCompTable_x {}'.format(trx_prefix, branches[i], rx_zero_TCT_x))
    ru.sendWait('db write {}/rx1{}/highGain/att/gainTempCompTable_y {}'.format(trx_prefix, branches[i], rx_zero_TCT_y))
    ru.sendWait('db write {}/rx1{}/bypass/noAtt/gainTempCompTable_x {}'.format(trx_prefix, branches[i], rx_zero_TCT_x))
    ru.sendWait('db write {}/rx1{}/bypass/noAtt/gainTempCompTable_y {}'.format(trx_prefix, branches[i], rx_zero_TCT_y))
    ru.sendWait('db write {}/rx1{}/bypass/att/gainTempCompTable_x {}'.format(trx_prefix, branches[i], rx_zero_TCT_x))
    ru.sendWait('db write {}/rx1{}/bypass/att/gainTempCompTable_y {}'.format(trx_prefix, branches[i], rx_zero_TCT_y))
    ru.sendWait('db write {}/rx3{}/gainTempCompTable_x {}'.format(trx_prefix, branches[i], rx_zero_TCT_x))
    ru.sendWait('db write {}/rx3{}/gainTempCompTable_y {}'.format(trx_prefix, branches[i], rx_zero_TCT_y))

    rx_temp.append([])
    rx_highgain_noatt.append([])
    rx_highgain_att.append([])
    rx_bypass_noatt.append([])
    rx_bypass_att.append([])
    tor_temp.append([])
    tor_outputpower.append([])
    pa_temp.append([])
    pa_offset.append([])

    # setup Rx carrier
    ru.sendWait(
        'trdc setup7 {} 1 0 0 {} 0 0 0 0 1 {} 0 0 1 0 11 1 {} {} 4 0 '.format(len(branches) + i + 1, int(rx_freq / 1e3),
                                                                              i, math.floor(i / 2), i % 2))
    ru.sendWait('trdc on {}'.format(len(branches) + i + 1))
'''
start_time = time.time()
while time.time() - start_time < time_total:
    '''
    for i in branch_index:
        #####read rx temp and ipwr
        rx_temp[i].append(ru.get_single_data('ts r Rx:{}'.format(branches[i])))
        sg.set_rf_state('ON')
        ru.set_rx_front_end(branch=branches[i], bypass='off', att='off')
        time.sleep(0.5)
        rx_highgain_noatt[i].append(ru.get_rxipwr()[rx_ipwr_FB[i]])
        ru.set_rx_front_end(branch=branches[i], bypass='off', att='on')
        time.sleep(0.5)
        rx_highgain_att[i].append(ru.get_rxipwr()[rx_ipwr_FB[i]])
        ru.set_rx_front_end(branch=branches[i], bypass='on', att='off')
        time.sleep(0.5)
        rx_bypass_noatt[i].append(ru.get_rxipwr()[rx_ipwr_FB[i]])
        ru.set_rx_front_end(branch=branches[i], bypass='on', att='on')
        time.sleep(0.5)
        rx_bypass_att[i].append(ru.get_rxipwr()[rx_ipwr_FB[i]])
        sg.set_rf_state('OFF')
    '''
    ##########PA cal##########################




    ####read Tx temp and power####
    '''
    for i in branch_index:
        trdc_tx.branches = [i]
        trdc_tx.del_all_carrier()
        trdc_tx.set_up_DL_carrier_init()
        time.sleep(5)
        tor_temp[i].append(ru.get_single_data('ts r Tor:{}'.format(branches[i])))
        tor_outputpower[i].append(pm.read_power())
        trdc_tx.trdc_release_all()

    time.sleep(time_step)
    '''

temp = ru.get_single_data('ts r PaDriver:A')
for i in branch_index:
    ru.sendWait('trdc release {}'.format(len(branches) + i + 1))
ru.closeCom()
