# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 10:45:31 2020

@author: easixno
"""

import serial
import serial.tools.list_ports
import re
import time
import paramiko  # 用于调用scp命令
from scp import SCPClient
from Lib.Basic import LogConfig

testlog = LogConfig.get_logger()


def list_com():
    port_list = list(serial.tools.list_ports.comports())
    print(port_list)
    if len(port_list) == 0:
        testlog.warning("No COM detected")
    else:
        for i in range(0, len(port_list)):
            print(port_list[i])


class DutSerial:
    def __init__(self, portx="COM11", bps=115200, timex=5):
        self.portx = portx
        self.bps = bps
        self.timex = timex
        self.ser = serial.Serial(portx, bps, timeout=timex)
        self.ser.close()

    def openCom(self):
        try:
            self.ser.open()
            testlog.info('{} is opened'.format(self.portx))
        except:
            testlog.warning('{} is not opened'.format(self.portx))
            raise Exception

    def closeCom(self):
        try:
            self.ser.close()
            testlog.info('{} is closed'.format(self.portx))
        except:
            testlog.warning('{} is not closed'.format(self.portx))
            raise Exception

    def send(self, string, encodeMode='utf-8', icolish=False, end='\n\r'):
        if (icolish):
            message = 'icolish -c \"{}\"{}'.format(string, end).encode(encodeMode)
        elif (not icolish):
            message = (string + end).encode(encodeMode)
        try:
            self.ser.write(message)
            testlog.info('Send to RU: {}'.format(message))
        except Exception:
            self.closeCom()

    def read(self):
        try:
            dataLength = self.ser.inWaiting()
            data = self.ser.read(dataLength).decode('utf-8')
        except UnicodeDecodeError:
            data = '???'
        return data

    def waitCommand(self, pattern='~#', timeout=10, delay=0.1):
        currentTime = time.time()
        outputData = ''
        while (time.time() - currentTime < timeout):
            data = self.read()
            if data:
                outputData = outputData + data
                testlog.info('Read from {}:\n{}'.format(self.portx, data))
                if (re.search(pattern, data)):
                    return outputData
            time.sleep(delay)
        self.closeCom()
        raise TimeoutError

    def waitData(self, pattern='~#', timeout=10, delay=0.1):
        currentTime = time.time()
        outputData = ''
        while (time.time() - currentTime < timeout):
            data = self.read()
            if data:
                print(data, end='')
                outputData = outputData + data
                if (re.search(pattern, data)):
                    return outputData
            time.sleep(delay)
        self.closeCom()
        raise TimeoutError

    def waitFloat(self, pattern='~#', timeout=10, delay=0.1):
        data = self.waitData(pattern=pattern, timeout=timeout, delay=delay).split('\n')
        for d in data:
            floatdata = re.search(re.compile('^\d\.\d'), d)
            if floatdata:
                return float(d)
        raise Exception('Can not find the data')

    def waitSend(self, string, pattern='\$|~#', timeout=10, delay=0.1, encodeMode='utf-8'):
        self.waitCommand(pattern=pattern, timeout=timeout, delay=delay)
        self.send(string, encodeMode='utf-8')

    def sendWait(self, string, pattern='\$|~#', timeout=10, delay=0.1, encodeMode='utf-8'):
        self.send(string, encodeMode='utf-8')
        return self.waitCommand(pattern=pattern, timeout=timeout, delay=delay)

    def setSwitch(self, switch, num, state):
        for i in num:
            self.sendWait('sw s {}:{} {}\n'.format(switch, i, state))

    def par_get(self):
        data = self.sendWait('par get', pattern='\$|~#', timeout=10, delay=0.1, encodeMode='utf-8')
        data = re.split('\r\n', data)[1:-2]
        output = {}
        for d in data:
            d = d.split('=')
            output[d[0].strip().strip('\'')]=d[1].strip().strip('\'')
        return output

    def get_ts(self):
        data = self.sendWait('ts r', pattern='\$|~#', timeout=10, delay=0.1, encodeMode='utf-8')
        data = re.split('\s:|\r\n', data)[1:-2]
        for i in range(len(data)):
            data[i] = data[i].strip().strip('\'')
        return data

    def get_vs(self):
        data = self.sendWait('vs r', pattern='\$|~#', timeout=10, delay=0.1, encodeMode='utf-8')
        data = re.split('\s:|\r\n', data)[1:-2]
        for i in range(len(data)):
            data[i] = data[i].strip().strip('\'')
        return data

    def get_cs(self):
        data = self.sendWait('cs r', pattern='\$|~#', timeout=10, delay=0.1, encodeMode='utf-8')
        data = re.split('\s:|\r\n', data)[1:-2]
        for i in range(len(data)):
            data[i] = data[i].strip().strip('\'')
        return data

    def get_rvc(self):
        data = self.sendWait('rvc r', pattern='\$|~#', timeout=10, delay=0.1, encodeMode='utf-8')
        data = re.split('\s:|\r\n', data)[1:-2]
        for i in range(len(data)):
            data[i] = data[i].strip().strip('\'')
        return data

    def get_sw(self):
        data = self.sendWait('sw g', pattern='\$|~#', timeout=10, delay=0.1, encodeMode='utf-8')
        data = re.split('\s:|\r\n', data)[1:-2]
        for i in range(len(data)):
            data[i] = data[i].strip().strip('\'')
        return data

    def get_trxpower(self, port=0):
        data = self.sendWait('trx power {}'.format(port), pattern='\$|~#', timeout=10, delay=0.1, encodeMode='utf-8')
        data = re.split('\s:|\r\n', data)[1:-2]
        for i in range(len(data)):
            data[i] = data[i].strip().strip('\'')
        return data

    def get_rxipwr(self, xenon=0):
        data = self.sendWait('xenon:{} rxpwr'.format(xenon), pattern='\$|~#', timeout=10, delay=0.1, encodeMode='utf-8')
        data = re.split('\s:|\r\n', data)[2:-19]
        for i in range(len(data)):
            data[i] = data[i].strip().strip('\'').strip('B').strip('d')
        data = data[1::2]
        for i in range(len(data)):
            data[i] = float(data[i])
        return data

    def get_rxipwr_fb(self, xenon=0, fb = 0, repeat = 10):
        ipwr = 0
        for i in range(repeat):
            ipwr = ipwr + self.get_rxipwr(xenon=xenon)[fb]
        return ipwr/repeat


    def set_rx_front_end(self, branch = 'A', bypass='off', att = 'off'):
        self.sendWait('sw s RxLnaBypass:{} {}'.format(branch,bypass))
        self.sendWait('sw s RxLna6dBAtt:{} {}'.format(branch, att))


    def get_dpdRestartCount(self, port):
        data = self.sendWait('trx dpd restart_counter {}'.format(port), pattern='\$|~#', timeout=10, delay=0.1,
                             encodeMode='utf-8')
        data = re.split('\s:|\r\n', data)[1:-2]
        data = ''.join(data)
        data = data[-1]
        return data

    def get_fmfault(self, xenon=0):
        data = self.sendWait('fm getfaults', pattern='\$|~#', timeout=10, delay=0.1, encodeMode='utf-8')
        data = re.split('\s:|\r\n', data)[1:-2]
        data = ''.join(data)
        data = data.strip()
        return data

    def get_single_data(self, command,index=-3, repeat=1):
        if repeat==1:
            for i in range(repeat):
                data = self.sendWait('{}'.format(command), pattern='\$|~#', timeout=10, delay=0.1,
                                     encodeMode='utf-8')
                data = re.split('\s:|\r\n', data)[index]
                return data
        elif repeat >1:
            temp=0
            for i in range(repeat):
                data = self.sendWait('{}'.format(command), pattern='\$|~#', timeout=10, delay=0.1,
                                     encodeMode='utf-8')
                data = re.split('\s:|\r\n', data)[index]
                temp = temp + float(data)
            return temp/repeat

    def calibrate_pa(self, name, target, start_offset = 0, accurecy = 3):
        offset = start_offset
        self.sendWait('ch w G{} {}'.format(name, offset))
        current = float(self.get_single_data('ch r I{}'.format(name)))

        while True:
            if abs(current - target)<accurecy:
                current = float(self.get_single_data('ch r I{}'.format(name),repeat=5))
                if abs(current - target)<accurecy:
                    break
            if target - current > accurecy:
                offset = offset + 10
            elif target - current < -1 * accurecy:
                offset = offset - 1
            self.sendWait('ch w G{} {}'.format(name, offset))
            #time.sleep(0.1)
            current = float(self.get_single_data('ch r I{}'.format(name)))
        self.sendWait('ch w G{} 0'.format(name, offset))
        return offset




    def trdc_single_carrier(self, devId=1, carrierTypeId=1, ratType=0, recTransm=1, crFreq=1e9, arfcnMin=0, arfcnMax=0, txCrPowAlloc=0, frameStartOffs=0, iqMsgSetting=1, setupRfPort=0,
            isBcch=0, noOfCpriLinks=1, cpriPort=0, axcId=1, axcIdRxControl=1, iqSubFrameNumber=0, iqSubFrameIndex=0, axcSlotSize=4, bfOffset=0):
        #default is LTE5 DL
        crFreq = int(crFreq/1e3)
        txCrPowAlloc = int(txCrPowAlloc * 10)
        txCarrGainSett = txCrPowAlloc
        command = 'trdc setup7 {0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11} {12} {13} {14} {15} {16} {17} {18} {19} {20}'.format(
            devId, carrierTypeId, ratType, recTransm, crFreq, arfcnMin, arfcnMax, txCrPowAlloc, frameStartOffs, iqMsgSetting, setupRfPort,
            txCarrGainSett,isBcch, noOfCpriLinks, cpriPort, axcId, axcIdRxControl, iqSubFrameNumber, iqSubFrameIndex, axcSlotSize, bfOffset)
        return command
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

    def setup_single_dl_carrier(self,id=1, F_id=1, type=0, direction=1, freq=1e9, par5=0, par6=0, backoff=0, par8=0,par9=1,branch=0, par12=0,par13=1,par14=0, par15=11, par16=1,axc_add1=0, axc_add2=0,AXC_size_id=4, par20=0):
        pass

'''        
    def readByTime(self,time):
        self.ser.open()
        dataLength = self.ser.inWaiting()
        try:
            data= self.ser.read(dataLength).decode('utf-8')
        except UnicodeDecodeError:
            data = '???'
        self.ser.close()
        print(data)
'''


class DutEthernet:
    def __init__(self, host='192.168.0.20', port=22, username='root', password=''):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def upload(self, source_folder, source_filename, target_folder):
        source = source_folder + source_filename
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        ssh_client.connect(self.host, self.port, self.username, self.password)
        scpclient = SCPClient(ssh_client.get_transport(), socket_timeout=15.0)
        try:
            scpclient.put(source, target_folder)
        except FileNotFoundError as e:
            print(e)
            print(source_filename + ' is not found. It will be skipped.')
        else:
            print(source_filename + ' upload success!')
        ssh_client.close()

    def download(self, source_folder, source_filename, target_folder):
        source = source_folder + source_filename
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        ssh_client.connect(self.host, self.port, self.username, self.password)
        scpclient = SCPClient(ssh_client.get_transport(), socket_timeout=15.0)
        try:
            scpclient.get(source, target_folder)
        except FileNotFoundError as e:
            print(e)
            print(source_filename + ' is not found. It will be skipped.')
        else:
            print(source_filename + ' upload success!')
        ssh_client.close()
