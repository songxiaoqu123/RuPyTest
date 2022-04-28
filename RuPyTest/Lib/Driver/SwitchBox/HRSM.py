# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 13:38:35 2021

@author: DACE-NJRD-Station1
"""

import win32gui
import win32con
import win32api
from pywinauto.application import Application
import time
# 从顶层窗口向下搜索主窗口，无法搜索子窗口
# FindWindow(lpClassName=None, lpWindowName=None)  窗口类名 窗口标题名



class HRSM:
    def __init__(self):
        self.app =Application().connect(title_re="汉瑞微波开关矩阵测试.*", class_name ='WindowsForms10.Window.8.app.0.141b42a_r7_ad1' ) 
        self.appWindow = self.app.window(title='汉瑞微波开关矩阵测试')
        self.send_command_button = self.appWindow.Button23
        self.X1 = self.appWindow['X1接口']
        self.X2 = self.appWindow['X2接口']
        self.X3 = self.appWindow['X3接口']
        self.X4 = self.appWindow['X4接口']
        self.X5 = self.appWindow['X5接口']
        self.X6 = self.appWindow['X6接口']
        self.X7 = self.appWindow['X7接口']
        self.X8 = self.appWindow['X8接口']
        self.K1 = (self.X1.Button1, self.X1.Button7, self.X1.Button6, self.X1.Button5, self.X1.Button4, self.X1.Button3, self.X1.Button2)
        self.K2 = (self.X2.Button1, self.X2.Button7, self.X2.Button6, self.X2.Button4, self.X2.Button5, self.X2.Button3, self.X2.Button2)
        self.K3 = (self.X3.Button1, self.X3.Button3, self.X3.Button2)
        self.K4 = (self.X4.Button1, self.X4.Button2, self.X4.Button3)
        self.K5 = (self.X5.Button1, self.X5.Button2, self.X5.Button3)
        self.K6 = (self.X6.Button1, self.X6.Button2, self.X6.Button3)
        self.K7 = (self.X7.Button1, self.X7.Button2, self.X7.Button3)
        self.K8 = (self.X8.Button1, self.X8.Button2, self.X8.Button3)
        self.path1 = []
        self.path2 = []
        self.path1.append([1, 6, 1, 0, 0, 0, 0, 1])
        self.path1.append([1, 6, 2, 0, 0, 0, 0, 1])
        self.path1.append([2, 6, 0, 1, 0, 0, 0, 1])
        self.path1.append([2, 6, 0, 2, 0, 0, 0, 1])
        self.path1.append([3, 6, 0, 0, 1, 0, 0, 1])
        self.path1.append([3, 6, 0, 0, 2, 0, 0, 1])
        self.path1.append([4, 6, 0, 0, 0, 1, 0, 1])
        self.path1.append([4, 6, 0, 0, 0, 2, 0, 1])
        self.path1.append([5, 6, 0, 0, 0, 0, 1, 1])
        self.path1.append([5, 6, 0, 0, 0, 0, 2, 1])
        self.path1.append([6, 6, 0, 0, 0, 0, 0, 1])
        self.path1.append([6, 1, 2, 0, 0, 0, 0, 2])
        self.path2.append([6, 1, 2, 0, 0, 0, 0, 2])
        self.path2.append([6, 1, 1, 0, 0, 0, 0, 2])
        self.path2.append([6, 2, 0, 2, 0, 0, 0, 2])
        self.path2.append([6, 2, 0, 1, 0, 0, 0, 2])
        self.path2.append([6, 3, 0, 0, 2, 0, 0, 2])
        self.path2.append([6, 3, 0, 0, 1, 0, 0, 2])
        self.path2.append([6, 4, 0, 0, 0, 2, 0, 2])
        self.path2.append([6, 4, 0, 0, 0, 1, 0, 2])
        self.path2.append([6, 5, 0, 0, 0, 0, 2, 2])
        self.path2.append([6, 5, 0, 0, 0, 0, 1, 2])
        self.path2.append([6, 6, 0, 0, 0, 0, 0, 2])
        self.path2.append([1, 6, 1, 0, 0, 0, 0, 1])






    def set_path(self, path_list):
        if len(path_list)!=8:
            raise Exception('Path should have 8 element!')
        self.appWindow.restore()
        self.K1[path_list[0]].click()
        self.K2[path_list[1]].click()
        self.K3[path_list[2]].click()
        self.K4[path_list[3]].click()
        self.K5[path_list[4]].click()
        self.K6[path_list[5]].click()
        self.K7[path_list[6]].click()
        self.K8[path_list[7]].click()
        self.appWindow.set_focus()
        self.send_command_button.click(coords=(10, 10))
        self.send_command_button.click(coords=(10, 10))
        #self.send_command_button.print_control_identifiers()  


if __name__ == '__main__':
    switch_matrix = HRSM()
    switch_matrix.set_path(switch_matrix.path1[0])