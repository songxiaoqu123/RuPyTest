import time
from Lib.Basic import LogConfig
from Lib.Driver.Instruments import VectorSpectrumAnalyser

LogConfig.init_logger()
testlog = LogConfig.get_logger()


vsa = VectorSpectrumAnalyser.VectorSpectrumAnalyzer('TCPIP0::192.168.0.21::inst0::INSTR')
vsa.set_freq_center(1e9)
vsa.check_opc()
