from Lib.Basic import LogConfig
from Lib.Driver.Ericsson import RRU

LogConfig.init_logger()
testlog = LogConfig.get_logger()




Com = "COM11"
dutSerial = RRU.DutSerial(portx = Com, bps = 115200, timex = 5)
dutSerial.openCom()


try:
    #while(True):
    dutSerial.sendWait(r'gc stop')
    dutSerial.sendWait(r'fui set gain 4 -23')
        #dutSerial.sendWait(r'fui set gain 2 -9')
        #dutSerial.sendWait(r'fui set gain 3 -9')
        #dutSerial.send(r'fui set gain 4 -9')
        #time.sleep(0.1)


    dutSerial.closeCom()
except:
    print('error, COM closed')
    dutSerial.closeCom()