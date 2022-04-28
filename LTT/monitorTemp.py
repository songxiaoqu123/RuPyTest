import time
from Lib.Basic import LogConfig
from Lib.Driver.Ericsson import RRU

LogConfig.init_logger()
testlog = LogConfig.get_logger()
from Lib.Driver.ComComponent import Serial485

########Tset Setup######################################################

heat_time = 30
cool_time = 30


dut = RRU.DutSerial(portx="COM11", bps=115200, timex=5)

with open('Logs\\Temperature.txt', 'w') as f:
    dut.openCom()
    f.write('\n')
    f.write('{:20}{:20}{:20}{:20}{:20}{:20}{:20}{:20}{:20}{:30}'.format('Sample', 'Cycle', 'State', 'Tx-norm', 'TxPower', 'TxDeltaPower', 'Rx-norm', 'RxPower', 'RxDeltaPower', 'StartTime'))

    ts_data = dut.get_ts()
    for d in ts_data[0::2]:
        d = 'ts-{}(C)'.format(d)
        f.write('{:20}'.format(d))
    vs_data = dut.get_vs()
    for d in vs_data[0::2]:
        d = 'vs-{}(V)'.format(d)
        f.write('{:20}'.format(d))
    cs_data = dut.get_cs()
    for d in cs_data[0::2]:
        d = 'cs-{}(A)'.format(d)
        f.write('{:20}'.format(d))
    rvc_data = dut.get_rvc()
    for d in rvc_data[0::2]:
        d = 'rvc-{}'.format(d)
        f.write('{:30}'.format(d))
    txpower_data = dut.get_trxpower(port=0)
    for d in txpower_data[0:-2:2]:
        d = 'TxPower-{}'.format(d)
        f.write('{:40}'.format(d))
    dut.closeCom()
    f.write('\n')
#########StartTest###################################################

state = "Cooling"
fans = Serial485.Serial485()
start_time = time.time()

while(time.time() - start_time < heat_time + cool_time):
    if (time.time() - start_time < heat_time) & (state == 'Cooling'):
        state = 'Heating'
        fans.set_fan_js48_speed(0, 0)
        dut.openCom()
        for j in range(2):
            dut.sendWait('trdc on {}'.format(j+1))
        dut.closeCom()
        time.sleep(5)

    if (time.time() - start_time > heat_time) & (state == 'Heating'):
        state = 'Cooling'
        fans.set_fan_js48_speed(0, 100)
        dut.openCom()
        for j in range(2):
            dut.sendWait('trdc off {}'.format(j+1))
        dut.closeCom()
        time.sleep(5)

    with open('Logs\\Temperature.txt', 'a') as f:

        test_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f.write('{: <20d}{: <20d}{:20}{: <20f}{: <20f}{: <20f}{: <20f}{: <20f}{: <20f}{:30}'.format(0, 0, state, 0, 0, 0, 0, 0, 0, test_time))


        ts_data = dut.get_ts()
        for d in ts_data[1::2]:
            d = d[:-1]
            d = '{}'.format(d)
            f.write('{:20}'.format(d))
        vs_data = dut.get_vs()
        for d in vs_data[1::2]:
            d = d[:-1]
            d = '{}'.format(d)
            f.write('{:20}'.format(d))
        cs_data = dut.get_cs()
        for d in cs_data[1::2]:
            d = d[:-1]
            d = '{}'.format(d)
            f.write('{:20}'.format(d))
        rvc_data = dut.get_rvc()
        for d in rvc_data[1::2]:
            d = '{}'.format(d)
            f.write('{:30}'.format(d))
        txpower_data = dut.get_trxpower(port=0)
        for d in txpower_data[1:-1:2]:
            d = d.strip(',')
            d = '{}'.format(d)
            f.write('{:40}'.format(d))

        f.write('\n')
    dut.closeCom()

time.sleep(5)
