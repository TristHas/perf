#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conf import *
import threading, socket, time
import json
import os

class DataManager(object):
    def __init__(self, adict, cpu):
        self.step = adict['step']
        self.timeout = int(adict['timeout'] / self.step)

        self.run = True
        self.local_store = False
        self.keep_going = True

        self.files = dict()
        self.targets = ['system'] + adict['processes']
        self.receivers = []

        self.thr_start = threading.Thread(target = self.processing, name = 'data managing', args =(cpu,), kwargs=adict)
        self.thr_start.start()

        self.sys_headers = cpu.sys_headers
        self.proc_headers = cpu.proc_headers


    def processing(self, *args, **adict):
        while self.run:
            cpu = args[0]
            data = cpu.transmit.get()
            if self.local_store:
                self.process_local(data)
            for socket in self.receivers:
                self.process_send(socket, data)

    def quit(self):
        self.run = False

    def start_send(self):
        self.data_thr = threading.Thread(target = self.init_send, name = 'init_send_data', args = ())
        self.data_thr.start()

    def init_send(self):
        soc_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc_data.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc_data.bind((SOC_ADR_REMOTE, SOC_PORT_DATA))
        soc_data.listen(1)
        connection, client_address = soc_data.accept()
        self.receivers.append(connection)
        dico = {}
        for keys in self.targets:
            if keys == 'system':
                dico[keys] = self.sys_headers
            else:
                dico[keys] = self.proc_headers
        mess = json.dumps(dico)
        print 'sending {}'.format(mess)
        send_data(connection, mess)



    def stop_send(self):
        tmp = self.receivers
        self.receivers = []
        for elem in tmp:
            elem.close()

    def process_send(self, connection, data):
        mess = json.dumps(data)
        send_data(connection, mess)

    def stop_local(self):
        self.local_store = False
        for key in self.files:
            self.files[key].close()

    def start_local(self):
        # Make record dir
        directory = os.path.join(NAO_DATA_DIR, time.ctime())
        os.makedirs(directory)

        # Open files
        for key in self.targets:
            filename = os.path.join(directory, key)
            self.files[key] = open(filename, 'w')
        for key in self.files:
            if key == 'system':
                print >> self.files[key], list_to_csv(self.sys_headers)
            else:
                print >> self.files[key], list_to_csv(self.proc_headers)
        self.local_store = True

    def process_local(self, tmp):
        if tmp == 'end':
            self.local_store = False
            for key in self.files:
                self.files[key].close()
        else:
            for key in self.files:
                if key != 'system':
                    tmp_proc = {}
                    tmp_proc[key] = [tmp[key][dic_key] for dic_key in self.proc_headers]
                    print >> self.files[key], list_to_csv(tmp_proc[key])
                else:
                    tmp_sys = {}
                    tmp_sys[key] = [tmp[key][dic_key] for dic_key in self.sys_headers]
                    print >> self.files[key], list_to_csv(tmp_sys[key])


###
###     Helpers
###
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
