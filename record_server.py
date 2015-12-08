from cpu_load import CPUWatcher
from data_manager import DataManager
from conf import *
from helpers import *

import argparse, time, os, sys
import socket, select
import Queue

def parserArguments(parser):
    parser.add_argument('--proc' , dest = 'processes', nargs='*', default = ['naoqi-service'], help = 'processes to watch')
    parser.add_argument('--tout' , dest = 'timeout', type = int, default = '10000' , help = 'timeout in seconds')
    parser.add_argument('--step' , dest = 'step', type = int, default = '1' , help = 'period of recording in seconds')
    parser.add_argument('--rec' , dest = 'rec', nargs='*', default = ['local', 'remote'] , help = 'record mode, can be local or remote')
    parser.add_argument('--verb', '-v' , dest = 'v', type = int, default = V_DEBUG , help = 'record mode, can be local or remote')

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

####
####    GLOBALS
####
log = Logger(SERV_LOG_FILE, D_VERB)
log.info('[SERV PROC] Server is launched')
data                = Queue.Queue()
headers             = define_headers()
connection_table    = {}
cpu = CPUWatcher(headers, data)
log.info('[SERV PROC] CPU Thread instantiated')
data_manager = DataManager(headers, data, connection_table)
log.info('[SERV PROC] DATA Thread instantiated')

####
####    ServerFunctions
####
def start_record(connection, msg):
    target = msg[2]
    client_address = connection.getpeername()
    if target not in connection_table[connection]:
        allready_recording = False
        for clients in connection_table:
            if target in connection_table[clients]:
                allready_recording = True
        log.debug('[SERV PROC] {} should_ask_start = {}'.format(client_address, allready_recording))
        if allready_recording:
            append_process =  True
        else:
            append_process = cpu.start(target)
        log.debug('[SERV PROC] {} append_process = {}'.format(client_address, append_process))
        if append_process:
            connection_table[connection].append(target)
            log.debug('[SERV PROC] {} appended {}'.format(client_address, target))
    else:
        log.warn('[SERV PROC] {} Asked to start record {} while already recording'.format(client_address, target))
        append_process = False
    if append_process:
        return SYNC
    else:
        return FAIL

def stop_record(connection, msg):
    target = msg[2]
    client_address = connection.getpeername()
    if target in connection_table[connection]:
        should_ask_stop = True
        for clients in connection_table:
            if clients is not connection:
                if target in connection_table[clients]:
                    should_ask_stop = False
        log.debug('[SERV PROC] {} should_ask_stop = {}'.format(connection.getpeername(), should_ask_stop))
        if should_ask_stop:
            should_remove = cpu.stop(target)
        else:
            should_remove = True
        if should_remove:
            connection_table[connection].remove(target)
            log.debug('[SERV PROC] {} removed {}'.format(connection.getpeername(), target))
    else:
        log.warn('[SERV PROC] {} Asked to stop record {} while not recording. Actual recordings are {}'.format(client_address, msg, connection_table[connection]))
        should_remove = False
    if should_remove:
        return SYNC
    else:
        return FAIL

def start_send(connection, msg):
    data_manager.start_send()
    return SYNC

def stop_send(connection, msg):
    data_manager.stop_send()
    return SYNC

#### Not implemented yet
def exit(connection, msg):
    return SYNC

def start_store(connection, msg):
    return SYNC

def stop_store(connection, msg):
    return SYNC

####
####    Handles different client messages
####
messages = {
    STOP_ALL        : exit,
    START_RECORD    : start_record,
    STOP_RECORD     : stop_record,
    START_SEND      : start_send,
    STOP_SEND       : stop_send,
    START_STORE     : start_store,
    STOP_STORE      : stop_store,
}

def treat_data(connection, data):
    client_address = connection.getpeername()
    if connection in connection_table:
        msg = data.split(MSG_SEP)
        if msg[0] in messages:
            log.debug('[SERV PROC] Received msg {} from {}'.format(msg, client_address))
            function = messages[msg[0]]
            answer = function(connection, msg)
        else:
            log.warn('[SERV PROC] {} sent invalid message {}'.format(client_address, msg))
            answer = FAIL
    else:
        log.error('[SERV PROC] {} Asked to start recording while not in connection table'.format(client_address))
        answer = FAIL
    return answer



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'dialog_cpu_stats')
    parserArguments(parser)
    args = parser.parse_args()
    adict = vars(args)

    if not os.path.isdir(NAO_DATA_DIR):
        os.makedirs(NAO_DATA_DIR)

    server_state = STATE_IDLE
    server_data_sockets = []


    # Waits for a client connection
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setblocking(0)
    server.bind(('', SOC_PORT_CTRL))
    server.listen(5)

    inputs = [ server ]
    outputs = [ ]
    message_queues = {}

    try:
        while inputs:
            readable, writable, exceptional = select.select(inputs, outputs, inputs)
            log.debug('[SERV PROC] Select triggered. readable: {} , writable: {}, exceptional: {}'.format([r.getpeername() if r is not server else 'server' for r in readable ],
                                                                                                          [w.getpeername() if w is not server else 'server'for w in writable],
                                                                                                          [e.getpeername() if e is not server else 'server' for e in exceptional]))
            for s in readable:
                ###
                ###     New client connection
                ###
                if s is server:
                    connection, client_address = s.accept()
                    log.info('[SERV PROC] New connection made by client {}'.format(client_address))
                    connection.setblocking(0)
                    inputs.append(connection)
                    if connection not in connection_table:
                        connection_table[connection] = []
                        log.verb('[SERV PROC] Client address {} added to connection_table'.format(client_address))
                    else:
                        log.warn('[SERV PROC] Client address {} already in connection_table'.format(client_address))
                    log.debug('[SERV PROC] connection_table is now {}'.format(connection_table))

                ###
                ###     Client Message
                ###
                else:
                    data = s.recv(1024)
                    log.debug('[SERV PROC] {} received {}'.format(s.getpeername(), data))

                    # Client request
                    if data:
                        answer = treat_data(s, data)
                        log.debug('[SERV PROC] answer to {} will be {}. Server state is now {}'.format(s, answer, server_state))
                        message_queues[s] = answer
                        outputs.append(s)

                    # Client disconnection
                    else:
                        log.info('[SERV PROC] {} closed socket connection'.format(s))
                        log.debug('[SERV PROC] Connection table is now {}'.format(connection_table))
                        if s in connection_table:
                            log.debug('[SERV PROC] Targets to remove are {}'.format(connection_table[s]))
                            for target in connection_table[s][:]:
                                stop_record(cpu, s, target)
                            del connection_table[s]
                            log.debug('[SERV PROC] Connection has been closed')
                        if s in outputs:
                            outputs.remove(s)
                        inputs.remove(s)
                        s.close()
                        log.debug('[SERV PROC] Remaining connections are {}.'.format(connection_table))

            # Answer to client
            for s in writable:
                s.sendall(message_queues[s])
                message_queues[s] = None
                outputs.remove(s)
    finally:
        log.info('[SERV PROC] end of server main loop')
        server.close()


