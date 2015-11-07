#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, time
from conf import *

class Logger():
    def __init__(self, filename, level = V_INFO):
        self.lev = level
        self.file = open(filename, 'w')


    def warn(self, mess):
        if self.lev >= V_WARN:
            message = "[WARN]{}:{}\n".format(time.time(), mess)
            self.file.write(message)
            self.file.flush()
            os.fsync(self.file)

    def info(self, mess):
        if self.lev >= V_INFO:
            message = "[INFO]{}:{}\n".format(time.time(), mess)
            self.file.write(message)
            self.file.flush()
            os.fsync(self.file)

    def debug(self, mess):
        if self.lev >= V_DEBUG:
            message = "[DBUG]{}:{}\n".format(time.time(), mess)
            self.file.write(message)
            self.file.flush()
            os.fsync(self.file)


def list_to_csv(input):
    return CSV_SEP.join(map(str,input))

def send_data(soc, mess):
    soc.sendall(mess)
    while True:
        data = soc.recv(8)
        if data == SYNC:
            break
        if data == FAIL:
            break
    return data

def recv_data(soc):
    data = soc.recv(4096)
    soc.sendall(SYNC)
    return data



