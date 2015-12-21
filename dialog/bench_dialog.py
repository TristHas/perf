#!/usr/bin/env python
# -*- coding: utf-8 -*-
#from functionaltools import ssh_tools

from ..log.log_watch import LogWatch
from ..cpu.easy_client import LightClient
import argparse, os, time, json, csv
import numpy as np

class DialogBench(object):
    def __init__(self, ip):
        self.ip = ip
        self.client = LightClient(ip = self.ip)
        self.log = LogWatch(ip)
        self.record = False
        self.receive = False
        self.printer = False
        self.store = False
        self.files = []

    def profile_compilation_performance(self, testID, visu = False):
        self.log.start_watch_dialog()
        self.start_store(testID)
        self.testID = testID
        if visu:
            self.start_display()

    def get_compilation_performance_results(self):
        self.log.stop_watch_dialog()
        self.log.dump_logs(self.testID)
        self.stop_store()
        results = [ self.log.get_load_time(),
                    self.log.get_bundle_compile_time('welcome'),
                    self.log.get_model_compile_time('welcome'),
                    self.log.get_reco_compile_time('welcome', 'Japanese'),
                    self.log.get_reco_compile_time('welcome', 'English'),
                    self.get_naoqiservice_VmRSS_diff(),
                    self.get_naoqiservice_VmSize_diff(),
                    self.get_cpu_lavg1_max(),
                    self.get_cpu_iotime_mean(),
                    self.get_cpu_majflt_sum(),
                    self.get_naoqiservice_stime_mean(),
                    self.get_naoqiservice_utime_mean(),
                    ]
        self.stop_display()
        self.testID = 'none'
        return results

    def start_display(self):
        if not self.record:
           self._start_record()
        if not self.receive:
            self.client.start_receive()
        if not self.printer:
            self.client.start_print()
        self.record = True
        self.receive = True
        self.printer = True

    def stop_display(self):
        if self.printer:
            self.client.stop_print()
            self.printer = False
            if not self._check_action():
                self._stop_record()
                self.client.stop_process()
                self.receive = False
                self.record = False

    def start_store(self, dirname = 'remote_cpu'):
        if not self.record:
            self._start_record()
        if not self.receive:
            self.client.start_receive()
        if not self.store:
            self.files = self.client.start_store(dirname = dirname)
        self.store = True
        self.record = True
        self.receive = True

    def stop_store(self):
        if self.store:
            self.client.stop_store()
            self.files = []
            self.store = False
            if not self._check_action():
                self._stop_record()
                self.client.stop_process()
                self.receive = False
                self.record = False

    def get_naoqiservice_VmRSS_diff(self):
        try:
            data = self.get_data('naoqi-service', 'VmRSS')
            result = data[-1] - data[0]
        except Exception:
            return None
        return result

    def get_naoqiservice_VmSize_diff(self):
        try:
            data = self.get_data('naoqi-service', 'VmSize')
            result = data[-1] - data[0]
        except Exception:
            return None
        return result

    def get_naoqiservice_utime_mean(self):
        try:
            data = self.get_data('naoqi-service', 'utime')
            result = np.mean(data)
        except Exception:
            return None
        return result

    def get_naoqiservice_stime_mean(self):
        try:
            data = self.get_data('naoqi-service', 'stime')
            result = np.mean(data)
        except Exception:
            return None
        return result

    def get_cpu_iotime_mean(self):
        try:
            data = self.get_data('system', 'io_time')
            result = np.mean(data)
        except Exception:
            return None
        return result

    def get_cpu_lavg1_max(self):
        try:
            data = self.get_data('system', 'lavg_1')
            result = np.max(data)
        except Exception:
            return None
        return result

    def get_cpu_majflt_sum(self):
        try:
            data = self.get_data('naoqi-service', 'majflt')
            result = np.sum(data)
        except Exception:
            return None
        return result

    ###
    ### Helpers
    ###
    def _start_record(self):
        self.client.start_record('system', 'system')
        self.client.start_record('process', 'naoqi-service')

    def _stop_record(self):
        self.client.stop_record('system', 'system')
        self.client.stop_record('process', 'naoqi-service')

    def _check_action(self):
        print 'self.printer = ' + str(self.printer) + ' self.store = ' + str(self.store)
        return self.printer or self.store

    def get_data(self, target, field):
        try:
            for files in self.files:
                if os.path.basename(files) == target:
                    with open(files) as csvfile:
                        reader = csv.DictReader(csvfile)
                        result = []
                        for row in reader:
                            print row
                            result.append(float(row[field]))
                        return result
        except AttributeError:
            return None

def parserArguments(parser):
    parser.add_argument('--proc' , dest = 'proc', nargs='*',
        default = [], help = 'processes to watch')
    parser.add_argument('--tout' , dest = 'timeout', type = int,
        default = '10000' , help = 'timeout in seconds')
    parser.add_argument('--step' , dest = 'step', type = int,
        default = '1' , help = 'period of recording in seconds')
    parser.add_argument('--rec' , dest = 'rec', nargs='*',
        default = ['local', 'remote'] , help = 'record mode, can be local or remote')
    parser.add_argument('--verbose', '-v' , dest = 'v', type = int,
        default = 1 , help = 'verbosity level')

