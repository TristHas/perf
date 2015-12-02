#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.api import run, cd, env, put, get
import argparse, time
from conf import *

def init_server_session(ip = IP_1, no_run = False):
    deploy_server(ip)
    if not no_run:
        run_server(ip)
        print 'Has run server'
    else:
        print 'not running server'
    time.sleep(2)       # Give time to server for launch

def deploy_server(ip = IP_1):
    env.user        = LOGIN
    env.password    = PWD
    env.host_string = ip
    clean_server(ip)
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

def run_server(ip = IP_1):
    env.user        = LOGIN
    env.password    = PWD
    env.host_string = ip
    run('python /home/nao/bench_dialog/record_server.py < /dev/null > /dev/null 2>&1 &', pty = False)

def kill_server(ip = IP_1):
    env.user        = LOGIN
    env.password    = PWD
    env.host_string = ip
    x = run('ps aux | grep record_server.py')
    y = x.split('\n')
    pid = y[0].split()[1]
    if len(y) == 3:
        run('kill -9 {}'.format(pid))
        print 'has killed {}'.format(y[0].split()[-1])
    else:
        print 'Nothing has been killed'

def clean_server(ip = IP_1):
    env.user        = LOGIN
    env.password    = PWD
    env.host_string = ip

    folders = run("ls {}".format(NAO_HOME))
    if "bench_dialog" in folders:
        run('rm -r {}'.format(NAO_WORK_DIR))

    if "bench_data" in folders:
        run('rm -r {}'.format(NAO_DATA_DIR))

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
        env.user        = LOGIN
        env.password    = PWD
        # FIXME: To be changed to handle multiple deploy IPs
        env.host_string = adict['ip'][0]

    if adict['deploy']:
        deploy_server()
    if adict['run']:
        run_server()
    if adict['kill']:
        kill_server()
    if adict['clean']:
        clean_server()
    if not (adict['clean'] or adict['kill'] or adict['deploy'] or adict['run']):
        parser.error("""Please specify valid options to the script.
                        You can display options function with -h""")
