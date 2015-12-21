import numpy as np
import time, csv
import matplotlib
from matplotlib import pyplot as plt
from helpers import Logger
from conf import *

N_COL = 2
PRINT_AXIS = range(15)
log = Logger(PRINT_CLIENT_LOG_FILE, D_VERB)

###
###     Non Dynamic prints
###

def print_file(file_path):
    with open(file_path) as csvfile:
        reader = csv.DictReader(csvfile)
        if os.path.basename(file_path) == 'system':
            headers = SYS_CPU_OTHER + LOAD_AVG + SYS_CPU_DATA + SYS_MEM_DATA
        else:
            headers =PROC_CPU_DATA + PROC_MEM_DATA
        print_data = {}
        for elem in headers:
            print_data[elem] = []
        print headers
        for row in reader:
            for elem in headers:
                print_data[elem].append(row[elem])
        for elem in headers:
            print 'print_data[{}]={}'.format(elem,print_data[elem])
        static_print(print_data)

def static_print(dico):
    n_elem = len(dico)
    n_col = N_COL
    if n_elem % n_col == 0:
        n_raw = int(n_elem / n_col)
    else:
        n_raw = int(n_elem / n_col) + 1
    fig, ax = plt.subplots(n_raw,n_col)
    log.info('Subplots are {} by {}'.format(n_raw, n_col))
    log.verb('Printing: {}'.format(dico))
    keys = dico.keys()
    ind = 0
    for raw in ax:
        if ind >= len(keys):
            log.warn('Odd Breaking while printing')
            break
        for column in raw:
            log.debug('back in loop')
            log.debug('plot {}'.format(dico[keys[ind]]))
            column.plot(dico[keys[ind]])
            column.set_title(keys[ind])
            ind += 1
            if ind >= len(keys):
                log.verb('breaking')
                break
    plt.show()


###
###     Old non optimized printing utilities
###     Should refactor input to match data_processor client workflow
###
def multi_init_print(data):
    log.info('Init multi printing')
    fig_ret = []
    ax_ret = []
    log.verb('Multi print init data: {}'.format(data))
    for target in data:
        n_elem = len(data[target])
        log.debug('len({})= {}'.format(target, n_elem))
        n_col = N_COL
        if n_elem % n_col == 0:
            n_raw = int(n_elem / n_col)
        else:
            n_raw = int(n_elem / n_col) + 1
        fig, ax = plt.subplots(n_raw,n_col)
        log.info('Subplots for {} are {} by {}'.format(target, n_raw, n_col))
        fig_ret.append(fig)
        ax_ret.append(ax)
    plt.show(False)
    plt.draw()
    log.verb('Multi print init has plotted and has drawn')
    return fig_ret, ax_ret

def clear_print():
    plt.close('all')


def init_print(dico):
    log.info('Init single printing')
    plt.ion()
    log.verb('Print init data: {}'.format(dico))
    n_elem = len(dico)
    log.debug('len({})={}'.format(dico, n_elem))
    n_col = N_COL
    if n_elem % n_col == 0:
        n_raw = int(n_elem / n_col)
    else:
        n_raw = int(n_elem / n_col) + 1
    fig, ax = plt.subplots(n_raw,n_col)
    log.info('Subplots are {} by {}'.format(n_raw, n_col))
    plt.show(False)
    plt.draw()
    return fig, ax


def multi_print_dic(multi_dico, (multi_fig, multi_ax)):
    log.verb('Multiprinting: {}'.format(multi_dico))
    for dico, ax, fig in zip(multi_dico, multi_ax, multi_fig):
        print_dic(multi_dico[dico], ax, fig)

def print_dic(dico, ax, fig):
    log.verb('Printing: {}'.format(dico))
    keys = dico.keys()
    ind = 0
    for raw in ax:
        if ind >= len(keys):
            log.warn('Odd Breaking while printing')
            break
        for column in raw:
            log.debug('back in loop')
            log.debug('plot {}'.format(dico[keys[ind]]))
            column.plot(dico[keys[ind]])
            column.set_title(keys[ind])
            ind += 1
            if ind >= len(keys):
                log.verb('breaking')
                break
    log.verb('Before drawing')
    fig.canvas.draw()
    log.verb('Has drawn')


###
###     Filename should be passed as parameter
###

if __name__ == '__main__':
    print_file('/tmp/bench_dialog/data/long_life_run 10.0.132.89/naoqi-service')
