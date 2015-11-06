#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.api import run, cd, env, put, get
import argparse, time
from conf import *

env.host_string = IP_1
env.user        = LOGIN
env.password    = PWD

def init_session():
    folders = run("ls {}".format(NAO_HOME))
    if "bench_dialog" in folders:
        run('rm -r {}'.format(NAO_WORK_DIR))

    if "bench_data" in folders:
        run('rm -r {}'.format(NAO_DATA_DIR))

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
    run('python /home/nao/bench_dialog/record_server.py < /dev/null > /dev/null 2>&1 &', pty = False)
    time.sleep(2)       # Give time to server for launch
    print 'Has run server'

def clean():
    folders = run("ls {}".format(NAO_HOME))
    if "bench_dialog" in folders:
        run('rm -r {}'.format(NAO_WORK_DIR))

    if "bench_data" in folders:
        run('rm -r {}'.format(NAO_DATA_DIR))

def parserArguments(parser):
    parser.add_argument('--clean', '-c', dest = 'clean', action = 'store_true', help = 'Cleans remote HOME. If not specified uploads files')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'dialog_cpu_stats')
    parserArguments(parser)
    args = parser.parse_args()
    adict = vars(args)
    if adict['clean']:
        clean()
    else:
        init_session()
