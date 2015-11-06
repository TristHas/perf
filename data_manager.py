#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conf import *
from helpers import Logger, send_data, list_to_csv
import threading, socket, time
import json
import os

class DataManager(object):
    def __init__(self, adict, headers, targets, data):
        self.step = adict['step']
        self.timeout = int(adict['timeout'] / self.step)

        self.log = Logger(DATA_LOG_FILE, adict['v'])

        self.run = True
        self.local_store = False
        self.keep_going = True

        self.files = dict()
        self.targets = ['system'] + adict['processes']
        self.receivers = []

        self.sys_headers = headers['system']
        self.proc_headers = headers['process']

        self.data_thread = threading.Thread(target = self.processing, name = 'data managing', args =(data,), kwargs=adict)
        self.log.info('Starting DATA THREAD')
        self.data_thread.start()
        self.log.debug('DATA THREAD Started')

    def processing(self, *args, **adict):
        while self.run:
            queue = args[0]
            self.log.debug('[DATA THREAD] Waiting for queue')
            data = queue.get()
            self.log.debug('[DATA THREAD] Got {}'.format(data))
            if self.local_store:
                self.process_local(data)
            for socket in self.receivers:
                self.process_send(socket, data)

    def quit(self):
        self.run = False

    def start_send(self):
        self.init_thread = threading.Thread(target = self.init_send, name = 'init_send_data', args = ())
        self.log.info('Starting INIT THREAD')
        self.init_thread.start()
        self.log.debug('INIT THREAD Started')

    def init_send(self):
        soc_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc_data.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc_data.bind((SOC_ADR_REMOTE, SOC_PORT_DATA))
        soc_data.listen(1)
        self.log.info('[INIT THREAD] Waiting for a connection')
        connection, client_address = soc_data.accept()
        self.log.info('[INIT THREAD] Connection accepted from {}'.format(client_address))
        dico = {}
        for keys in self.targets:
            if keys == 'system':
                dico[keys] = self.sys_headers
                self.log.debug('[INIT THREAD] Got sys header')
            else:
                dico[keys] = self.proc_headers
                self.log.debug('[INIT THREAD] Got proc header')
        mess = json.dumps(dico)
        self.log.debug('[INIT THREAD] Sending {}'.format(mess))
        send_data(connection, mess)
        self.log.info('[INIT THREAD] Headers sent. End of thread')
        ### Sync data thread
        self.receivers.append(connection)

    def process_send(self, connection, data):
        mess = json.dumps(data)
        self.log.debug('[DATA THREAD] Sending data {}'.format(mess))
        send_data(connection, mess)
        self.log.debug('[DATA THREAD] Data sent')

    def stop_send(self):
        self.log.info('Stopping DATA THREAD')
        tmp = self.receivers
        self.receivers = []
        for elem in tmp:
            elem.close()
            self.log.debug('Closed data socket')



    def start_local(self):
        # Make record dir
        self.log.info('Starting local')
        directory = os.path.join(NAO_DATA_DIR, time.ctime())
        os.makedirs(directory)
        self.log.debug('Made local record dir')

        # Open files
        for key in self.targets:
            filename = os.path.join(directory, key)
            self.files[key] = open(filename, 'w')
            self.log.debug('Opened {}'.format(filename))
        for key in self.files:
            if key == 'system':
                print >> self.files[key], list_to_csv(self.sys_headers)
                self.log.debug('wrote {}'.format(list_to_csv(self.sys_headers)))
            else:
                print >> self.files[key], list_to_csv(self.proc_headers)
                self.log.debug('wrote {}'.format(list_to_csv(self.proc_headers)))
        self.local_store = True
        self.log.debug('End start local')

    def process_local(self, tmp):
        if tmp == 'end':
            self.log.info('[DATA THREAD] Received end message')
            self.local_store = False
            for key in self.files:
                self.files[key].close()
                self.log.debug('[DATA THREAD] Closing {}'.format(key))
        else:
            for key in self.files:
                if key != 'system':
                    tmp_proc = {}
                    tmp_proc[key] = [tmp[key][dic_key] for dic_key in self.proc_headers]
                    print >> self.files[key], list_to_csv(tmp_proc[key])
                    self.log.debug('[DATA THREAD] Stored {}'.format(tmp_proc[key]))
                else:
                    tmp_sys = {}
                    tmp_sys[key] = [tmp[key][dic_key] for dic_key in self.sys_headers]
                    print >> self.files[key], list_to_csv(tmp_sys[key])
                    self.log.debug('[DATA THREAD] Stored {}'.format(tmp_sys[key]))

    def stop_local(self):
        self.log.info('Stopping storage')
        self.local_store = False
        for key in self.files:
            self.files[key].close()
            self.log.debug('closed {}'.format(key))

