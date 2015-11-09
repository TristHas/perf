#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, time
from conf import *

class Logger():
    def __init__(self, filename, level = V_INFO, real_time = True):
        self.lev = level
        self.file = open(filename, 'w')
        self.real_time = real_time

    def warn(self, mess):
        if self.lev >= V_WARN:
            message = "[W]{}:{}\n".format(time.time(), mess)
            self.file.write(message)
            if self.real_time:
                self.file.flush()
                os.fsync(self.file)

    def info(self, mess):
        if self.lev >= V_INFO:
            message = "[I]{}:{}\n".format(time.time(), mess)
            self.file.write(message)
            if self.real_time:
                self.file.flush()
                os.fsync(self.file)

    def verb(self, mess):
        if self.lev >= V_VERBOSE:
            message = "[V]{}:{}\n".format(time.time(), mess)
            self.file.write(message)
            if self.real_time:
                self.file.flush()
                os.fsync(self.file)

    def debug(self, mess):
        if self.lev >= V_DEBUG:
            message = "[D]{}:{}\n".format(time.time(), mess)
            self.file.write(message)
            if self.real_time:
                self.file.flush()
                os.fsync(self.file)

def list_to_csv(input):
    return CSV_SEP.join(map(str,input))

def send_data(soc, mess):
    soc.sendall(mess)
    while True:
        print 'send_data has sent'
        data = soc.recv(8)
        print 'send_data has received'
        if data == SYNC:
            break
        if data == FAIL:
            break
    print 'send_data returning {}'.format(data)
    return data

def recv_data(soc):
    print 'recv data will receive'
    data = soc.recv(4096)
    print 'recv data has received'
    soc.sendall(SYNC)
    print 'recv data has sent'
    return data




