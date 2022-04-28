import time
from Lib.Basic import LogConfig
from Lib.Driver.Instruments.SignalGenerator import Keysignt_E4438C
LogConfig.init_logger()
testlog = LogConfig.get_logger()

sg = Keysignt_E4438C('TCPIP0::192.168.0.63::inst0::INSTR')

waveform = 'MTONE4_5'


sg.send(r':MMEMory:LOAD:WFM:ALL')
#sg.send(r':MEM:COPY "MTONE4_5","/USER/WAVEFORM/MTONE4_5"')
while(1):
    try:
        sg.send(r':RAD:ARB:WAV "WFM1:{}"'.format(waveform))
        sg.send(r':SOURce:RADio:ARB:STATe ON')
        time.sleep(1)
    except(KeyboardInterrupt):
        break