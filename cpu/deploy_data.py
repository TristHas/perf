#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.api import run, cd, env, put, get
import argparse, time, os
from conf import *

def deploy_server(ip):
    env.user        = LOGIN
    env.password    = PWD
    env.host_string = ip
    clean_server(ip)

    run("mkdir {}".format(ROOT_DIR))
    run("mkdir {}".format(WORK_DIR))
    run("mkdir {}".format(DATA_DIR))
    run("mkdir {}".format(LOG_DIR))

    local_work_dir = os.path.dirname(os.path.abspath(__file__))
    local_cpu_file = os.path.join(local_work_dir, 'cpu_load.py')
    local_server_file = os.path.join(local_work_dir, 'record_server.py')
    conf_file = os.path.join(local_work_dir, 'conf.py')
    data_file = os.path.join(local_work_dir, 'data_manager.py')
    helper_file = os.path.join(local_work_dir, 'helpers.py')

    put(local_cpu_file, WORK_DIR)
    put(local_server_file, WORK_DIR)
    put(conf_file, WORK_DIR)
    put(data_file, WORK_DIR)
    put(helper_file, WORK_DIR)

def run_server(ip):
    env.user        = LOGIN
    env.password    = PWD
    env.host_string = ip
    run('python {}/record_server.py < /dev/null > /dev/null 2>&1 &'.format(WORK_DIR), pty = False)
    time.sleep(2)

def kill_server(ip):
    env.user        = LOGIN
    env.password    = PWD
    env.host_string = ip
    x = run('ps aux | grep record_server.py')
    y = x.split('\n')
    pid = y[0].split()[1]
    if len(y) == 3:
        run('kill -9 {}'.format(pid))

def clean_server(ip):
    env.user        = LOGIN
    env.password    = PWD
    env.host_string = ip
    folders = run("ls {}".format(PARENT_DIR))
    if DIR_NAME in folders:
        run('rm -r {} > /dev/null 2>&1'.format(ROOT_DIR))


def parserArguments(parser):
    parser.add_argument('--clean', '-c', dest = 'clean', action = 'store_true', help = 'Cleans remote HOME')
    parser.add_argument('--kill', '-k', dest = 'kill', action = 'store_true', help = 'kills the server')
    parser.add_argument('--run', '-r', dest = 'run', action = 'store_true', help = 'runs the server')
    parser.add_argument('--deploy', '-d', dest = 'deploy', action = 'store_true', help = 'deploys the server files')
    parser.add_argument('--ip', '-i', dest = 'ip', nargs='*', default = [], help = 'IP concerned')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'dialog_cpu_stats')
    parserArguments(parser)
    args = parser.parse_args()
    adict = vars(args)
    if adict['ip']:
        ip = adict['ip'][0]
    if adict['kill']:
        kill_server(ip)
    if adict['clean']:
        clean_server(ip)
    if adict['deploy']:
        deploy_server(ip)
    if adict['run']:
        run_server(ip)

    if not (adict['ip'] and (adict['clean'] or adict['kill'] or adict['deploy'] or adict['run'])):
        parser.error("""Please specify valid options to the script.
                        You can display options function with -h""")
