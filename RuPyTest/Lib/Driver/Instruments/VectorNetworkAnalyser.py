from Lib.Driver.Instruments.Instrument import VisaInstrument
import time



class VectorNetworkAnalyzer(VisaInstrument):
    def __init__(self, address):
        VisaInstrument.__init__(self, address)

    def load_state(self, file_name):
        self.send('MMEM:LOAD \'{}\''.format(file_name))

    def set_rf_state(self, state):
        self.send('OUTP {}'.format(state))
        time.sleep(0.1)
        self.send('INITiate:CONTinuous OFF')

    def set_power(self, power, channel=1):
        self.send('SOUR:POW{} {}'.format(channel, power))

    def set_freq(self, start, stop, step, channel=1):
        self.send('SENS{}:FREQ:STAR {}'.format(channel, start))
        self.send('SENS{}:FREQ:STOP {}'.format(channel, stop))
        self.send('SENS{}:SWE:STEP {}'.format(channel, step))

    def read_S_parameter(self, port_to, port_from):
        self.send('CALC:PAR:DEL:ALL')
        self.send('CALCulate1:PARameter:DEFine:EXT \'MyMeas\',\'S{}{}\''.format(port_to, port_from))
        self.send('DISPlay:WINDow1:TRACe1:FEED \'MyMeas\'')
        time.sleep(0.2)
        self.send('INITiate:IMMediate;*wai')
        self.send('FORMat:DATA ascii')
        self.send('CALCulate:DATA? SDATA')
        data = self.instrument.read()
        data = data.split(',')
        for i in range(len(data)):
            data[i] = float(data[i])
        data = np.array(data[0::2]) + 1j * np.array(data[1::2])
        data = IqCalculate.to_log10(data)
        return data


