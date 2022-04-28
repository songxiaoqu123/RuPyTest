import win32api
import win32con
import win32gui
from ctypes import *
import time

def mouse_move(x,y):
    windll.user32.SetCursorPos(x, y)

def mouse_click(x=None,y=None):
    if not x is None and not y is None:
        mouse_move(x,y)
        time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

def mouse_dclick(x=None,y=None):
    if not x is None and not y is None:
        mouse_move(x,y)
        time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

time.sleep(5)
mouse_click(656,165)      #click "Measure"


time.sleep(5)
mouse_click(589,74)       #click "Rx_Delay"


time.sleep(5)
mouse_click(592,105)      #click "OK"


time.sleep(5)
mouse_click(1249,846)     #click "OK"

'''
win32api.keybd_event(0x0D, 0, 0, 0)
win32api.keybd_event(0x0D, 0, win32con.KEYEVENTF_KEYUP, 0)
'''

time.sleep(5)
mouse_click(486,432)      #click "OK"


time.sleep(5)
mouse_dclick(377,167)      #double click and choose PIS

time.sleep(5)
mouse_dclick(473,612)      #double click and choose PIS
time.sleep(5)
mouse_click(418,660)      #click "Reset"