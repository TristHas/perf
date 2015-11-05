# No need
# Same
from cpu_load import CPUWatcher
from data_manager import DataManager
import argparse, time, os, sys
from conf import *
# New
import socket
import threading
import json


f_err = open(SERV_LOG_ERROR, 'w')
f_out = open(SERV_LOG_INFO,'w')
f_in = open('/dev/null')
#sys.stderr = f_err

def write_file(mess):
    print >> f_out, mess
    f_out.flush()
    os.fsync(f_out)

def parserArguments(parser):
    parser.add_argument('--proc' , dest = 'processes', nargs='*', default = [], help = 'processes to watch')
    parser.add_argument('--tout' , dest = 'timeout', type = int, default = '10000' , help = 'timeout in seconds')
    parser.add_argument('--step' , dest = 'step', type = int, default = '1' , help = 'period of recording in seconds')
    parser.add_argument('--rec' , dest = 'rec', nargs='*', default = ['local', 'remote'] , help = 'record mode, can be local or remote')
    parser.add_argument('--verbose', '-v' , dest = 'v', type = int, default = 1 , help = 'record mode, can be local or remote')

def data_send(cpu, adict):
    soc_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc_data.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc_data.bind((SOC_ADR_REMOTE, SOC_PORT_DATA))
    soc_data.listen(1)
    if adict['v'] >= V_DEBUG:
        write_file('[DATA THREAD] Awaiting for connection')
    connection, client_address = soc_data.accept()
    if adict['v'] >= V_INFO:
        write_file('[DATA THREAD] Conection accepted')
    while True:
        data = connection.recv(32)
        if adict['v'] >= V_DEBUG:
            write_file('[DATA THREAD] received {}'.format(data))
        break

    while True:
        end_count = 0
        queue_mess = cpu.transmit.get()
        if queue_mess != 'end':
            mess = json.dumps(queue_mess)
            if adict['v'] >= V_DEBUG:
                write_file('[DATA THREAD] Sending {}'.format(mess))
            send_data(connection, mess)
        else:
            if adict['v'] >= V_DEBUG:
                write_file('[DATA THREAD] Sending end. Breaking')
            send_data(connection, 'end')
            break
    if adict['v'] >= V_INFO:
        write_file('[DATA THREAD] End of execution')

def send_data(soc, mess):
    soc.sendall(mess)
    while True:
        data = soc.recv(8)
        if data == SYNC:
            break
        if data == FAIL:
            break
    return data

server_state = STATE_IDLE
server_data_sockets = []

if __name__ == '__main__':
    try:
        write_file('[SERV PROC] Server is launched')
        parser = argparse.ArgumentParser(description = 'dialog_cpu_stats')
        parserArguments(parser)
        args = parser.parse_args()
        adict = vars(args)

        if adict['v'] >= V_DEBUG:
            write_file(adict)

        # Create data directory
        if not os.path.isdir(NAO_DATA_DIR):
            os.makedirs(NAO_DATA_DIR)

        # Waits for a client connection
        soc_ctrl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc_ctrl.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc_ctrl.bind((SOC_ADR_REMOTE, SOC_PORT_CTRL))
        soc_ctrl.listen(1)

        ###
        ###     Add handling of multiple connections?
        ###
        connection, client_address = soc_ctrl.accept()
        write_file('[SERV PROC] Connection made by client')

        # Instantiate CPUWatcher
        cpu = CPUWatcher(adict)
        write_file('[SERV PROC] CPU Thread instantiated')
        data_manager = DataManager(adict, cpu)
        write_file('[SERV PROC] DATA Thread instantiated')

        try:
            while True:
                write_file('[SERV PROC] Back in loop')
                data = connection.recv(32)
                if adict['v'] >= V_DEBUG:
                    write_file('[SERV PROC] received {}'.format(data))
                if data:
                    if data == START_RECORD:
                        if server_state == STATE_IDLE:
                            cpu.start()
                            server_state = STATE_RECORD
                            if adict['v'] >= V_INFO:
                                write_file('[SERV PROC] send start command')
                            connection.sendall(SYNC)
                        else:
                            if adict['v'] >= V_INFO:
                                write_file('[SERV PROC] start command asked but state non idle')
                            connection.sendall(SYNC)

                    elif data == STOP_RECORD:
                        if server_state <= STATE_RECORD:
                            if adict['v'] >= V_INFO:
                                write_file('[SERV PROC] Stop command, record is stopped')
                            cpu.stop()
                            server_state = STATE_IDLE
                            connection.sendall(SYNC)
                        else:
                            if adict['v'] >= V_INFO:
                                write_file('[SERV PROC] Stop command, record is stopped')
                            cpu.stop()
                            connection.sendall(FAIL)

                    elif data == START_SEND:
                        if server_state == STATE_IDLE:
                            connection.sendall(FAIL)
                            if adict['v'] >= V_INFO:
                                write_file('[SERV PROC] Asked for send while idle')
                        elif server_state >= STATE_SEND:
                            write_file('[SERV PROC] Sending already')
                            connection.sendall(SYNC)
                        else:
                            data_manager.start_send()
                            if adict['v'] >= V_INFO:
                                write_file('[SERV PROC] Starts sending. Wait for connections')
                            if server_state == STATE_RECORD:
                               server_state = STATE_SEND
                            if server_state == STATE_STORE:
                                server_state = STATE_FULL
                            connection.sendall(SYNC)

                    elif data == STOP_SEND:
                        if server_state < STATE_SEND:
                            if adict['v'] >= V_INFO:
                                write_file('[SERV PROC] Asked for stop send command while not sending')
                                connection.sendall(FAIL)
                        else:
                            if adict['v'] >= V_INFO:
                                write_file('[SERV PROC] Stop record')
                            data_manager.stop_send()
                            if server_state == STATE_SEND:
                               server_state = STATE_RECORD
                            if server_state == STATE_FULL:
                                server_state = STATE_STORE
                            connection.sendall(SYNC)

                    elif data == START_STORE:
                        if server_state == STATE_IDLE:
                            if adict['v'] >= V_INFO:
                                write_file('[SERV PROC] Asked for local store while idle')
                            connection.sendall(FAIL)
                        elif server_state == STATE_FULL or server_state == STATE_STORE:
                            if adict['v'] >= V_INFO:
                                write_file('[SERV PROC] Asked for local store while already recording')
                            connection.sendall(SYNC)
                        else:
                            if adict['v'] >= V_INFO:
                                write_file('[SERV PROC] Start local record')
                            data_manager.start_local()
                            if server_state == STATE_RECORD:
                                server_state = STATE_STORE
                            else:
                                server_state = STATE_FULL
                            connection.sendall(SYNC)

                    elif data == STOP_STORE:
                        if server_state == STATE_FULL:
                            if adict['v'] >= V_INFO:
                                write_file('[SERV PROC] Stop local record')
                            data_manager.stop_local()
                            server_state = STATE_SEND
                            connection.sendall(SYNC)

                        elif server_state == STATE_STORE:
                            if adict['v'] >= V_INFO:
                                write_file('[SERV PROC] Stop local record')
                            data_manager.stop_local()
                            connection.sendall(SYNC)
                            server_state = STATE_RECORD
                        else:
                            if adict['v'] >= V_INFO:
                                write_file('[SERV PROC] Asked for stop local record while not recording')
                            connection.sendall(SYNC)

                    elif data == STOP_ALL:
                        server_state = STATE_STOPPED
                        cpu.quit()
                        data_manager.quit()
                        if adict['v'] >= V_INFO:
                            write_file('[SERV PROC] Stoppped all threads')
                        connection.sendall(SYNC)
                        break
                    else:
                        if adict['v'] >= V_INFO:
                            write_file('[SERV PROC] Received non valid client request:' + data)
                else:
                    if adict['v'] >= V_DEBUG:
                        write_file('[SERV PROC] Received empty data. Exiting server loop'.format(data))
                    break
        except Exception as e:
            write_file(e)
            write_file(e.message)
        finally:
            connection.close()
            soc_ctrl.close()
            if adict['v'] >= V_INFO:
                write_file('[SERV PROC] end of server task')
    finally:
        f_err.close()
        f_out.close()
        f_in.close()
