#!/usr/bin/env python
# -*- coding: utf-8 -*-
#from functionaltools import ssh_tools

from conf import *
from deploy_data import init_session, clean
from easy_client import LightClient
from fabric.api import env
import argparse, os, time, json

def _get_result_data():
    if not os.path.isdir(LOCAL_DATA_DIR):
        os.makedirs(LOCAL_DATA_DIR)
    nao_data_files = os.path.join(NAO_DATA_DIR, "*")
    get(nao_data_files, LOCAL_DATA_DIR)

class RemoteCPUWatch(object):
    def __init__(self, ip = None):
        if ip:
            self.ip = ip
            env.host_string = ip
        else:
            self.ip = REMOTE_IP_DEF
        init_session()
        self.client = LightClient(self.ip)
        self.record = False
        self.receive = False
        self.printer = False
        self.store = False

    def __enter__(self):
        return self

    def start_display(self):
        self.client.start_record()
        self.client.start_receive()
        self.client.start_print()
        self.record = True
        self.receive = True
        self.printer = True

    def start_store(self):
        self.client.start_record()
        self.client.start_storage()
        self.store = True

    def stop_store(self):
        self.client.stop_storage()
        self.store = False
        if not self.check_action():
            self.client.stop_record()

    def check_action(self):
        return self.receive or self.store

    def stop_display(self):
        self.client.stop_receive()
        self.receive = False
        self.client.stop_print()
        self.printer = False
        if not self.check_action():
            self.client.stop_record()

    def get_data(self):
        pass

    def __exit__(self, type, value, traceback):
        self.stop_display()
        self.stop_store()
        self.client.stop_all()
        clean()
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

    with RemoteCPUWatch() as cpu:
        print 'cpu started'
        cpu.start_display()
        cpu.start_store()
        print 'actions started'
        time.sleep(30)
        print 'Done'











