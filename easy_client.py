#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conf import *
from helpers import Logger, send_data, recv_data
#from printer import print_dic, init_print
from data_client import DataClient
from data_processing import DataProcessor

import socket, threading, select, Queue, json
import time, sys, argparse


### Code for server for sending headers.

#dico = {}
#for keys in self.targets:
#    if keys == 'system':
#        dico[keys] = self.sys_headers
#        self.log.debug('[INIT THREAD] Got sys header')
#    else:
#        dico[keys] = self.proc_headers
#        self.log.debug('[INIT THREAD] Got proc header')
#mess = json.dumps(dico)
#self.log.debug('[INIT THREAD] Sending {}'.format(mess))
#send_data(connection, mess)
#self.log.info('[INIT THREAD] Headers sent. End of thread')
### Sync data thread

class LightClient(object):
    def __init__(self, ip, adict = {'v': V_DEBUG, 'processes':['naoqi-service']}):
        if not os.path.isdir(LOCAL_DATA_DIR):
            os.makedirs(LOCAL_DATA_DIR)

        # Logging
        self.log = Logger(CLIENT_LOG_FILE, adict['v'])
        self.log.info('[MAIN THREAD] Instantiated client')
        self.log.debug(adict)

        # Central data
        self.receiving = False
        self.define_headers()
        self.define_targets(adict)
        self.transmit = Queue.Queue()

        # workers
        self.data_client = DataClient(adict, self.transmit, ip)
        self.data_processor = DataProcessor(adict, self.transmit, self.headers, self.targets)

        # Connection
        self.connect(ip)

    def connect(self, ip):
        self.soc_ctrl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc_ctrl.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_ip = socket.gethostbyname('')
        self.log.debug('[MAIN THREAD] connecting...')
        self.soc_ctrl.connect((ip,SOC_PORT_CTRL))
        self.log.info('[MAIN THREAD] Client connected to server')

    def define_headers(self):
        head = {}
        head['process'] = PROC_CPU_DATA + PROC_MEM_DATA
        head['system']  = SYS_CPU_OTHER + LOAD_AVG + SYS_CPU_DATA + SYS_MEM_DATA
        self.headers = head

    def define_targets(self, adict):
        targ = {}
        targ['system'] = ['system']
        targ['process'] = adict['processes']
        self.targets = targ

    def start_record(self):
        self.log.debug('[MAIN THREAD] Asking server to start recording')
        send_data(self.soc_ctrl,START_RECORD)
        self.log.info('[MAIN THREAD] Server asked to start recording')

    def stop_record(self):
        self.log.debug('[MAIN THREAD] Asking server to stop recording')
        send_data(self.soc_ctrl,STOP_RECORD)
        self.log.info('[MAIN THREAD] Server asked to stop recording')

    def start_receive(self):
        if not self.receiving:
            self.receiving = True
            self.log.debug('[MAIN THREAD] Asking server to start sending')
            status = send_data(self.soc_ctrl,START_SEND)
            self.log.info('[MAIN THREAD] Server asked to start sending')
            if status == FAIL:
                self.log.error('[MAIN THREAD] Client tried to receive but server denied it')
            else:
                self.data_client.start()
                self.log.info('[MAIN THREAD] Client is receiving')
            self.log.debug("[MAIN THREAD] DATA THREAD started")
        else:
            self.log.warn("[MAIN THREAD] Asked to start receiving while already receiving")

    def stop_receive(self):
        if self.receiving:
            self.log.debug('[MAIN THREAD] Closing data channel. Exiting data client thread')
            self.data_client.stop()
            self.log.info("[MAIN THREAD] Asked server to stop receiving")
            self.receiving = False
        else:
            self.log.warn("[MAIN THREAD] Asked to stop receiving while already receiving")

    def start_store(self, dirname = 'easy_client'):
        return self.data_processor.start_store(dirname)

    def stop_store(self):
        self.data_processor.stop_store()

    def start_print(self):
        self.data_processor.start_print()

    def stop_print(self):
        self.printing = data_processor.stop_print()

    def stop_print(self):
        self.data_processor.stop_print()

    def stop_process(self):
        self.stop_print()
        self.stop_store()
        self.data_processor.stop()
        self.stop_receive()
        self.soc_ctrl.close()

    def stop_all(self):
        self.stop_process()
        send_data(self.soc_ctrl, STOP_ALL)


def parserArguments(parser):
    parser.add_argument('--proc' , dest = 'processes', nargs='*', default = [], help = 'processes to watch')
    parser.add_argument('--tout' , dest = 'timeout', type = int, default = '10000' , help = 'timeout in seconds')
    parser.add_argument('--step' , dest = 'step', type = int, default = '1' , help = 'period of recording in seconds')
    parser.add_argument('--rec' , dest = 'rec', nargs='*', default = ['local', 'remote'] , help = 'record mode, can be local or remote')
    parser.add_argument('--verbose', '-v' , dest = 'v', type = int, default = V_INFO , help = 'record mode, can be local or remote')
    parser.add_argument('--ip', '-i' , dest = 'ip', type = str, default = None , help = 'ip to connect to')


remote_commands = {
    'start record\n'  : START_RECORD,
    'stop record\n'   : STOP_RECORD,
    'start send'    : START_SEND,
    'stop send'     : STOP_SEND,
    'stop\n'          : STOP_ALL,
}

local_commands = {
    'start print'   :'',
    'stop print'    :'',
    'get data'      :'',
}

if __name__ == '__main__':
    print 'Start'
    parser = argparse.ArgumentParser(description = 'dialog_cpu_stats')
    parserArguments(parser)
    args = parser.parse_args()
    adict = vars(args)
    if adict['ip']:
        ip = adict['ip']
    else:
        ip = IP_1

    print 'Arguments parsed'
    client = LightClient(ip, adict)
    while sys.stdin in select.select([sys.stdin], [], [], 1000)[0]:
        line = sys.stdin.readline()
        if line:
            if line =='start send\n':
                client.start_receive()
            elif line == 'stop send\n':
                client.stop_receive()
            elif line == 'start record\n':
                client.start_record()
            elif line == 'stop record\n':
                client.stop_record()
            elif line == 'print\n':
                client.start_print()
            elif line == "start store\n":
                client.start_store('easy_client')
            elif line == "stop store\n":
                client.stop_store()
            elif line == "start print\n":
                client.start_print()
            elif line == "stop print\n":
                client.stop_print()
            elif line == "quit\n":
                client.stop_process()
                break
            else:
                print 'wrong command argument'
        else:
            print('eof')
            sys.exit(0)
    else:
        client.stop_process()
        print 'Exit because of user inaction'
    print 'line ={} /'.format(line)
