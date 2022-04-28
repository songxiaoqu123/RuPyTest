import time

from Lib.Basic import LogConfig
from Lib.Driver.Ericsson import RRU

LogConfig.init_logger()
testlog = LogConfig.get_logger()

Com = "COM11"
dutSerial = RRU.DutSerial(portx = Com, bps = 115200, timex = 5)
dutSerial.openCom()


try:
    start_time = time.time()
    with open('RxMonitor.txt', 'w') as f:
        f.write('Rx Noise Floor monitor {}\n'.format(start_time))
    while(True):
        rx_power = dutSerial.get_rxipwr()
        rx_power = rx_power[0]-151.4
        current_time = time.time() - start_time
        with open ('RxMonitor.txt', 'a') as f:
            f.write('{:<30}{:<30}\n'.format(current_time,rx_power))
        time.sleep(0.1)
    dutSerial.closeCom()
except:
    print('error, COM closed')
    dutSerial.closeCom()