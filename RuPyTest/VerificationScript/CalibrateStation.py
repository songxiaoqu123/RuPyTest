import time
from Lib.Basic import LogConfig
from Lib.Driver import Instruments
from Lib.Driver.Instruments.SignalGenerator import Keysignt_E4438C
LogConfig.init_logger()
testlog = LogConfig.get_logger()

'''
第一步校准信号源输出口功率，将RefFileName设为None, OutputFileName 设为比如‘SG_OUTP.txt’ 此时输出一个信号源输出值
第二部将RefFileName设为‘SG_OUTP.txt’， 校准其他各个路径


'''

OutputFileName = 'SG1_RXA_1.txt'
PathName = 'SG1_RXA_1'
#OutputFileName = 'A_VSA.txt'
#OutputFileName = 'SG_A.txt'

RefFileName = 'SG1_Power_0.txt'  #if ==None, cal SG output power

sg = Keysignt_E4438C('TCPIP0::192.168.0.63::inst0::INSTR')
#vsa = Keysignt_N9020('TCPIP0::192.168.0.83::hislip0::INSTR')
pm = Instruments.load_instrument('PM')



frequency_range = range(600000000, 2300000000, 10000000)
pm.set_dbm()
pm.set_offset(0)
sg.set_amp(0)
sg.set_rf_state(state='ON',delay=1)

Path_loss = []


for f in frequency_range:
    sg.set_freq(f)
    time.sleep(3)
    power = pm.read_power()
    Path_loss.append(power)

if RefFileName:
    with open(RefFileName, 'r') as rf:
        Path_loss_Ref = rf.readlines()
    with open(OutputFileName, 'w') as f:
        f.write('Calibration data for signal path:  {}\n'.format(PathName))
        f.write('-------------------------------------------\n')
        f.write('edit by easixno\n')
        f.write('-------------------------------------------\n')
        for i in range(len(frequency_range)):
            Path_loss[i] = Path_loss[i] - float(Path_loss_Ref[i])
            f.write('({}, {})\n'.format(frequency_range[i], Path_loss[i]))


else:
    with open(OutputFileName, 'w') as f:
        for i in range(len(frequency_range)):
            f.write('{}\n'.format(Path_loss[i]))