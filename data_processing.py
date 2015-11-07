#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conf import *
from helpers import Logger
from printer import multi_init_print, multi_print_dic
import threading
import json

DATA_PROC_LOG_FILE = os.path.join(LOCAL_DATA_DIR, 'data_processor.log')

class DataProcessor(object):
    def __init__(self, adict, queue, headers, targets):
        self.log = Logger(DATA_PROC_LOG_FILE, adict['v'])
        # Main thread communication
        self.transmit = queue
        self.headers = headers
        self.targets = targets

        # print data
        self.printing = False
        self.base_data = None
        self.fig = ()
        self.ax = ()

        # Launching Thread
        self.log.info('[MAIN THREAD] Launch proces thread')
        self.thr = threading.Thread(target = self.process, args = (), name = 'process_thread')
        self.log.info('[MAIN THREAD] Starting process thread')
        self.thr.start()
        self.log.debug('[MAIN THREAD] Process thread started')

    def start_print(self):
        self.log.info('[MAIN THREAD] Start printing')
        self.build_print_headers()
        self.log.debug('[MAIN THREAD] Built headers')
        self.fig, self.ax = multi_init_print(self.base_data)
        self.log.debug('[MAIN THREAD] Graphics initiated')
        self.printing = True

    def build_print_headers(self):
        ret = {}
        for types in self.targets:
            for instance in self.targets[types]:
                ret[instance]={}
                for data_field in self.headers[types]:
                    ret[instance][data_field] = []
        self.base_data = ret
        self.log.debug('[DATA THREAD] Header: {}'.format(self.base_data))

    def process(self):
        while True:
            self.log.debug('[PROCESS THREAD] Getting data')
            data = self.transmit.get()
            self.log.debug('[PROCESS THREAD] Got data')
            if self.printing:
                to_print = self.build_print_data(data)
                self.log.debug('[PROCESS THREAD] Printing')
                multi_print_dic(self.base_data, self.ax, self.fig)
                self.log.debug('[PROCESS THREAD] Printed')
        self.log.info('[PRINT THREAD] Stop printing thread')

    def build_print_data(self, data):
        print type(data)
        dico = json.loads(data)
        print dico
        for target in dico:
            for data_field in dico[target]:
                print 'target {}, datafield {}'.format(target, data_field)
                # Easy to handle data sequence length here
                self.base_data[target][data_field].append(dico[target][data_field])












