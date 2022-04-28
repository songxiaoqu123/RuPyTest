# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 11:02:50 2019

@author: EASIXNO
"""
import sys
import pyvisa
import time
import socket
import numpy as np
from Lib.Basic import LoadDataBase, LogConfig
from Lib.TestMethod import IqCalculate

testlog = LogConfig.get_logger()


def load_instrument(instrumentName):  # load json文件，根据每个仪表的name, 在json中查找对应的仪表
    type, address = LoadDataBase.load_instrumentconfig_db(instrumentName)
    instrument = getattr(sys.modules[__name__], type)(address=address)  # 获取json文件中的type名称字符串作为类名，实例化instrument
    testlog.debug('{}{} is loaded.\n'.format(instrument.logHead, instrumentName))
    return instrument


class VisaInstrument:
    def __init__(self, address, name=None, timeout=10):
        self.address = address
        self.name = name
        rm = pyvisa.ResourceManager()
        self.instrument = rm.open_resource(self.address)
        self.instrument.timeout = timeout*1000
        self.logHead = '{:40} |'.format(self.address)
        testlog.debug('{}Initialized.'.format(self.logHead))

    # 发送字符串到仪表
    def send(self, command, opc_timeout=5):
        self.instrument.write(str(command))
        testlog.info('{}SEND  |{}'.format(self.logHead, command))

    def read(self):
        message = self.instrument.read().strip()
        testlog.info('{}READ  |{}'.format(self.logHead, message))
        return message

    def query(self, command, delay=0):
        self.send(command)
        time.sleep(delay)
        message = self.read()
        return message

    def send_binery_values(self, command):
        self.instrument.write_binary_values()
        testlog.info('{}SEND  |{}'.format(self.logHead, command))

    def read_binery_values(self):
        message = self.instrument.read_binary_values()
        testlog.info('{}READ  |{}'.format(self.logHead, message))
        return message

    def query_binery_values(self, command):
        message = self.instrument.query_binary_values(command)
        # testlog.debug('{}SEND  |{}'.format(self.logHead, command)).strip()
        # testlog.debug('{}READ  |{}'.format(self.logHead, message))
        return message

    def reset(self):
        self.send('*CLS')
        self.send('*RST')

    def write_raw(self, command):
        # write byte data
        return self.instrument.write_raw(command)


    def check_opc(self):  # 检查当前动作是否完成， check operation complete
        message = self.query('*OPC?')
        if message == '1':
            testlog.debug('{}Operation complete'.format(self.logHead))
            return True
        else:
            testlog.warning('{}Operation NOT complete'.format(self.logHead))




