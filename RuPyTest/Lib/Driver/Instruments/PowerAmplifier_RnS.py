import pyvisa
from Lib.Driver.Instruments.Instrument import VisaInstrument
import time




class RnSPowerAmplifier(VisaInstrument):
    def __init__(self, address):
        VisaInstrument.__init__(self, address)
        self.send_termination = '\n'
        self.instrument.set_visa_attribute(pyvisa.constants.VI_ATTR_TERMCHAR, 10)
        self.instrument.set_visa_attribute(pyvisa.constants.VI_ATTR_TERMCHAR_EN, True)

    def set_rf_stat(self, stat, wait_time):
        self.send('RF:OUTP:STAT {}'.format(stat))
        time.sleep(wait_time)

    def set_rf_on(self, wait_time=5):
        if not (self.query_rf_stat()):
            self.send('RF:OUTP:STAT ON')
            time.sleep(wait_time)
            stat = self.query_rf_stat()
            if stat:
                testlog.info('{}PA is turned on!'.format(self.logHead))
            else:
                testlog.error('{}PA turning on FAIL!'.format(self.logHead))
                raise Exception('PA operating mode error!')
        else:
            testlog.warning('{}PA has already been turned on!'.format(self.logHead))

    def set_rf_off(self, wait_time=5):
        if (self.query_rf_stat()):
            self.send('RF:OUTP:STAT OFF')
            time.sleep(wait_time)
            stat = self.query_rf_stat()
            if not stat:
                testlog.info('{}PA is turned off!'.format(self.logHead))

            else:
                testlog.error('{}PA turning off FAIL!'.format(self.logHead))
                raise Exception('PA operating mode error!')
        else:
            testlog.warning('{}PA has already been turned off!'.format(self.logHead))

    def query_rf_stat(self):
        response = self.query('RF:OUTP:STAT?')
        response = int(response)
        if (response == 0):
            return False
        elif (response == 1):
            return True
        else:
            raise Exception('Return Invalid PA state!')


