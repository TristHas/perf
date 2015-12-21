#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conf import *
from helpers import Logger, send_data, recv_data
from data_client import DataClient
from data_processing import DataProcessor
import socket, threading, select, Queue, json
import time, sys, argparse

class LightClient(object):
    def __init__(self, ip):
        self.log = Logger(MAIN_CLIENT_LOG_FILE, D_VERB)
        self.log.info('[MAIN THREAD] Instantiated client')
        self.receiving = False
        self.define_headers()
        self.targets = {}
        self.transmit = Queue.Queue()
        self.data_client = DataClient(self.transmit, ip)
        self.data_processor = DataProcessor(self.transmit, self.headers, self.targets)
        self.connect(ip)

    def connect(self, ip):
        self.soc_ctrl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc_ctrl.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_ip = socket.gethostbyname('')
        self.log.debug('[MAIN THREAD] connecting...')
        self.soc_ctrl.connect((ip,SOC_PORT_CTRL))
        self.log.info('[MAIN THREAD] Client connected to server')

    def disconnect(self):
        ### data processor should not be here
        self.data_processor.stop()
        self.soc_ctrl.close()

    def define_headers(self):
        head = {}
        head['process'] = PROC_CPU_DATA + PROC_MEM_DATA + TIMESTAMPS
        head['system']  = SYS_CPU_OTHER + LOAD_AVG + SYS_CPU_DATA + SYS_MEM_DATA + TIMESTAMPS
        self.headers = head

    def add_target(self, target, name):
        if target in self.targets:
            self.targets[target].append(name)
        else:
            self.targets[target]=[name]

    def remove_target(self, target, name):
       if target in self.targets:
           if name in self.targets[target]:
               self.targets[target].remove(name)
               self.log.info('[MAIN THREAD] Removed {} named {}'.format(target, name))
           else:
               self.log.error('[MAIN THREAD] Asked to remove {} named {} while not recorded'.format(target, name))
       else:
           self.log.error('[MAIN THREAD] Asked to remove {} named {} while not recorded'.format(target, name))

    def start_record(self, target, name):
        self.log.debug('[MAIN THREAD] Asking server to start recording')
        msg = MSG_SEP.join([START_RECORD, target, name])
        answer = send_data(self.soc_ctrl,msg)
        self.log.info('[MAIN THREAD] Server asked to start recording')
        if answer == SYNC:
            self.add_target(target, name)
            self.log.info('[MAIN THREAD] Added {} named {}'.format(target, name))
        else:
            self.log.warn('[MAIN THREAD] Could not add {} named {} because of server answer'.format(target, name))

    def stop_record(self, target, name):
        self.log.debug('[MAIN THREAD] Asking server to stop recording')
        msg = MSG_SEP.join([STOP_RECORD, target, name])
        answer = send_data(self.soc_ctrl,msg)
        self.log.info('[MAIN THREAD] Server asked to stop recording {}'.format(name))
        if answer == SYNC:
            self.remove_target(target, name)
        else:
            self.log.warn('[MAIN THREAD] Could not remove {} named {} because of server answer'.format(target, name))

    def start_receive(self):
        if not self.receiving:
            self.receiving = True
            self.log.debug('[MAIN THREAD] Asking server to start sending')
            status = send_data(self.soc_ctrl,START_SEND)
            self.log.info('[MAIN THREAD] Server asked to start sending')
            if status == FAIL:
                self.log.error('[MAIN THREAD] Client tried to receive but server denied it')
            else:
                print status
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
            send_data(self.soc_ctrl,STOP_SEND)
        else:
            self.log.warn("[MAIN THREAD] Asked to stop receiving while already receiving")

    def start_store(self, dirname = 'easy_client'):
        return self.data_processor.start_store(dirname)

    def stop_store(self):
        self.data_processor.stop_store()

    def start_print(self):
        self.data_processor.start_print()

    def stop_print(self):
        self.printing = self.data_processor.stop_print()

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



if __name__ == '__main__':
    print 'Start'
    parser = argparse.ArgumentParser(description = 'dialog_cpu_stats')
    parserArguments(parser)
    args = parser.parse_args()
    adict = vars(args)
    if adict['ip']:
        ip = adict['ip']
    else:
        sys.exit('Please specify an ip with --ip option')
    print ip
    print 'Arguments parsed'
    client = LightClient(ip)
    while sys.stdin in select.select([sys.stdin], [], [], 1000)[0]:
        line = sys.stdin.readline()
        if line:
            if line =='start send\n':
                client.start_receive()
            elif line == 'stop send\n':
                client.stop_receive()
            elif line.startswith('start record'):
                data = line.split()
                if len(data) !=3:
                    print 'Wrong input argument {}'.format(line)
                else:
                    if data[2] == 'system':
                        client.start_record('system', 'system')
                    else:
                        client.start_record('process', data[2])
            elif line.startswith('stop record'):
                data = line.split()
                if len(data) !=3:
                    print 'Wrong input argument {}'.format(line)
                else:
                    if data[2] == 'system':
                        client.stop_record('system', 'system')
                    else:
                        client.stop_record('process', data[2])
            elif line == 'print\n':
                client.start_print()
            elif line =="start store\n":
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
