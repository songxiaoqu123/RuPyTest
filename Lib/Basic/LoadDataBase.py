import json
from Lib.Basic import LogConfig

testlog = LogConfig.get_logger()

def load_instrumentconfig_db(instrumentName):  # load json文件，根据每个仪表的name, 在json中查找对应的仪表
    with open('../../Config/InstrumentConfig.json', 'r') as f:
        jsonDict = json.load(f)
    instrumentsList = jsonDict['Instruments']
    for instrumentDict in instrumentsList:
        if instrumentName == instrumentDict['name']:  # 根据仪表name搜寻仪表
            testlog.debug('{} is found in instrument db.\n'.format(instrumentName))
            return instrumentDict['type'], instrumentDict['address']
    testlog.error('Instrument name: {} not found.'.format(instrumentName))
    raise Exception('Instrument name not found')

def load_testconfig_db():
    with open('../../Config/TestConfig.json', 'r') as f:
        jsonDict = json.load(f)
    return jsonDict

def load_switchboxconfig_db():
    with open('../../Config/SwitchBoxConfig.json', 'r') as f:
        jsonDict = json.load(f)
    switches = jsonDict['switches']
    paths = jsonDict['paths']
    # transform switches to form like "K1[0006,0007]"
    switches_transformed = {}
    for switch in switches:
        switches_transformed[switch['name']] = switch['channels'].split(',')
    # transform paths to form like "RESET[0006,0024,0035,0044]"
    paths_transformed = {}
    for path in paths:
        paths_transformed[path['name']] = []
        for k in path['positions'].split(';'):
            k = k.split('=')
            k[1] = int(k[1])
            k = switches_transformed[k[0]][k[1] - 1]
            paths_transformed[path['name']].append(k)
    return paths_transformed

