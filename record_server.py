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


###
###     FIXME: Send error message to the client when the process can't be found
###
def start_record(cpu, connection, target):
    should_ask_start = True
    for clients in connection_table:
        if target in connection_table[clients]:
            should_ask_start = False
    log.debug('[SERV PROC] {} should_ask_start = {}'.format(connection.getpeername(), should_ask_start))
    if should_ask_start:
        should_append = cpu.start(target)
    else:
        should_append =  True
    if should_append:
        connection_table[connection].append(target)
        log.debug('[SERV PROC] {} appended {}'.format(connection.getpeername(), target))

def stop_record(cpu, connection, target):
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

connection_table = {}

def treat_data(data, connection, cpu, data_manager, server_state):
    if data.startswith(START_RECORD):
        client_address = connection.getpeername()
        if connection in connection_table:
            msg = data.split(MSG_SEP)
            log.debug('[SERV PROC] Received msg {} from {}'.format(msg, client_address))
            if msg[2] not in connection_table[connection]:
                start_record(cpu, connection, msg[2])
            else:
                log.warn('[SERV PROC] {} Asked to start record {} while already recording'.format(client_address, msg[2]))
            server_state = STATE_RECORD                                 ### Got to do smt else here
            return server_state, SYNC
        else:
            log.error('[SERV PROC] {} Asked to start recording while not in connection table'.format(connection.getpeername()))
            return server_state, FAIL

    elif data.startswith(STOP_RECORD):
        client_address = connection.getpeername()
        if connection in connection_table:
            msg = data.split(MSG_SEP)
            log.debug('[SERV PROC] Received msg {}'.format(msg))
            if msg[2] in connection_table[connection]:
                log.verb('[SERV PROC] Received msg {}'.format(msg))
                stop_record(cpu, connection, msg[2])
                server_state = STATE_RECORD
                return server_state, SYNC
            else:
                log.warn('[SERV PROC] {} Asked to stop record {} while not recording. Actual recordings are {}'.format(client_address, msg, connection_table[connection]))
                return server_state, SYNC
        else:
            log.error('[SERV PROC] {} Asked to start recording while not in connection table'.format(connection.getpeername()))
            return server_state, FAIL

    elif data == START_SEND:
        if server_state < STATE_RECORD:
            return server_state, FAIL
        else:
            data_manager.start_send()
            if server_state == STATE_RECORD:
               server_state = STATE_SEND
            if server_state == STATE_STORE:
                server_state = STATE_FULL
            return server_state, SYNC

    elif data == STOP_SEND:
        if server_state < STATE_SEND:
            return server_state, FAIL
        else:
            data_manager.stop_send()
            if server_state == STATE_SEND:
               server_state = STATE_RECORD
            if server_state == STATE_FULL:
                server_state = STATE_STORE
            return server_state, SYNC

    elif data == START_STORE:
        if server_state == STATE_IDLE:
            return server_state, FAIL
        elif server_state == STATE_FULL or server_state == STATE_STORE:
            return server_state, SYNC
        else:
            data_manager.start_local()
            if server_state == STATE_RECORD:
                server_state = STATE_STORE
            else:
                server_state = STATE_FULL
            return server_state, SYNC

    elif data == STOP_STORE:
        if server_state == STATE_FULL:
            data_manager.stop_local()
            server_state = STATE_SEND
            return server_state, SYNC

        elif server_state == STATE_STORE:
            data_manager.stop_local()
            return server_state, SYNC
            server_state = STATE_RECORD
        else:
            return server_state, SYNC

    elif data == STOP_ALL:
        server_state = STATE_STOPPED
        cpu.quit()
        data_manager.quit()
        return server_state, SYNC
    else:
        print 'non valid data'
        return server_state, FAIL


if __name__ == '__main__':
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
    headers = define_headers()
    data    = Queue.Queue()

    # Waits for a client connection
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setblocking(0)
    server.bind(('', SOC_PORT_CTRL))
    server.listen(5)

    ###
    ###     Add handling of multiple connections?
    ###
    inputs = [ server ]
    outputs = [ ]
    message_queues = {}

    # Instantiate CPUWatcher
    cpu = CPUWatcher(adict, headers, targets, data)
    log.info('[SERV PROC] CPU Thread instantiated')
    data_manager = DataManager(adict, headers, targets, data)
    log.info('[SERV PROC] DATA Thread instantiated')

    try:
        while inputs:
            readable, writable, exceptional = select.select(inputs, outputs, inputs)
            log.debug('[SERV PROC] Select triggered. readable: {} , writable: {}, exceptional: {}'.format([r.getpeername() if r is not server else 'server' for r in readable ],
                                                                                                          [w.getpeername() if w is not server else 'server'for w in writable],
                                                                                                          [e.getpeername() if e is not server else 'server' for e in exceptional]))
            for s in readable:
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
                else:
                    data = s.recv(1024)
                    log.debug('[SERV PROC] {} received {}'.format(s.getpeername(), data))
                    if data:
                        server_state, answer = treat_data(data, s, cpu, data_manager, server_state)
                        log.debug('[SERV PROC] answer to {} will be {}. Server state is now {}'.format(s, answer, server_state))
                        message_queues[s] = answer
                        outputs.append(s)
                    else:
                        log.info('[SERV PROC] Received empty data. Closing connection')
                        log.info('[SERV PROC] Connection  is  {}'.format(s))
                        log.info('[SERV PROC] Connection table is now {}'.format(connection_table))
                        if s in connection_table:
                            for target in connection_table[s]:
                                stop_record(cpu, s, target)
                            del connection_table[s]
                            log.debug('[SERV PROC] Connection has been closed')
                        if s in outputs:
                            outputs.remove(s)
                        inputs.remove(s)
                        s.close()
                        log.debug('[SERV PROC] Remaining connections are {}.'.format(connection_table))

            for s in writable:
                s.sendall(message_queues[s])
                message_queues[s] = None
                outputs.remove(s)
    finally:
        log.info('[SERV PROC] end of server main loop')
        server.close()


