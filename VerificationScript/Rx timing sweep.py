from Lib.Basic import LogConfig
from Lib.Driver.Ericsson import RRU

LogConfig.init_logger()
testlog = LogConfig.get_logger()




Com = "COM12"
dutSerial = RRU.DutSerial(portx = Com, bps = 115200, timex = 5)
dutSerial.openCom()


try:
    '''
    dutSerial.sendWait(r'db prod copy /7xx/id_ruType_1.25.x/ul/rf_bA/rfPortToSmgCpriI2SubDelay')
    dutSerial.sendWait(r'db write /7xx/id_ruType_1.25.x/ul/rf_bA/rfPortToSmgCpriI2SubDelay 89190')
    dutSerial.sendWait(r'db prod copy /7xx/id_ruType_1.25.x/ul/rf_bB/rfPortToSmgCpriI2SubDelay')
    dutSerial.sendWait(r'db write /7xx/id_ruType_1.25.x/ul/rf_bB/rfPortToSmgCpriI2SubDelay 89190')
    dutSerial.sendWait(r'db prod copy /nrFdd300_Id14/ulSubbandTime')
    dutSerial.sendWait(r'db resize /nrFdd300_Id14/ulSubbandTime 2')
    dutSerial.sendWait(r'db write /nrFdd300_Id14/ulSubbandTime 100 298')
    dutSerial.sendWait(r'db resize /ul/nrFdd300_Id14/ulDelayDelta 2')
    dutSerial.sendWait(r'db prod copy /ul/nrFdd300_Id14/ulDelayDelta')
    dutSerial.sendWait(r'db resize /ul/nrFdd300_Id14/ulDelayDelta 2')
    dutSerial.sendWait(r'db write /ul/nrFdd300_Id14/ulDelayDelta 353 0')
    '''


    dutSerial.sendWait(r'te log clear')
    dutSerial.sendWait(r'te enable all TIME_ALIGNMENT_UL')
    dutSerial.sendWait(r'te enable all RX_TA')
    dutSerial.sendWait(r'te e trace1 trace2 RX_AGC')
    dutSerial.sendWait(r'te enable all UL_SUBBAND')
    dutSerial.sendWait(r'te e trace3 RX_TA')
    dutSerial.sendWait(r'te save *')






    #dutSerial.sendWait(r'db write /nrFdd400_Id7/ulSubbandTime 118 517')
    #dutSerial.sendWait(r'db write /ul/nrFdd400_Id7/ulDelayDelta -25360 0')




    dutSerial.closeCom()
except:
    print('error, COM closed')
    dutSerial.closeCom()