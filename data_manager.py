#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conf import *
from helpers import Logger, send_data, list_to_csv
import threading, socket, time
import json
import os

class DataManager(object):
    def __init__(self, adict, headers, targets, transmit):
        self.step = adict['step']
        self.timeout = int(adict['timeout'] / self.step)

        self.log = Logger(DATA_LOG_FILE, adict['v'])
        self.run = True

        self.targets = ['system'] + adict['processes']
        self.receivers = []
        self.transmit = transmit

        self.sys_headers = headers['system']
        self.proc_headers = headers['process']

        self.data_thread = threading.Thread(target = self.processing, name = 'data managing', args = ())
        self.log.info('Starting DATA THREAD')
        self.data_thread.start()
        self.log.debug('DATA THREAD Started')

    def processing(self):
        while self.run:
            self.log.debug('[DATA THREAD] Waiting for queue')
            data = self.transmit.get()
            self.log.debug('[DATA THREAD] Got {}'.format(data))
            for socket in self.receivers:
                self.process_send(socket, data)

    def quit(self):
        self.run = False

    def start_send(self):
        self.init_thread = threading.Thread(target = self.init_connection, name = 'init_send_connection', args = ())
        self.log.info('[MAIN THREAD] Starting INIT THREAD')
        self.init_thread.start()
        self.log.debug('[MAIN THREAD] INIT THREAD Started')

    def init_connection(self):
        soc_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc_data.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc_data.bind(('', SOC_PORT_DATA))
        soc_data.listen(1)
        self.log.info('[INIT THREAD] Waiting for a connection')
        connection, client_address = soc_data.accept()
        self.log.info('[INIT THREAD] Connection accepted from {}'.format(client_address))
        self.receivers.append(connection)

    def process_send(self, connection, data):
        mess = json.dumps(data)
        self.log.debug('[DATA THREAD] Sending data {}'.format(mess))
        status = send_data(connection, mess)
        if status == '':
            self.receivers.remove(connection)
            self.log.info('[DATA THREAD] connection removed')
        self.log.debug('[DATA THREAD] Data sent')

    def stop_send(self):
        self.log.info('[MAIN THREAD] Stopping DATA THREAD')
        tmp = self.receivers
        self.receivers = []
        for elem in tmp:
            elem.close()
            self.log.debug('[MAIN THREAD] Closed data socket')

    def is_sending(self):
        if len(self.receivers) > 0:
            return True
        else:
            return False
