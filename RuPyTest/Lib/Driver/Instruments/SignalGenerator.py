from Lib.Driver.Instruments.Instrument import VisaInstrument
import time


class SignalGenerator(VisaInstrument):
    #def __init__(self, address):
        #VisaInstrument.__init__(self, address)

    def set_freq(self, freq, port=1):
        self.send('SOUR{port}:FREQ {freq}'.format(port=port, freq=freq))

    def set_amp(self, amp=-100.0, port=1):
        self.send("SOUR{port}:POWer:LEVel:IMM:AMPL {amp}".format(port=port, amp=amp))

    def set_waveform(self, wavefile, port=1):
        self.send('SOUR{0}:BB:ARB:PRES'.format(port))
        self.send(r'SOURce{0}:BB:ARBitrary:WAVeform:SELect "{1}"'.format(port, wavefile))
        self.send("SOURce{0}:BB:ARB:STAT ON".format(port))

    def set_sample_rate(self, sample_rate, port=1):
        self.send("SOURce{0}:BB:ARB:CLOC {1}".format(port, sample_rate))

    def set_rf_state(self, state, port=1, delay=0):
        self.send('OUTP{port}:STAT {state}'.format(port=port, state=state))
        time.sleep(delay)

    def write_binary_stream(self, command, bin_data):
        # input command and binary data block, the '#' is included in the function
        data_len = len(bin_data)
        len_data_len = len(f'{data_len}')
        command_header = f'{command}#{len_data_len}{data_len}'.encode('ascii')
        self.write_raw(command_header + bin_data)

    def write_binary_file(self, filename, bin_data):
        self.write_binary_stream(command=f"MMEM:DATA '{filename}',", bin_data=bin_data)
