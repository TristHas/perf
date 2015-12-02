#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conf import *
from printer import *
from helpers import Logger, list_to_csv
from Queue import Empty
import shutil, os
import threading
import json

DATA_PROC_LOG_FILE = os.path.join(LOCAL_DATA_DIR, 'data_processor.log')

class DataProcessor(object):
    def __init__(self, adict, queue, headers, targets):
        self.log = Logger(DATA_PROC_LOG_FILE, level = V_DEBUG)
        # Main thread communication
        self.keep_running = True
        self.transmit = queue
        self.headers = headers
        self.targets = targets

        # print data
        self.printing = False
        self.base_data = None
        self.fig = ()
        self.ax = ()
        # store data
        self.local_store = False
        self.files = {}

        # Launching Thread
        self.thr = threading.Thread(target = self.process, args = (), name = 'process_thread')
        self.start()

    ###
    ###     Process Thread
    ###

    def start(self):
        self.log.info('[MAIN THREAD] Starting process thread')
        self.thr.start()
        self.log.debug('[MAIN THREAD] Process thread started')

    def stop(self):
        self.keep_running = False
        self.log.info('[MAIN THREAD] Asked processing thread end')

    def process(self):
        while self.keep_running:
            self.log.debug('[PROCESS THREAD] Getting data')
            try:
                data = self.transmit.get(timeout = 1)
                data = json.loads(data)
                self.log.debug('[PROCESS THREAD] Got data')
                if self.printing:
                    to_print = self.build_print_data(data)
                    self.log.debug('[PROCESS THREAD] Printing')
                    multi_print_dic(self.base_data, self.print_data)
                    self.log.debug('[PROCESS THREAD] Printed')
                if self.local_store:
                    # self.build_store_data?
                    self.process_store(data)
                    #### To write: self.process_local
            except Empty:
                self.log.debug('[PROCESS THREAD] No data')
        self.log.info('[PROCESS THREAD] End of thread')

    ###
    ###         Print utilities
    ###
    def start_print(self):
        self.log.info('[MAIN THREAD] Start printing')
        self.build_print_headers()
        self.log.debug('[MAIN THREAD] Built headers')
        self.print_data = multi_init_print(self.base_data)
        self.log.debug('[MAIN THREAD] Graphics initiated')
        self.printing = True

    def stop_print(self):
        self.log.info('[MAIN THREAD] Stop printing')
        self.printing = False

    def build_print_headers(self):
        ret = {}
        for types in self.targets:
            for instance in self.targets[types]:
                ret[instance]={}
                for data_field in self.headers[types]:
                    ret[instance][data_field] = []
        self.base_data = ret
        self.log.debug('[DATA THREAD] Header: {}'.format(self.base_data))

    def build_print_data(self, dico):
        for target in dico:
            for data_field in dico[target]:
                # Easy to handle data sequence length here
                self.base_data[target][data_field].append(dico[target][data_field])

    ####
    ####        Storage utilities
    ####

    def process_store(self, dico):
        print dico
        #print self.files
        for target in self.files:
            res = [dico[target][data_field] for data_field in dico[target]]
            print >> self.files[target], list_to_csv(res)
            self.log.debug('[PROCESS THREAD] Stored {}'.format(list_to_csv(res)))


    def start_store(self, dirname = None):
        # Make record dir
        if not dirname:
            print 'dirname is none'
            dirname = time.time()
        print dirname
        self.log.info('[MAIN THREAD] Starting local storage')
        directory = os.path.join(LOCAL_DATA_DIR, dirname)
        print "directory = " + directory
        if os.path.isdir(directory):
            shutil.rmtree(directory)
        os.makedirs(directory)
        self.log.debug('[MAIN THREAD] Made local record dir')

        # Open files
        for types in self.targets:
            for instance in self.targets[types]:
                filename = os.path.join(directory, instance)
                self.files[instance] = open(filename, 'w')
                self.log.debug('[MAIN THREAD] Opened {}'.format(filename))

        # Write headers
        for key in self.files:
            if key == 'system':
                print >> self.files[key], list_to_csv(self.headers['system'])
                self.log.debug('[MAIN THREAD] wrote {}'.format(list_to_csv(self.headers['system'])))
            else:
                print >> self.files[key], list_to_csv(self.headers['process'])
                self.log.debug('[MAIN THREAD] wrote {}'.format(list_to_csv(self.headers['process'])))

        # Ask start storing
        self.local_store = True
        self.log.debug('[MAIN THREAD] End start local')
        return [os.path.join(directory, instance) for instance in self.files]

    def stop_store(self):
        self.log.info('[MAIN THREAD] Stopping storage')
        self.local_store = False
        for key in self.files:
            self.files[key].close()
            self.log.debug('closed {}'.format(key))





