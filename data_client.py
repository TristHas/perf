#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import socket, threading
from helpers import Logger, send_data, recv_data
from conf import *

DATA_CLIENT_LOG_FILE = os.path.join(LOCAL_DATA_DIR, 'data_client.log')

class DataClient(object):
    def __init__(self, queue, ip):
        if not os.path.isdir(LOCAL_DATA_DIR):
            os.makedirs(LOCAL_DATA_DIR)
        self.log = Logger(DATA_CLIENT_LOG_FILE, D_VERB)
        self.log.info('[MAIN THREAD] Instantiatie data_client')
        self.transmit = queue
        self.receiving = False
        self.remote_ip = ip
        self.my_ip = socket.gethostbyname(socket.gethostname())
        # Headers could be used to check structure integrity of received data
        # Data integrity check put in data_processor
        # self.headers = None

    def start(self):
        self.soc_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc_data.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.log.debug('[MAIN THREAD] Connecting to server data channel')
        self.soc_data.connect((self.remote_ip,SOC_PORT_DATA))
        self.log.info('[MAIN THREAD] Data Channel Connected')
        self.data_receive = threading.Thread(target = self.receive, args = ())
        self.log.info('[MAIN THREAD] Starting DATA THREAD')
        self.receiving = True
        self.data_receive.start()
        self.log.debug('[MAIN THREAD] DATA THREAD started')

    def stop(self):
        self.log.debug("[MAIN THREAD] Stop command sent")
        self.receiving = False
        self.log.info("[MAIN THREAD] Asked DATA THREAD to stop receiving")

    def receive(self):
        #FIXME_1 : recv_data is blocking. If nothing is sent and asked to stop, it will block program exit
        while self.receiving:
            self.log.debug('[DATA THREAD] waiting for data from server')
            data = recv_data(self.soc_data)
            self.log.debug('[DATA THREAD] Received data {}\n'.format(data))
            if data:
                self.transmit.put(data)
                self.log.debug('[DATA THREAD] Transmitted data ')
            else:   # Not sure this should exist
                self.log.info('[DATA THREAD] Empty data received. Closing socket ')
                self.soc_data.close()
                break
        if not self.receiving:
            self.log.info('[DATA THREAD] self.receiving is False. Closing socket ')
            self.soc_data.close()
        self.log.info('[DATA THREAD] Exiting thread \n')




