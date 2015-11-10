import numpy as np
import time
import matplotlib
matplotlib.use('GTKAgg')
from matplotlib import pyplot as plt
from helpers import Logger
from conf import *

N_COL = 2
PRINT_AXIS = range(15)

PRINT_LOG_FILE = os.path.join(LOCAL_DATA_DIR, 'printer.log')
log = Logger(PRINT_LOG_FILE, V_DEBUG)

def multi_init_fast(data):
    print_data = {}
    log.verb('Multi print init data: {}'.format(data))
    for target in data:
        print_data[target] = fast_init_single(data[target])
    log.verb('Multi print init has plotted and has drawn')
    return print_data

def fast_init_single(dico):
    n_elem = len(dico)
    log.debug('len({})= {}'.format(dico, n_elem))
    n_col = N_COL

    if n_elem % n_col == 0:
        n_raw = int(n_elem / n_col)
    else:
        n_raw = int(n_elem / n_col) + 1

    fig, ax = plt.subplots(n_raw,n_col)
    fig.show()
    fig.canvas.draw()
    log.debug(fig)

    ind = 0
    keys = dico.keys()
    line_ret = []
    background_ret = []
    ax_ret = []

    for raw in ax:
        if ind >= len(keys):
            log.warn('Odd Breaking while printing')
            break
        for column in raw:
            log.debug('back in loop')
            log.debug('plot title {}'.format(keys[ind]))

            column.set_title(keys[ind])

            line = column.plot([0, 20], [0, 20], animated=True)[0]
            line.set_xdata(PRINT_AXIS)
            line_ret.append(line)

            backgrounds = fig.canvas.copy_from_bbox(column.bbox)
            background_ret.append(backgrounds)

            ax_ret.append(column)
            log.debug([column])

            ind += 1
            if ind >= len(keys):
                log.verb('breaking')
                break
    log.debug([fig])
    fig.canvas.draw()
    fig.canvas.flush_events()
    return fig, ax_ret, line_ret, background_ret

def multi_print_fast(multi_dico, print_data):
    log.verb('Multiprinting: {}'.format(multi_dico))
    for keys in multi_dico:
        print_dic_fast(multi_dico[keys], print_data[keys])

def print_dic_fast(dico, (fig, ax, lines, backgrounds)):
    log.verb('Printing: {}'.format(dico))
    keys = dico.keys()
    for ind in range(len(keys)):
        log.debug('back in loop')

        ### Should do better here
        ydata = dico[keys[ind]]
        xdata = range(len(ydata))
        log.debug('Before drawing')
        fig.canvas.restore_region(backgrounds[ind])
        lines[ind].set_data(xdata,ydata)#
        log.debug([ax[ind]])
        log.debug([fig])
        ax[ind].draw_artist(lines[ind])
        fig.canvas.blit(ax[ind].bbox)
        log.debug('Has drawn data {}'.format(lines[ind].get_data()))

        #column.set_title(keys[ind])
        if ind >= len(keys):
            log.verb('breaking')
            break











###
###     Old non optimized printing utilities
###     Should refactor input to match data_processor client workflow
###

def multi_init_print(data):
    log.info('Init multi printing')
    plt.ion()
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

def init_print(dico):
    log.info('Init single printing')
    plt.ion()
    log.verb('Print init data: {}'.format(dico))
    n_elem = len(dico)
    log.debug('len({})={}'.format(target, n_elem))
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


def multi_print_dic(multi_dico, multi_ax, multi_fig):
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







def test_print_time():
    dic_1 = {   'mem_size21':range(10),
                'mem_size345':range(10),
                'mem_size43':range(10),
                'mem_size23':range(10),
                'mem_size2':range(10),
                'mem_size1':range(10),
    }

    dic_2 = {   'mem_size21':range(10),
                'mem_size345':range(10),
                'mem_size43':range(10),
                'mem_size23':range(10),
                'mem_size2':range(10),
                'mem_size1':range(5),
                'mem_size1':range(48),
                'mem_info':[23,45,86,587],
    }

    multi_dic = {'dic_1':dic_1, 'dic_2':dic_2, 'dic_3':dic_1}

    def add_elem(dic):
        for key in dic:
            dic[key].append(5)
    type = 'non_fast'
    iter = 5

    if type == 'fast':
        print_data = multi_init_fast(multi_dic)
        for i in range(iter):
            for key in multi_dic:
                add_elem(multi_dic[key])
            start = time.time()
            multi_print_fast(multi_dic, print_data)
            stop = time.time()
            print stop - start


    else:
        fig, ax = multi_init_print(multi_dic)
        for i in range(iter):
            for key in multi_dic:
                add_elem(multi_dic[key])
            start = time.time()
            multi_print_dic(multi_dic, ax, fig)
            stop = time.time()
            print stop - start

    #raw_input()

if __name__ == '__main__':
    test_print_time()

