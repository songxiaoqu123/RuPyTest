from Lib.Driver.Instruments.Instrument import VisaInstrument
import time




class PowerSourceUnit(VisaInstrument):
    def __init__(self, address):
        VisaInstrument.__init__(self, address)

    def set_voltage(self, voltage, channel=0):
        if channel == 0:
            self.send('VOLT {voltage}'.format(voltage=voltage))
        else:
            self.send('VOLT {voltage},(@{channel})'.format(voltage=voltage, channel=channel))

    def set_current(self, current, channel=0):
        if channel == 0:
            self.send('CURR {current}'.format(current=current))
        else:
            self.send('CURR {current},(@{channel})'.format(current=current, channel=channel))

    def set_volt_curr(self, channel=0, voltage=None, current=None):
        if voltage:
            if channel == 0:
                self.send('VOLT {voltage}'.format(voltage=voltage))
            else:
                self.send('VOLT {voltage},(@{channel})'.format(voltage=voltage, channel=channel))
        if current:
            if channel == 0:
                self.send('CURR {current}'.format(current=current))
            else:
                self.send('CURR {current},(@{channel})'.format(current=current, channel=channel))

    def read_current(self, channel=0):
        if channel == 0:
            self.send('MEAS:CURR?')
        else:
            self.send('MEAS:CURR? (@{channel})'.format(channel=channel))
        return float(self.read())

    def read_voltage(self, channel=0):
        if channel == 0:
            self.send('MEAS:VOLT?')
        else:
            self.send('MEAS:VOLT? (@{channel})'.format(channel=channel))
        return float(self.read())

    def set_output(self, state, channel=0, before_delay=0, after_delay=0):
        time.sleep(before_delay)
        if channel == 0:
            self.send('OUTP {state}'.format(state=state))
        else:
            self.send('OUTP {state},(@{channel})'.format(state=state, channel=channel))
        time.sleep(after_delay)
