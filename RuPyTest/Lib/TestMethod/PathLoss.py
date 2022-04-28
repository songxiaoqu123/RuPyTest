import numpy as np
import os

class PathLoss():
    def __init__(self, port_from, port_to):
        self.folder = 'C:\RuPyTestConfig\RuPyPathLoss'
        self.port_from = port_from
        self.port_to = port_to


    def get_raw_pathloss(self):
        filename = '{}\\{}_{}.txt'.format(self.folder, self.port_from, self.port_to)
        with open(filename, 'r') as f:
            data = f.readlines()
            freq = []
            insertion_loss = []
        for i in range(len(data)):
            data[i] = data[i].strip('\n').strip('(').strip(')').split(',')
            freq.append(data[i][0])
            insertion_loss.append(data[i][1])
        freq = np.array(freq, dtype=float)
        insertion_loss = np.array(insertion_loss, dtype=float)
        return freq, insertion_loss

    def get_path_loss(self, freq):
        freq_raw, il_raw = self.get_raw_pathloss()
        return np.interp(freq, freq_raw, il_raw)


if __name__ == '__main__':
    path_loss = PathLoss(folder='.', port_from='TXA', port_to='SPEC')
    f = [800.12545e6, 801.1554e6]
    il = path_loss.get_path_loss(f)
    print(il)

# power = np.interp(freq, freq_arr, power_arr)
