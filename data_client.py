#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import socket, threading
from helpers import Logger, send_data, recv_data
from conf import *

DATA_CLIENT_LOG_FILE = os.path.join(LOCAL_DATA_DIR, 'data_client.log')

class DataClient(object):
    def __init__(self, adict, queue, ip = None):
        if not os.path.isdir(LOCAL_DATA_DIR):
            os.makedirs(LOCAL_DATA_DIR)
        self.log = Logger(DATA_CLIENT_LOG_FILE, adict['v'])
        self.log.info('Instantiatie data_client')
        self.transmit = queue
        self.receiving = False
        # Headers could be used to check structure integrity of received data
        # Data integrity check put in data_processor
        # self.headers = None

    def start(self):
        self.soc_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc_data.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.soc_data.bind((IP_2, SOC_PORT_DATA))
        self.log.debug('[MAIN THREAD] Connecting to server data channel')
        self.soc_data.connect((SOC_ADR_REMOTE,SOC_PORT_DATA))
        self.log.info('[MAIN THREAD] Data Channel Connected')
        self.data_receive = threading.Thread(target = self.receive, args = ())
        self.log.info('[MAIN THREAD] Starting DATA THREAD')
        self.receiving = True
        self.data_receive.start()
        self.log.debug('[MAIN THREAD] DATA THREAD started')

    def stop(self):
        # Not good practice
        self.log.debug("[MAIN THREAD] Sending server stop receive command")
        send_data(self.soc_ctrl, STOP_SEND)
        self.log.debug("[MAIN THREAD] Stop command sent")
        self.receiving = False
        self.log.info("[MAIN THREAD] Asked DATA THREAD to stop receiving")

    def receive(self):
        while self.receiving:
            self.log.debug('[DATA THREAD] waiting for data from server\n')
            data = recv_data(self.soc_data)
            self.log.debug('[DATA THREAD] Received data {}\n'.format(data))
            if data:
                self.transmit.put(data)
                self.log.debug('[DATA THREAD] Transmitted data \n')
            else:
                self.log.info('[DATA THREAD] Empty data received. Closing socket \n')
                self.soc_data.close()
                break
        if not self.receiving:
            self.log.info('[DATA THREAD] self.receiving is False. Closing socket \n')
            self.soc_data.close()
        #
        #self.transmit.put('end')# Not sure we should communicate like that
        #
        self.receiving = False
        self.log.info('[DATA THREAD] Exiting thread \n')
































