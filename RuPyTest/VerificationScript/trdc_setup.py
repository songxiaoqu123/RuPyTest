from Lib.Driver.Ericsson import RRU
from Lib.Basic import LogConfig

LogConfig.init_logger()
testlog = LogConfig.get_logger()


Com = "COM12"
ru = RRU.DutSerial(portx = Com, bps = 115200, timex = 5)
ru.openCom()

trdc_command = ru.trdc_single_carrier(crFreq=772e6)
print(trdc_command)
ru.sendWait(trdc_command)
ru.sendWait('trdc on 1')

ru.closeCom()
