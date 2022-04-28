from Lib.Driver.Instruments.Instrument import VisaInstrument
import time


class VectorSpectrumAnalyzer(VisaInstrument):
    #def __init__(self, address):
    #    VisaInstrument.__init__(self, address)

    def set_freq_center(self, freq):
        self.send(':SENS:FREQ:CENT {}'.format(freq))

    def set_freq_span(self, freq):
        self.send(':SENS:FREQ:SPAN {}'.format(freq))

    def set_freq_start(self, freq):
        self.send(':SENS:FREQ:START {}'.format(freq))

    def set_freq_stop(self, freq):
        self.send(':SENS:FREQ:STOP {}'.format(freq))

    def set_ref_lev(self, ref_lev):
        self.send(':CALC:STAT:SCAL:X:RLEV {}'.format(ref_lev))

    def set_RBW(self, rbw):
        self.send(':SENSe:BANDwidth:RESolution:AUTO 0')
        self.send(':SENSe:BANDwidth:RESolution {}'.format(rbw))

    def set_att(self, att):
        self.send(':POW:ATT {}'.format(att))


    def set_sweep_time(self, swp_time):
        self.send(':SWE:TIME {} s'.format(swp_time))

    def set_sweep_point(self, num_of_point):
        self.send(':SWE:POIN {}'.format(num_of_point))


    def set_trace_type(self,type_num,trace_num=1):
        trace_type = ['WRITe','AVERage','MAXHold','MINHold']
        self.send(':TRAC{}:TYPE {}'.format(trace_num,trace_type[type_num]))

    def set_detector_type(self,type_num,):
        trace_type = ['AVERage']
        self.send(':DETector:TRACe {}'.format(trace_type[type_num]))
    def set_ave_num(self,average_num=1):
        self.send(':AVERage:COUNt {}'.format(average_num))
#Keysight
    def set_data_format(self, type_number):
        if type_number == 1:
            self.send(':FORMat:DATA REAL,32')
        if type_number == 2:
            self.send(':FORMat:DATA INT,32')
        if type_number == 3:
            self.send(':FORMat:DATA ASCii')
    '''
    #RnS
    def set_data_format(self, type_number):
        if type == 1:
            self.send(':FORM:DATA REAL,32')
        if type == 2:
            self.send(':FORM:DATA INT,32')
        if type == 3:
            self.send(':FORM:DATA ASCII,32')
    '''
    def get_trace(self):
        try:
            self.send(':INIT:CONT 0')
            self.send(':INIT:IMM')
            return self.query(':FETCh:SAN1?')
        except:
            self.get_trace()

    def set_mode(self, mode_index, meas_index):
        mode = {0: "NR5G", 1: "VSA89601", 2: "ADEMOD", 3: "AVIONIC", 4: "BTooth", 5: "CQM", 6: "EMI", 7: "EDGEGSM",
                8: "BASIC", 9: "LTEAFDD", 10: "LTEATDD", 11: "MRECEIVE", 12: "MSR", 13: "NFIGure", 14: "PNOISE",
                15: "PA", 16: "PULSEX", 17: "RTS", 18: "RTSA", 19: "RLC", 20: "SCPILC", 21: "SEQAN", 22: "SRCOMMS",
                23: "SA", 24: "VMA", 25: "WCDMA"}
        meas = {0: "SAN", 1: "CHP", 2: "OBW", 3: "ACP", 4: "PST", 5: "TXP", 6: "SPUR", 7: "SEM", 8: "LIST"}
        self.send(':INSTrument:CONFigure:{}:{}'.format(mode[mode_index], meas[meas_index]))

    def set_CCDF_stat(self, stat):
        self.send(':CALC:STAT:CCDF:STAT {}'.format(stat))

    def get_CCDF(self, form='CFAC'):
        self.send(':CALC:STAT:RES? {}'.format(form))
        return float(self.instrument.read())

    def init(self):
        #self.send(':INIT:')
        self.send(':INIT:CONT 0')
        self.send(':INIT:IMM')

    def set_sem_mask(self, mask):
        start_freq = ''
        stop_freq = ''
        start_limit = ''
        stop_limit = ''
        rbw = ''
        for sub_mask in mask:
            start_freq = start_freq + ' {}'.format(sub_mask[0])
            stop_freq = stop_freq + ' {}'.format(sub_mask[1])
            start_limit = start_limit + ' {}'.format(sub_mask[2])
            stop_limit = stop_limit + ' {}'.format(sub_mask[3])
            rbw = rbw + ' {}'.format(sub_mask[4])
            
        self.send('SEM:OFFS:LIST:FREQ:STAR {}'.format(start_freq))
        self.send('SEM:OFFS:LIST:FREQ:STOP {}'.format(start_freq))
        self.send('SEM:OFFS:LIST:STAR:ABS {}'.format(start_freq))
        self.send('SEM:OFFS:LIST:STOP:ABS {}'.format(start_freq))
        self.send('SEM:OFFS:LIST:FREQ:STAR {}'.format(start_freq))


if __name__ == '__main__':
    vsa = VectorSpectrumAnalyzer(address='TCPIP0::192.168.0.22::hislip0::INSTR')
    print(vsa.query('*IDN?'))
    vsa.set_mode(0,0)

    '''
    #Fetch Spectrum
    vsa.set_data_format(1)  # ASCii
    vsa.send(':FORMat:BORDer NORMal')
    vsa.send(':FETCh:SAN1?')
    data = vsa.instrument.read_binary_values(is_big_endian=True)
    print(data)
    '''