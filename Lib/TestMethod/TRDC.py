import math

from Lib.Driver.Ericsson import RRU
from Lib.Driver.Ericsson.RUMA import TCA
from Lib.Basic import LogConfig
import re


class TRDC_DL():
    def __init__(self, branches, carriers_setup_string, rru=None,tca = None, trdc_start_index=1,cpriPorts='1A'):
        self.rru = rru
        self.tca = tca
        self.carriers_setup_string = carriers_setup_string
        self.branches = branches
        self.carriers_setup = []
        self.cpriPorts = cpriPorts
        self.trdc_start_index = trdc_start_index
        self.config_path = r'C:\RuPyTestConfig\trdc'
        self.trdc_index = range(trdc_start_index, trdc_start_index+len(carriers_setup_string)*len(self.branches))
        self.axc_cont = [0]
        for carrier_setup_string in self.carriers_setup_string:
            carrier_setup = carrier_setup_string.split('_')
            setup = {}
            setup['CarrierName'] = carrier_setup[0]
            setup['CenterFreq'] = float(carrier_setup[1])
            setup['PowerBackoff'] = float(carrier_setup[2].strip('P').strip('dB'))
            with open(r'C:\RuPyTestConfig\trdc\TxPattern.txt', 'r') as f:
                tag = f.readline()
                tag = tag.split()
                config = f.readlines()
                for cfg in config:
                    cfg = cfg.split()
                    if cfg[0] == setup['CarrierName']:
                        for i in range(len(tag)):
                            setup[tag[i]] = cfg[i]
            self.carriers_setup.append(setup)
        for branch in self.branches:
            for carrier_setup in self.carriers_setup:
                    self.axc_cont.append(self.axc_cont[-1] + int(int(carrier_setup['SamplingRate']) / 3840))




    def get_txPattern(self, carrier_name):
        with open(r'C:\RuPyTestConfig\trdc\TxPattern.txt', 'r') as f:
            tag = f.readline()
            tag = tag.split()
            config = f.readlines()
            for cfg in config:
                cfg = cfg.split()
                if cfg[0] == carrier_name:
                    cfg_dict = {}
                    for i in range(len(tag)):
                        cfg_dict[tag[i]] = cfg[i]
                    return cfg_dict


    def trdc_command(self, devId, setupRfPort, carrier_setup,axc_cont,axcSlotSize=4, arfcnMin=0, arfcnMax=0, frameStartOffs=0,iqMsgSetting=1,isBcch=0, noOfCpriLinks=1, cpriPort=0,axcId=1, axcIdRxControl=1,bfOffset=0):
        carrierTypeId = carrier_setup['carrierTypeId']
        ratType = carrier_setup['ratType']
        recTransm = 1
        crFreq = int(carrier_setup['CenterFreq']/1e3)
        txCrPowAlloc = int(carrier_setup['PowerBackoff'] * 10)
        txCarrGainSett = txCrPowAlloc
        iqSubFrameNumber = math.floor(axc_cont / 4)
        iqSubFrameIndex = axc_cont % 4
        #default is LTE5 DL
        command = 'trdc setup7 {0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11} {12} {13} {14} {15} {16} {17} {18} {19} {20}'.format(
            devId, carrierTypeId, ratType, recTransm, crFreq, arfcnMin, arfcnMax, txCrPowAlloc, frameStartOffs, iqMsgSetting, setupRfPort,
            txCarrGainSett,isBcch, noOfCpriLinks, cpriPort, axcId, axcIdRxControl, iqSubFrameNumber, iqSubFrameIndex, axcSlotSize, bfOffset)
        data = self.rru.sendWait(command)
        data = data.split('\n')
        for d in data:
            if re.search('radioTimeDelay', d):
                d = float(d.split('=')[-1].strip())
                break
        fs_bf = 256-math.ceil(d*(1e-10)*(3.84e6))
        return_data = {}
        return_data['fs_bf'] = fs_bf



        return return_data
        # devId: 				trdc number
        # carrierTypeId: 		check with 'db list */carrierTypeList used', should be configed
        # ratType: 				LTE=0, NR=6, should be configed
        # recTransm				Tx = 1, Rx=0
        # crFreq				Carrier center frequency (kHz)
        # arfcnMin/arfcnMax		GSM frequency hopping, otherwise set 0
        # txCrPowAlloc			Power relative to Pmax, (0.1dB)
        # frameStartOffs 		Usually 0
        # iqMsgSetting			What is it? Usually 0?
        # setupRfPort			Antenna Port Number
        # txCarrGainSett		Same as txCrPowAlloc
        # isBcch				Normally 0
        # noOfCpriLinks			Normally 1
        # cpriPort				CPRI port number
        # axcId					What is it? Tx = 1, Rx = 11?
        # axcIdRxControl		What is it? Usually 1?
        # iqSubFrameNumber
        # iqSubFrameIndex
        # axcSlotSize			What is it? Usually 4?
        # bfOffset				Basic frame offset, set to 0

    def del_all_carrier(self, cpri='1A', direction='TX'):
        self.tca.DeleteAllCarriers(cpriPorts=self.cpriPorts,flowDirection=direction)

    def get_waveform_file(self):
        #only single waveform support currently
        waveform_file = self.config_path + '\\'+ self.carriers_setup[0]['WaveformFile']
        return waveform_file

    def trdc_on_all(self):
        for i in self.trdc_index:
            self.rru.sendWait('trdc on {}'.format(i))

    def trdc_release_all(self):
        for i in self.trdc_index:
            self.rru.sendWait('trdc off {}'.format(i))
            self.rru.sendWait('trdc release {}'.format(i))

    def send_trdc_commond(self):
        carrier_id = self.trdc_start_index
        for branch in self.branches:
            for carrier_setup in self.carriers_setup:
                if carrier_setup['Techonology']=="LTE":
                    self.trdc_command(devId=carrier_id, setupRfPort=branch, carrier_setup=carrier_setup,axc_cont=self.axc_cont[carrier_id-self.trdc_start_index])
                    carrier_id = carrier_id +1

    def set_up_DL_carrier_init(self):
        carrier_id= self.trdc_start_index
        #self.tca.IQFileClearAll()
        self.tca.SetStartStopCondition(cpriPorts=self.cpriPorts, flowDirection = 'TX',flowDataType='IQ', startCondition='FRAME_PRE_START',startCondParam=[0,0,0,0],stopCondition='NEVER',stopCondParam=[0,0,0,0])
        self.tca.IQFileAdd(self.get_waveform_file(), cpriPorts=self.cpriPorts)
        self.tca.IQFileSetCurrentByName(self.get_waveform_file(), cpriPorts=self.cpriPorts)
        axc_cont_index=0
        for branch in self.branches:
            for carrier_setup in self.carriers_setup:
                if carrier_setup['Techonology']=="LTE":
                    fs_adr = 1
                    trdc_return_data = self.trdc_command(devId=carrier_id, setupRfPort=branch, carrier_setup=carrier_setup,axc_cont=self.axc_cont[-1])
                    self.tca.TX_add_carrier(cpriPorts=self.cpriPorts, axc_cont=self.axc_cont[axc_cont_index], carrier_id=carrier_id, tech='LTE', freq=int(carrier_setup['SamplingRate']), fs_hf=149,
                                   fs_bf=trdc_return_data['fs_bf'], fs_adr=fs_adr, Gain=0)
                    axc_cont_index = axc_cont_index +1
                    carrier_id = carrier_id + 1
        self.trdc_on_all()
        self.tca.StartPlayBack(cpriPorts=self.cpriPorts)

class TRDC_UL():
    def __init__(self, branches, carriers_setup_string, rru=None,tca = None, trdc_start_index=1,cpriPorts='1A'):
        self.rru = rru
        self.tca = tca
        self.carriers_setup_string = carriers_setup_string
        self.branches = branches
        self.carriers_setup = []
        self.cpriPorts = cpriPorts
        self.trdc_start_index = trdc_start_index
        self.config_path = r'C:\RuPyTestConfig\trdc'
        self.trdc_index = range(trdc_start_index, trdc_start_index+len(carriers_setup_string)*len(self.branches))
        self.axc_cont = [0]
        for carrier_setup_string in self.carriers_setup_string:
            carrier_setup = carrier_setup_string.split('_')
            setup = {}
            setup['CarrierName'] = carrier_setup[0]
            setup['CenterFreq'] = float(carrier_setup[1])
            with open(r'C:\RuPyTestConfig\trdc\RxPattern.txt', 'r') as f:
                tag = f.readline()
                tag = tag.split()
                config = f.readlines()
                for cfg in config:
                    cfg = cfg.split()
                    if cfg[0] == setup['CarrierName']:
                        for i in range(len(tag)):
                            setup[tag[i]] = cfg[i]
            self.carriers_setup.append(setup)
        for b in self.branches:
            for carrier_setup in self.carriers_setup:
                    self.axc_cont.append(self.axc_cont[-1] + int(int(carrier_setup['SamplingRate']) / 3840))


    def get_rxPattern(self, carrier_name):
        with open(r'C:\RuPyTestConfig\trdc\RxPattern.txt', 'r') as f:
            tag = f.readline()
            tag = tag.split()
            config = f.readlines()
            for cfg in config:
                cfg = cfg.split()
                if cfg[0] == carrier_name:
                    cfg_dict = {}
                    for i in range(len(tag)):
                        cfg_dict[tag[i]] = cfg[i]
                    return cfg_dict


    def trdc_command(self, devId, setupRfPort, carrier_setup,axc_cont,axcSlotSize=4, arfcnMin=0, arfcnMax=0, frameStartOffs=0,iqMsgSetting=1,isBcch=0, noOfCpriLinks=1, cpriPort=0, axcIdRxControl=1,bfOffset=0):
        carrierTypeId = carrier_setup['carrierTypeId']
        ratType = carrier_setup['ratType']
        recTransm = 0
        crFreq = int(carrier_setup['CenterFreq']/1e3)
        txCrPowAlloc = 0
        txCarrGainSett = txCrPowAlloc
        axcId = 11
        iqSubFrameNumber = math.floor(axc_cont / 4)
        iqSubFrameIndex = axc_cont % 4
        #default is LTE5 DL
        command = 'trdc setup7 {0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11} {12} {13} {14} {15} {16} {17} {18} {19} {20}'.format(
            devId, carrierTypeId, ratType, recTransm, crFreq, arfcnMin, arfcnMax, txCrPowAlloc, frameStartOffs, iqMsgSetting, setupRfPort,
            txCarrGainSett,isBcch, noOfCpriLinks, cpriPort, axcId, axcIdRxControl, iqSubFrameNumber, iqSubFrameIndex, axcSlotSize, bfOffset)
        self.rru.sendWait(command)

        # devId: 				trdc number
        # carrierTypeId: 		check with 'db list */carrierTypeList used', should be configed
        # ratType: 				LTE=0, NR=6, should be configed
        # recTransm				Tx = 1, Rx=0
        # crFreq				Carrier center frequency (kHz)
        # arfcnMin/arfcnMax		GSM frequency hopping, otherwise set 0
        # txCrPowAlloc			Power relative to Pmax, (0.1dB)
        # frameStartOffs 		Usually 0
        # iqMsgSetting			What is it? Usually 1?
        # setupRfPort			Antenna Port Number
        # txCarrGainSett		Same as txCrPowAlloc
        # isBcch				Normally 0
        # noOfCpriLinks			Normally 1
        # cpriPort				CPRI port number
        # axcId					What is it? Tx = 1, Rx = 11?
        # axcIdRxControl		What is it? Usually 1?
        # iqSubFrameNumber
        # iqSubFrameIndex
        # axcSlotSize			What is it? Usually 4?
        # bfOffset				Basic frame offset, set to 0

    def del_all_carrier(self, direction='RX'):
        self.tca.DeleteAllCarriers(cpriPorts=self.cpriPorts,flowDirection=direction)

    def get_waveform_file(self):
        #only single waveform support currently
        waveform_file = self.config_path + '\\'+ self.carriers_setup[0]['WaveformFile']
        return waveform_file

    def trdc_on_all(self):
        for i in self.trdc_index:
            self.rru.sendWait('trdc on {}'.format(i))

    def trdc_release_all(self):
        for i in self.trdc_index:
            self.rru.sendWait('trdc off {}'.format(i))
            self.rru.sendWait('trdc release {}'.format(i))

    def send_trdc_commond(self):
        carrier_id = self.trdc_start_index
        for branch in self.branches:
            for carrier_setup in self.carriers_setup:
                if carrier_setup['Techonology']=="LTE":
                    self.trdc_command(devId=carrier_id, setupRfPort=branch, carrier_setup=carrier_setup,axc_cont=self.axc_cont[carrier_id-self.trdc_start_index])
                    carrier_id = carrier_id +1

    def set_up_UL_carrier_init(self):
        carrier_id= self.trdc_start_index
        axc_cont_index=0
        for branch in self.branches:
            for carrier_setup in self.carriers_setup:
                if carrier_setup['Techonology']=="LTE":
                    self.trdc_command(devId=carrier_id, setupRfPort=branch, carrier_setup=carrier_setup,axc_cont=self.axc_cont[-1])
                    self.tca.RX_add_carrier(cpriPorts=self.cpriPorts,axc_cont=self.axc_cont[axc_cont_index],carrier_id=carrier_id,tech='LTE',freq=int(carrier_setup['SamplingRate']) ,fs_hf=0,fs_bf=46,fs_adr=1,syncMode1='FSINFO')
                    axc_cont_index = axc_cont_index +1
                    carrier_id = carrier_id + 1
        self.trdc_on_all()

    def get_UL_IQ(self):
        samples_as_complex = self.tca.GetCarrierSamples(38400, 0, 0, carrierIndex=0, startCondition='RADIO_FRAME',
                                                   cpriDataConfig=[], cpriPorts=self.cpriPorts)


'''
#DL trial
if __name__ == '__main__':
    LogConfig.init_logger()
    testlog = LogConfig.get_logger()
    Com = "COM12"
    rru = RRU.DutSerial(portx=Com, bps=115200, timex=5)
    tca = TCA()
    rru.openCom()



    trdc1 = TRDC_DL(branches =[0, 1], rru=rru, tca=tca, carriers_setup_string=['L50tm3p1_770e6_P-3.0dB', 'L50tm3p1_780e6_P-3.0dB'])
    trdc1.del_all_carrier()
    trdc1.set_up_DL_carrier_init()
    trdc1.send_trdc_commond()
    trdc1.trdc_on_all()
    trdc1.trdc_release_all()
    rru.closeCom()
    print(trdc1.carriers_setup)
'''

#UL trial
if __name__ == '__main__':
    LogConfig.init_logger()
    testlog = LogConfig.get_logger()
    Com = "COM12"
    rru = RRU.DutSerial(portx=Com, bps=115200, timex=5)
    tca = TCA()
    rru.openCom()



    trdc1 = TRDC_UL(branches =[0, 1], rru=rru, tca=tca, carriers_setup_string=['L50tm3p1_710e6', 'L50tm3p1_720e6'])
    trdc1.del_all_carrier()
    trdc1.set_up_UL_carrier_init()

#    trdc1.send_trdc_commond()
#    trdc1.trdc_on_all()
    trdc1.trdc_release_all()
    rru.closeCom()
    print(trdc1.carriers_setup)
