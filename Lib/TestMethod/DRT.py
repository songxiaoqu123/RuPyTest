from Lib.Basic import LogConfig
from Lib.Driver.Ericsson import RRU
import copy

class DRT():
    def __init__(self, rru, db_prefix=r'/trxCtrl/param/KRC161971_1/R1A/', section='section1', xDpdPerformance=808,
                 dohGainOffset=0, xStability=400, predicate=None, DRT_index=None, DRT_min=-8, DRT_max=15,
                 D_A_deviation_max=8):
        self.db_prefix = db_prefix
        self.section = section
        self.xDpdPerformance = xDpdPerformance
        self.dohGainOffset = dohGainOffset
        self.xStability = xStability
        self.predicate = predicate
        self.DRT_index = DRT_index
        self.DRT_range = range(DRT_min, DRT_max+1)
        self.D_A_deviation_max = D_A_deviation_max
        self.rru = rru
        self.delay_inuse = []
        self.obue_margin_best = -99
        for i in DRT_index:
            data = self.rru.sendWait(r'db list {}{}/xLut{}'.format(self.db_prefix, self.section, i)).split(',')
            a = int(data[1].strip())
            d = int(data[2].strip())
            self.delay_inuse.append([a,d])
        self.delay_best = copy.deepcopy(self.delay_inuse)

    def check_delay_available(self):
        for delay in self.delay_inuse:
            if self.delay_inuse.count(delay)>1:   #保证LUT没有重复项
                return False
            #if delay[0] == delay[1]:
            #    return False
            if abs(delay[0]-delay[1])>self.D_A_deviation_max:
                return False
        return True

    def check_obue_result(self, obue_margin):
        if obue_margin > self.obue_margin_best:
            self.obue_margin_best = obue_margin
            self.delay_best = self.delay_inuse[:]

    def write_to_drt(self):
        #write self.delay_inuse to ru
        for i in range(len(self.DRT_index)):
            self.rru.sendWait(r'db write {}{}/xLut{} 0 {} {} 0 -4500'.format(self.db_prefix, self.section, self.DRT_index[i], self.delay_inuse[i][0], self.delay_inuse[i][1])).split(',')
    '''
    def drt_sweep_1d(self, iter_main = 2,iter_lut = 4):
        for i1 in range(iter_main):
            for j in range(len(self.DRT_index)):
                for i2 in range(iter_lut):
                    pass
    '''





if __name__ == '__main__':
    LogConfig.init_logger()
    testlog = LogConfig.get_logger()
    Com = "COM12"
    rru = RRU.DutSerial(portx=Com, bps=115200, timex=5)
    rru.openCom()

    DRT_index = [1, 2, 3, 4, 5, 6, 7, 9, 10, 11,12,13,14,15]  #LUT0 and LUT8 should always be 0 and not tuned.
    drt = DRT(rru=rru, db_prefix=r'/trxCtrl/param/KRC161971_1/R1A/', section='section1', xDpdPerformance=808, dohGainOffset=0,
              xStability=400, predicate=None, DRT_index=DRT_index, DRT_min=-8, DRT_max=15, D_A_deviation_max=8)
    print(drt.check_delay_available())
    rru.closeCom()