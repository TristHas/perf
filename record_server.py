from cpu_load import CPUWatcher
from data_manager import DataManager
from conf import *
from helpers import *

import argparse, time, os, sys
import socket
import Queue

def parserArguments(parser):
    parser.add_argument('--proc' , dest = 'processes', nargs='*', default = [], help = 'processes to watch')
    parser.add_argument('--tout' , dest = 'timeout', type = int, default = '10000' , help = 'timeout in seconds')
    parser.add_argument('--step' , dest = 'step', type = int, default = '1' , help = 'period of recording in seconds')
    parser.add_argument('--rec' , dest = 'rec', nargs='*', default = ['local', 'remote'] , help = 'record mode, can be local or remote')
    parser.add_argument('--verbose', '-v' , dest = 'v', type = int, default = V_INFO , help = 'record mode, can be local or remote')

target_type = ('system', 'process')

def define_headers():
    head = {}
    head['process'] = PROC_CPU_DATA + PROC_MEM_DATA
    head['system']  = SYS_CPU_OTHER + LOAD_AVG + SYS_CPU_DATA + SYS_MEM_DATA
    return head

def define_targets():
    return {
        'system' :['system'],
        'process':adict['processes'],
        }

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description = 'dialog_cpu_stats')
        parserArguments(parser)
        args = parser.parse_args()
        adict = vars(args)

        if not os.path.isdir(NAO_DATA_DIR):
            os.makedirs(NAO_DATA_DIR)

        server_state = STATE_IDLE
        server_data_sockets = []
        log = Logger(SERV_LOG_FILE, adict['v'])

        log.info('[SERV PROC] Server is launched')
        log.debug(adict)

        targets = define_targets()
        log.debug(targets['process'])
        log.debug(type(targets['process']))
        headers = define_headers()
        data    = Queue.Queue()

        # Waits for a client connection
        soc_ctrl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc_ctrl.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc_ctrl.bind((SOC_ADR_REMOTE, SOC_PORT_CTRL))
        soc_ctrl.listen(1)

        ###
        ###     Add handling of multiple connections?
        ###
        log.info('[SERV PROC] Awaiting client connection')
        connection, client_address = soc_ctrl.accept()
        log.info('[SERV PROC] Connection made by client {}'.format(client_address))

        # Instantiate CPUWatcher
        cpu = CPUWatcher(adict, headers, targets, data)
        log.info('[SERV PROC] CPU Thread instantiated')
        data_manager = DataManager(adict, headers, targets, data)
        log.info('[SERV PROC] DATA Thread instantiated')

        try:
            # remplacer certaines info par des warning dans les logs?
            while True:
                log.debug('[SERV PROC] Back in loop, receiving ...')
                data = connection.recv(32)
                log.debug('[SERV PROC] received {}'.format(data))
                if data:
                    if data == START_RECORD:
                        if server_state == STATE_IDLE:
                            cpu.start()
                            server_state = STATE_RECORD
                            log.info('[SERV PROC] send start command')
                            connection.sendall(SYNC)
                        else:
                            log.warn('[SERV PROC] start command asked but state non idle')
                            connection.sendall(SYNC)

                    elif data == STOP_RECORD:
                        if server_state <= STATE_RECORD:
                            log.info('[SERV PROC] Stop command, record is stopped')
                            cpu.stop()
                            server_state = STATE_IDLE
                            connection.sendall(SYNC)
                        else:
                            log.warn('[SERV PROC] Asked for stop whereas state is {}'.format(server_state))
                            connection.sendall(FAIL)

                    elif data == START_SEND:
                        if server_state == STATE_IDLE:
                            connection.sendall(FAIL)
                            log.warn('[SERV PROC] Asked for send while idle')
                        elif server_state >= STATE_SEND:
                            log.info('[SERV PROC] Sending already')
                            connection.sendall(SYNC)
                        else:
                            data_manager.start_send()
                            log.info('[SERV PROC] Starts sending. Wait for connections')
                            if server_state == STATE_RECORD:
                               server_state = STATE_SEND
                            if server_state == STATE_STORE:
                                server_state = STATE_FULL
                            connection.sendall(SYNC)

                    elif data == STOP_SEND:
                        if server_state < STATE_SEND:
                            log.warn('[SERV PROC] Asked for stop send command while not sending')
                            connection.sendall(FAIL)
                        else:
                            log.info('[SERV PROC] Stop record')
                            data_manager.stop_send()
                            if server_state == STATE_SEND:
                               server_state = STATE_RECORD
                            if server_state == STATE_FULL:
                                server_state = STATE_STORE
                            connection.sendall(SYNC)

                    elif data == START_STORE:
                        if server_state == STATE_IDLE:
                            log.warn('[SERV PROC] Asked for local store while idle')
                            connection.sendall(FAIL)
                        elif server_state == STATE_FULL or server_state == STATE_STORE:
                            log.warn('[SERV PROC] Asked for local store while already recording')
                            connection.sendall(SYNC)
                        else:
                            log.info('[SERV PROC] Start local record')
                            data_manager.start_local()
                            if server_state == STATE_RECORD:
                                server_state = STATE_STORE
                            else:
                                server_state = STATE_FULL
                            connection.sendall(SYNC)

                    elif data == STOP_STORE:
                        if server_state == STATE_FULL:
                            log.info('[SERV PROC] Stop local record')
                            data_manager.stop_local()
                            server_state = STATE_SEND
                            connection.sendall(SYNC)

                        elif server_state == STATE_STORE:
                            log.info('[SERV PROC] Stop local record')
                            data_manager.stop_local()
                            connection.sendall(SYNC)
                            server_state = STATE_RECORD
                        else:
                            log.warn('[SERV PROC] Asked for stop local record while not recording')
                            connection.sendall(SYNC)

                    elif data == STOP_ALL:
                        server_state = STATE_STOPPED
                        cpu.quit()
                        data_manager.quit()
                        log.info('[SERV PROC] Stoppped all threads')
                        connection.sendall(SYNC)
                        break
                    else:
                        log.warn('[SERV PROC] Received non valid client request:' + data)
                else:
                    log.info('[SERV PROC] Received empty data. Exiting server loop'.format(data))
                    break

        except Exception as e:
            write_file(e)
            write_file(e.message)
        finally:
            connection.close()
            soc_ctrl.close()
            log.info('[SERV PROC] end of server task')
    finally:
        pass
