from Lib.Driver.Instruments.Instrument import VisaInstrument
import time



class PowerMeter(VisaInstrument):
    #def __init__(self, address):
        #VisaInstrument.__init__(self, address)

    def set_freq(self, freq):
        self.send('FREQ {freq}'.format(freq=freq))

    def set_dbm(self):
        self.send('UNIT:POW DBM')

    def set_offset(self, offset):
        self.send('UNIT:POW DBM')
        self.send('CORR:OFFS:STAT ON')
        self.send('CORR:OFFS {offset}'.format(offset=offset))

    def read_power(self):
        self.send('SENSe:POWer:AVG:FAST ON')
        self.send('INIT')
        power = float(self.instrument.query('FETCH?'))
        return (power)

