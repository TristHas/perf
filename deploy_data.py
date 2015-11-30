#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.api import run, cd, env, put, get
import argparse, time
from conf import *



def init_server_session(ip = IP_1, no_run = False):
    env.user        = LOGIN
    env.password    = PWD
    env.host_string = ip
    clean_server()
    run("mkdir {}".format(NAO_WORK_DIR))
    run("mkdir {}".format(NAO_DATA_DIR))

    local_cpu_file = os.path.join(LOCAL_WORK_DIR, 'cpu_load.py')
    local_server_file = os.path.join(LOCAL_WORK_DIR, 'record_server.py')
    conf_file = os.path.join(LOCAL_WORK_DIR, 'conf.py')
    data_file = os.path.join(LOCAL_WORK_DIR, 'data_manager.py')
    helper_file = os.path.join(LOCAL_WORK_DIR, 'helpers.py')
    put(local_cpu_file, NAO_WORK_DIR)
    put(local_server_file, NAO_WORK_DIR)
    put(conf_file, NAO_WORK_DIR)
    put(data_file, NAO_WORK_DIR)
    put(helper_file, NAO_WORK_DIR)
    if not no_run:
        run('python /home/nao/bench_dialog/record_server.py < /dev/null > /dev/null 2>&1 &', pty = False)
        print 'Has run server'
    else:
        print 'not running server'
    time.sleep(2)       # Give time to server for launch


def clean_server():
    folders = run("ls {}".format(NAO_HOME))
    if "bench_dialog" in folders:
        run('rm -r {}'.format(NAO_WORK_DIR))

    if "bench_data" in folders:
        run('rm -r {}'.format(NAO_DATA_DIR))

def parserArguments(parser):
    parser.add_argument('--clean', '-c', dest = 'clean', action = 'store_true', help = 'Cleans remote HOME. If not specified uploads files')
    parser.add_argument('--no_run', '-n', dest = 'no_run', action = 'store_true', help = 'Does not run the server')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'dialog_cpu_stats')
    parserArguments(parser)
    args = parser.parse_args()
    adict = vars(args)
    if adict['clean']:
        clean_server()
    else:
        init_server_session(no_run = adict['no_run'])
