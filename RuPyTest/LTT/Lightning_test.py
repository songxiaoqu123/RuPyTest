import time
from Lib.Basic import LogConfig
from Lib.Driver.Ericsson import RRU

LogConfig.init_logger()
testlog = LogConfig.get_logger()

########Tset Setup######################################################
dut_com = ['COM11']
port = ['A', 'B', 'C', 'D']

output_path = 'Logs\\'
totall_cycle = 50000


sample_period = 5
state = 'testing'
tx_norm = 47.8
tx_freq = 2160e6
tx_pathloss = [-37.0, -36.7, -37.1, -37]

rx_norm = -50
rx_gain_norm = 151.4
rx_freq = 1970e6
rx_pathloss = [-33.2, -33.0, -33.3, -33.1]
rx_pwr_index = [0, 6, 12, 18]


#sg = Keysignt_E4438C('TCPIP0::192.168.0.63::inst0::INSTR')
#pm = Instruments.PowerMeter('USB0::0x0AAD::0x00E2::107227::INSTR')
#vsa = Instruments.VectorSpectrumAnalyzer('TCPIP0::K-N9020B-6018-2.local::hislip0::INSTR')


##########Init Test######################################################
dut_index = range(len(dut_com))
port_index = range(len(port))
#switch_matrix = HRSM.HRSM()

starttime = time.strftime("%Y%m%d%H%M%S", time.localtime())
sample = 0
outputfile = []
dut = []
for i in dut_index:
    dut.append(RRU.DutSerial(portx=dut_com[i], bps=115200, timex=5))
    for j in port_index:
        outputfile.append('{}DUT{}-PORT{}-{}.txt'.format(output_path, i, port[j], starttime))

        with open(outputfile[i * len(port) + j], 'w') as f:
            f.write(starttime)
            dut[i].openCom()
            f.write(dut[i].sendWait('par get'))
            f.write('\n')
            f.write('{:20}{:20}{:20}{:20}{:20}{:20}{:20}{:20}{:20}{:30}{:20}{:20}{:20}{:20}'.format('Sample', 'Cycle', 'State', 'Tx-norm',
                                                                                'TxPower', 'TxDeltaPower', 'Rx-norm',
                                                                                'RxPower', 'RxDeltaPower', 'StartTime',
                                                                                'ACLR_L', 'ACLR_R', 'EVM', 'Frequency_Err'))

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
            f.write('{:40}'.format('fm_fault'))
            f.write('\n')

#########StartTest###################################################
#try:
for cycle in range(totall_cycle):
    try:
        for i in dut_index:
            for j in port_index:
                test_index = i * len(port) + j
                '''
                switch_matrix.set_path(switch_matrix.path1[test_index])
                time.sleep(3)
                tx_power = 0
                tx_power = pm.read_power() - tx_pathloss[test_index]
                vsa.set_data_format(3)
                vsa.send(':CONFigure:ACPower')
                ACLR = vsa.query(':FETCh:ACPower?')
                ACLR = ACLR.split(',')
                ACLR_L = float(ACLR[4])
                ACLR_R = float(ACLR[6])
                vsa.send(':CONFigure:CEVM')
                CEVM = vsa.query(':FETCh:CEVM?')
                CEVM = CEVM.split(',')
                EVM = float(CEVM[0])
                Freq_err = float(CEVM[12])

                switch_matrix.set_path(switch_matrix.path2[test_index])

                sg.set_freq(rx_freq)
                sg.set_amp(rx_norm - rx_pathloss[test_index])
                sg.set_rf_state('ON')
                time.sleep(0.5)
                dut[i].openCom()
                rx_power = dut[i].get_rxipwr()

                rx_power = rx_power[rx_pwr_index[test_index]]

                rx_power = rx_power - rx_gain_norm
                '''
                tx_power = 0
                rx_power = 0
                ACLR_L = 0
                ACLR_R = 0
                EVM = 0
                Freq_err = 0
                with open(outputfile[test_index], 'a') as f:
                    f.write('\n')
                    test_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    f.write('{: <20d}{: <20d}{:20}{: <20f}{: <20f}{: <20f}{: <20f}{: <20f}{: <20f}{:30}{: <20f}{: <20f}{: <20f}{: <20f}'.format(sample, cycle, state, tx_norm, tx_power, tx_power - tx_norm,
                                                                                                            rx_norm, rx_power, rx_power - rx_norm, test_time,
                                                                                                            ACLR_L, ACLR_R, EVM, Freq_err))

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
                    fm_fault = dut[i].get_fmfault()
                    f.write('{:40}'.format(fm_fault))


                #dut[i].closeCom()
                #sg.set_rf_state('OFF')

        sample = sample + 1
        time.sleep(sample_period)
    except:
        pass

#except:

        #dut[i].closeCom()
