#!/usr/bin/env python
# -*- coding: utf-8 -*-
#from functionaltools import ssh_tools

from conf import *
from deploy_data import init_server_session, clean_server
from easy_client import LightClient
from fabric.api import env
import argparse, os, time, json

def _get_result_data():
    if not os.path.isdir(LOCAL_DATA_DIR):
        os.makedirs(LOCAL_DATA_DIR)
    nao_data_files = os.path.join(NAO_DATA_DIR, "*")
    get(nao_data_files, LOCAL_DATA_DIR)

class RemoteCPUWatch(object):
    def __init__(self, ip):
        self.ip = ip
        self.client = LightClient(ip = self.ip)
        self.record = False
        self.receive = False
        self.printer = False
        self.store = False
        self.files = []

    def start_display(self):
        if not self.record:
            self.client.start_record()
        if not self.receive:
            self.client.start_receive()
        if not self.printer:
            self.client.start_print()
        self.record = True
        self.receive = True
        self.printer = True

    def stop_display(self):
        self.client.stop_print()
        self.printer = False
        if not self.check_action():
            self.client.stop_receive()
            self.receive = False
            self.client.stop_record()
            self.record = False

    def start_store(self):
        if not self.record:
            self.client.start_record()
        if not self.receive:
            self.client.start_receive()
        if not self.store:
            self.files = self.client.start_store()
        self.store = True
        self.record = True
        self.receive = True

    def stop_store(self):
        self.client.stop_store()
        self.store = False
        if not self.check_action():
            print 'actions checked positive'
            self.client.stop_process()
            self.receive = False
            self.record = False

    def check_action(self):
        return self.printer or self.store

    def get_data(self, target, field):
        pass


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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description = 'client for requesting robot system data')
    parserArguments(parser)
    args = parser.parse_args()
    adict = vars(args)

    for key in adict:
        print '{key}:{value}'.format(key= str(key), value = adict[key])

    with RemoteCPUWatch(ip = '10.0.132.32') as cpu:
        print 'cpu started'
        #cpu.start_display()
        cpu.start_store()
        print 'actions started'
        time.sleep(30)
        print 'Done'

