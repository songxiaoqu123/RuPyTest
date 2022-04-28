with open ('E:\RuPyTest\WaveForm\LteWarp3p0_10G_T14.cdl3','rb') as f:
    with open ('E:\RuPyTest\WaveForm\LteWarp3p0_10G_T14.txt','w') as g:
        data = f.read()
        g.write(str(data))