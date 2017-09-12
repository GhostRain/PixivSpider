# -*- coding:utf-8 -*-
import win32api
import os
import sys
from dbHelper import dbHelper

def on_close(sig):
	os.chdir(sys.path[0])
	f = open('cache.dat', 'wb')
	imgIDList = []
	imgIDList.append(1)
	imgIDList.append(2)
	imgIDList.append(3)
	imgIDList.append(4)
	f.write(','.join(map(str,imgIDList)))
	f.close()

win32api.SetConsoleCtrlHandler(on_close, True)
on_close(1)
raw_input()