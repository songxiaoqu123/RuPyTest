from Lib.Driver.Instruments.VectorSpectrumAnalyser import VectorSpectrumAnalyzer
import time
from Lib.Basic import LogConfig
testlog = LogConfig.get_logger()

class VectorSpectrumAnalyzer(VectorSpectrumAnalyzer):
    def read_binery_values(self):
        message = self.instrument.read_binary_values(is_big_endian=True)
        testlog.info('{}READ  |{}'.format(self.logHead, message))
        return message


    def set_ext_gain_BTS(self, gain):
        self.send(':CORR:BTS:GAIN {}'.format(gain))


    def get_trace(self):
        try:
            self.set_data_format(1)
            self.send(':INIT:CONT 0')
            self.send(':INIT:IMM')
            self.send(':FETCh:SAN1?')
            return self.read_binery_values()
        except:
            self.get_trace()

    def get_evm(self):
        try:
            self.set_data_format(3)
            self.send(':INIT:CONT 0')
            self.send(':INIT:IMM')
            self.send(':FETCh:EVM?')
            data = self.read()
            data = data.split(',')
            result = {'Power':float(data[0]), 'EVM_rms':float(data[1]),'EVM_peak':float(data[2]), 'Freq_err':float(data[3]), 'syb_clock_err':float(data[4]), 'IQ_offset':float(data[5])}
            return result
        except:
            self.get_evm()

    def get_acp(self):
        try:
            self.set_data_format(3)
            self.send(':INIT:CONT 0')
            self.send(':INIT:IMM')
            self.send(':FETCh:ACP?')
            data = self.read()
            data = data.split(',')
            result = {'Power': float(data[1]), 'ACLR1_L': float(data[4]), 'ACLR1_R': float(data[6]),'ACLR2_L': float(data[8]), 'ACLR2_R': float(data[10])}
            return result
        except:
            self.get_acp()

if __name__ == '__main__':
    vsa = VectorSpectrumAnalyzer(address='TCPIP0::192.168.0.22::hislip0::INSTR')
    print(vsa.query('*IDN?'))
    vsa.send('*RCL 1')
    vsa.set_freq_center(2120e6)
    vsa.set_ext_gain_BTS(-35)
    print(vsa.get_acp())
    vsa.send('*RCL 2')
    vsa.set_freq_center(2120e6)
    vsa.set_ext_gain_BTS(-35)
    print(vsa.get_evm())


'''
    vsa = VectorSpectrumAnalyzer(address='TCPIP0::192.168.0.22::hislip0::INSTR')
    print(vsa.query('*IDN?'))
    vsa.set_data_format(1)  # ASCii
    vsa.send(':FORMat:BORDer NORMal')
    vsa.send(':FETCh:SAN1?')
    data = vsa.instrument.read_binary_values(is_big_endian=True)
    print(data)
'''