#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conf import *
from helpers import Logger, send_data
from printer import print_dic, init_print
import socket, threading, Queue, json
import time, sys, argparse

def recv_data(soc):
    data = soc.recv(4096)
    soc.sendall('sync')
    return data

def treat_header(header):
    dico = json.loads(header)
    print dico
    ret = {}
    for keys in dico:
        ret[keys]={}
        header_list = dico[keys]
        for elem in header_list:
            ret[keys][elem] = []
    print '[DATA THREAD] Header: {}'.format(ret)
    return ret

def treat_data(data, base_data):
    dico = json.loads(data)
    for keys in dico:
        for elem in base_data[keys]:
            base_data[keys][elem].append(dico[keys][elem])

class LightClient(object):
    def __init__(self, adict, ip = None):
        if not os.path.isdir(LOCAL_DATA_DIR):
            os.makedirs(LOCAL_DATA_DIR)
        self.log = Logger(CLIENT_LOG_FILE, adict['v'])
        self.soc_ctrl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc_ctrl.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.soc_ctrl.bind((IP_2, SOC_PORT_CTRL))
        self.soc_ctrl.connect((SOC_ADR_REMOTE,SOC_PORT_CTRL))
        self.transmit = Queue.Queue()
        self.receiving = True
        self.headers = None

    def __enter__(self):
        return self

    def start_record(self):
        send_data(self.soc_ctrl,START_RECORD)

    def stop_record(self):
        send_data(self.soc_ctrl,STOP_RECORD)

    def start_receive(self):
        self.receiving = True
        self.data_receive = threading.Thread(target = self.receive, args = ())
        self.data_receive.start()

    def stop_receive(self):
        self.receiving = False
        send_data(self.soc_ctrl, STOP_SEND)

    def start_storage(self):
        send_data(self.soc_ctrl, START_STORE)

    def stop_storage(self):
        send_data(self.soc_ctrl, STOP_STORE)

    def start_print(self):
        while not self.headers:
            time.sleep(1)
        base_data = self.headers.copy()
        if self.receiving:
            fig, ax = init_print()
            self.printing = True
            self.data_receive = threading.Thread(target = self.print_loop, args = (fig, ax, base_data))
            self.data_receive.start()
            #if self.adict['v']
            print "[MAIN THREAD] Print Thread started"

    def print_loop(self, fig, ax, base_data):
        while self.printing:
            print '[PRINT THREAD] Getting data'
            data = self.transmit.get()
            print '[PRINT THREAD] Got data'
            if data == 'end':
                self.printing = False
                print '[PRINT THREAD] Treated end message'
            else:
                treat_data(data, base_data)
                print '[PRINT THREAD] Data treated'
                #print 'Printer got, about to print'
                print_dic(base_data, ax, fig)
                print '[PRINT THREAD] Data treated'
        print '[PRINT THREAD] Stop printing thread'

    def stop_print(self):
        self.printing = False

    def stop_all(self):
        self.stop_storage()
        self.stop_print()
        self.stop_receive()
        send_data(self.soc_ctrl, STOP_ALL)
        self.soc_data.close()

    def receive(self):
        send_data(self.soc_ctrl,START_SEND)
        self.soc_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc_data.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.soc_data.bind((IP_2, SOC_PORT_DATA))
        self.soc_data.connect((SOC_ADR_REMOTE,SOC_PORT_DATA))
        print '[DATA THREAD] Connected'

        # treat header
        data = recv_data(self.soc_data)
        self.headers = treat_header(data)

        while self.receiving:
            print '[DATA THREAD] waiting for data from server\n'
            data = recv_data(self.soc_data)
            #print '[DATA THREAD] Received data\n'
            if data:
                #data = json.loads(data)
                #print '[DATA THREAD] Putting data {}\n'.format(data)
                self.transmit.put(data)
                print '[DATA THREAD] Transmitted {} \n'.format(data)
                #print '[DATA THREAD] has put data \n'
                #print '[DATA THREAD] received {} \n'.format(data)
            else:
                print '[DATA THREAD] Empty data received. Closing socket \n'
                self.soc_data.close()
                break
        if not self.receiving:
            print '[DATA THREAD] self.receiving is False. Closing socket \n'
            self.soc_data.close()
        self.transmit.put('end')
        print '[DATA THREAD] Exiting thread \n'

    def __exit__(self, type, value, traceback):
        print 'execute exit'
        self.soc_ctrl.close()

def parserArguments(parser):
    parser.add_argument('--proc' , dest = 'processes', nargs='*', default = [], help = 'processes to watch')
    parser.add_argument('--tout' , dest = 'timeout', type = int, default = '10000' , help = 'timeout in seconds')
    parser.add_argument('--step' , dest = 'step', type = int, default = '1' , help = 'period of recording in seconds')
    parser.add_argument('--rec' , dest = 'rec', nargs='*', default = ['local', 'remote'] , help = 'record mode, can be local or remote')
    parser.add_argument('--verbose', '-v' , dest = 'v', type = int, default = V_INFO , help = 'record mode, can be local or remote')

remote_commands = {
    'start record'  : START_RECORD,
    'stop record'   : STOP_RECORD,
    'start send'    : START_SEND,
    'stop send'     : STOP_SEND,
    'start store'   : START_STORE,
    'stop store'    : STOP_STORE,
    'stop'          : STOP_ALL,
}

local_commands = {
    'start print'   :'',
    'stop print'    :'',
    'get data'      :'',
}

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'dialog_cpu_stats')
    parserArguments(parser)
    args = parser.parse_args()
    adict = vars(args)

    with LightClient(adict) as client:
        while True:
            line = raw_input()
            print '/' + line + '/'
            if line in remote_commands:
                if line =='start send':
                    client.start_receive()
                    client.start_print()
                else:
                    send_data(client.soc_ctrl, remote_commands[line])
                print "sent {}".format(line)
            else:
                print 'wrong command argument'
