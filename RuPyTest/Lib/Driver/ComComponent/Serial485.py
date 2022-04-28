# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import time

import serial
import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu

##########del after debug#########
from Lib.Driver.Instruments import PowerMeter
pm = PowerMeter.PowerMeter('GPIB0::9::INSTR')
pm.reset()
pm.set_dbm()
with open('switch test log.txt','w') as f:
    f.write('{:20}{:20}{:20}\n'.format('repeat', 'PortOn', 'PortOff'))


################################
class Serial485:
    def __init__(self, port="com3", baudrate=9600, bytesize=8, parity='N', stopbits=1 ):
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.master = modbus_rtu.RtuMaster(serial.Serial(port=self.port, baudrate=self.baudrate, bytesize=self.bytesize, parity=self.parity, stopbits=self.stopbits))
        self.master.set_timeout(2.0)
        self.master.set_verbose(True)



    def set_fan_js48_speed(self, slave, speed):
        try:
            read = self.master.execute(slave=slave, function_code=cst.WRITE_SINGLE_REGISTER, starting_address=3, output_value=speed)
            print(read)
        except Exception as exc:
                print(str(exc))
                alarm = (str(exc))
                return alarm  ##如果异常就返回[],故障信息

    def set_electric_relay(self, slave, port, state):
        #port = 0\1, state = 0\1
        if state == 0:
           output_value = 0
        elif state == 1:
            output_value = 65280
        try:
            read = self.master.execute(slave=slave, function_code=cst.WRITE_SINGLE_COIL, starting_address=port, output_value=output_value)
            print(read)
        except Exception as exc:
                print(str(exc))
                alarm = (str(exc))
                return read, alarm  ##如果异常就返回[],故障信息



if __name__ == "__main__":
    ser485 = Serial485()
    #ser485.set_fan_js48_speed(0, 100)
    #ser485.set_fan_js48_speed(1, 100)
    i=0
    while True:
        ser485.set_electric_relay(11, 0, 1)
        time.sleep(0.2)
        ser485.set_electric_relay(11, 0, 0)
        time.sleep(1)
        PortOn = pm.read_power()
        ser485.set_electric_relay(11, 1, 1)
        time.sleep(0.2)
        ser485.set_electric_relay(11, 1, 0)
        time.sleep(1)
        PortOff = pm.read_power()
        with open('switch test log.txt', 'a') as f:
            f.write('{:20}{:20}{:20}\n'.format(i, PortOn, PortOff))
        #ser485.set_fan_js48_speed(0, 100)
        #ser485.set_fan_js48_speed(0, 100)
        print('repeat {} times'.format(i))
        i=i+1

