import logging
import os
import sys
import time
defaultFileName = 'TestLog'
defaultPath = r'C:\RuPyTestLog\Logs'
defaultLogger = 'testlog'

def init_logger(fileName = defaultFileName, logPath = defaultPath):
    if not os.path.exists(logPath):         #如果log文件存放路径不存在，则创建路径， 如果log文件已存在，且logClear = True, 则先删除文件
        os.mkdir(logPath)
    time_str = time.strftime("%Y%m%d%H%M%S", time.localtime())
    fileName = logPath + '\\' + fileName + time_str + '.log'



    testlog = logging.getLogger(defaultLogger)
    testlog.setLevel(level=logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level=logging.DEBUG)
    console_formatter = logging.Formatter('%(levelname)-8s | %(message)s')
    console_handler.setFormatter(console_formatter)
    testlog.addHandler(console_handler)

    file_handler = logging.FileHandler(fileName)
    file_handler.setLevel(level=logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)-25s|%(levelname)-8s|%(message)s')
    file_handler.setFormatter(file_formatter)
    testlog.addHandler(file_handler)

    testlog.debug("Test log initialized.\n")

def get_logger(logger = defaultLogger):
    testlog = logging.getLogger(logger)
    return testlog

