#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..log.log_watch import LogWatch
from ..cpu.easy_client import LightClient
from ..naoqi.naoqi_watcher import NaoqiWatcher
from qi import Session
import numpy as np
import argparse, os, time, json, csv

LOG_FILE = '/tmp/bench_life/main'

class VersionBench(object):
    def __init__(self, ip):
        self.ip = ip
        self.client = LightClient(ip = self.ip)
        self.naoqi  = NaoqiWatcher(ip = self.ip)
        #self.log = LogWatch(ip)
        self.record = False
        self.files = []
        self.set_robot_version()

    def set_robot_version(self):
        try:
            s = Session()
            s.connect(self.ip)
            system = s.service('ALSystem')
            version = system.systemVersion()
            split_version = version.split('.')
            if len(split_version) < 2:
                raise Exception('Wrong version format returned: {}'.format(version))
            if split_version[0] < 2:
                raise Exception('Unhandled version: {}'.format(version))
            if split_version[1] < 4:
                ### SHOULD test on 2.3 and predecessors
                raise Exception('Unhandled version: {}'.format(version))
            self.version = int(split_version[1])
            self.exact_version = version
        except Exception as e:
            #### SHOULD find out what to do
            print 'Version number processing went wrong: '
            print e.message
            print 'Considering we run on 2.4'
            self.version = 4

    def start_store(self, dirname = 'bench_version'):
        if not self.record:
            if self.version == 5:
                self.client.start_record('system', 'system')
                self.client.start_record('process', 'naoqi-service')
                self.client.start_record('process', 'naoqi-bin')
                self.client.start_record('process', 'client_gyro')
            else:
                self.client.start_record('system', 'system')
            self.client.start_receive()
            self.files = self.client.start_store(dirname = dirname)
            self.record = True

    def stop_store(self):
        if self.record:
            self.client.stop_store()
            self.client.stop_receive()
            if self.version == 5:
                self.client.stop_record('system', 'system')
                self.client.stop_record('process', 'naoqi-service')
                self.client.stop_record('process', 'naoqi-bin')
                self.client.stop_record('process', 'client_gyro')
            else:
                self.client.stop_record('system', 'system')
            self.client.disconnect()
            self.record = False

    def profile_long_life_run(self):
        #self.log.start_watch_general()
        self.start_store('long_life_run {}'.format(self.ip))
        naoqi_file = self.naoqi.start_activity_record()
        self.files.append(naoqi_file)

    def get_profile_results(self):
        #Should fsync to force file writing? that may be the cpu record problem we observe? Maybe already solved
        self.stop_store()
        self.naoqi.stop_activity_record()
        results = [
            self.get_naoqiservice_VmRSS_diff(),
            self.get_naoqiservice_VmSize_diff(),
            self.get_cpu_lavg1_max(),
            self.get_cpu_iotime_mean(),
            self.get_cpu_majflt_sum(),
            self.get_naoqiservice_stime_mean(),
            self.get_naoqiservice_utime_mean(),
            self.get_cpu_lavg1_mean()
        ]
        print results


    def get_naoqiservice_VmRSS_diff(self):
        try:
            data = self.get_data('naoqi-service', 'VmRSS')
            result = data[-1] - data[0]
        except Exception:
            return None
        return result

    def get_data(self, target, field):
        try:
            for files in self.files:
                if os.path.basename(files) == target:
                    with open(files) as csvfile:
                        reader = csv.DictReader(csvfile)
                        result = []
                        for row in reader:
                            result.append(float(row[field]))
                        return result
        except AttributeError:
            return None

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

    def get_cpu_lavg1_mean(self):
        try:
            data = self.get_data('system', 'lavg_1')
            result = np.mean(data)
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



