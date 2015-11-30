import numpy as np
import time
import matplotlib
#matplotlib.use('GTKAgg')
from matplotlib import pyplot as plt
from helpers import Logger
from conf import *

N_COL = 2
PRINT_AXIS = range(15)

PRINT_LOG_FILE = os.path.join(LOCAL_DATA_DIR, 'printer.log')
log = Logger(PRINT_LOG_FILE, V_INFO)

def multi_init_fast(data):
    print_data = {}
    log.verb('Multi print init data: {}'.format(data))
    for target in data:
        print_data[target] = fast_init_single(data[target])
    log.verb('Multi print init has plotted and has drawn')
    return print_data

def fast_init_single(dico):
    n_elem = len(dico)
    log.debug('init dico: {}'.format(dico))
    n_col = N_COL
    if n_elem % n_col == 0:
        n_raw = int(n_elem / n_col)
    else:
        n_raw = int(n_elem / n_col) + 1
    fig, ax = plt.subplots(n_raw,n_col)
    fig.set_size_inches(15, 10, forward=True)
    fig.show()
    fig.canvas.draw()
    ind = 0
    keys = dico.keys()
    background_ret = []
    ax_ret = []
    for raw in ax:
        if ind >= len(keys):
            log.warn('Odd Breaking while printing')
            break
        for column in raw:
            log.debug('plot title {}'.format(keys[ind]))
            column.set_title(keys[ind])
            # Set y axis length
            column.yaxis.set_view_interval(0,PRINT_TIC)
            #Create base line object
            column.plot(np.zeros(PRINT_TIC), np.zeros(PRINT_TIC), animated=True)    # x_data should be range(PRINT_TIC))
                                                                                    # But bug observed, when initialized with this, then
                                                                                    # we can't adjust the view_interval.
                                                                                    # Because of data_interval value?
            log.debug('line data: {}'.format(column.lines[0].get_data()))
            # Cache background
            #column.bbox.union([label.get_window_extent() for label in column.get_xticklabels()])
            backgrounds = fig.canvas.copy_from_bbox(column.bbox.expanded(1.2,1.2))#column.bbox.union([label.get_window_extent() for label in column.get_xticklabels()]))

            background_ret.append(backgrounds)
            # Flattens axes
            ax_ret.append(column)
            ind += 1
            if ind >= len(keys):
                log.verb('breaking')
                break
    fig.canvas.draw()
    fig.canvas.flush_events() # Not sure what this does, is it necessary?
    return fig, ax_ret, background_ret

def multi_print_fast(multi_dico, print_data):
    log.verb('Multiprinting: {}'.format(multi_dico))
    for keys in multi_dico:
        print_dic_fast(multi_dico[keys], print_data[keys])

def print_dic_fast(dico, (fig, ax, backgrounds)):
    log.verb('Printing: {}'.format(dico))
    keys = dico.keys()
    for ind in range(len(keys)):
        line = ax[ind].lines[0]

        # Set data
        ydata = dico[keys[ind]]
        xdata = range(len(ydata))                                       # Should not need xdata if fixed input
        #print 'len(xdata)={}'.format(len(xdata))

        ax[ind].xaxis.set_view_interval(0, len(xdata))                 # Should not need if fixed-size input
        #print ax[ind].xaxis.get_view_interval()

        if ydata[-1] > ax[ind].yaxis.get_view_interval()[1]:            # If added value exceed the printing box vertical limit
            ax[ind].yaxis.set_view_interval(0, 1.2 * ydata[-1] )        # Augment printing box vertical limit

        log.debug('Before drawing')
        fig.canvas.restore_region(backgrounds[ind])
        line.set_data(xdata,ydata)
        # Should draw the tics. The following lines does not print the values on the side. What artist handles it?
        # It seems that draw_artist(y_axis) should do it but ax.bbox needs to be enlarged to contain the labels. CF init
        ax[ind].draw_artist(ax[ind].yaxis)
        ax[ind].draw_artist(ax[ind].xaxis)
        ax[ind].draw_artist(line)
        for title in ax[ind].texts:
            print 'title {}'.format(title)
            ax[ind].draw_artist(title)
        #for labels in ax[ind].yaxis.get_ticklabels():
        #    print labels
            #ax[ind].draw_artist(labels)
        fig.canvas.blit(ax[ind].bbox.expanded(1.2,1.2))
        #fig.canvas.blit(ax[ind].bbox.expanded(1.2,1.1))
        #fig.canvas.blit(ax[ind].bbox.union([label.get_window_extent() for label in ax[ind].get_xticklabels()]))
        fig.canvas.flush_events()
        log.debug('Has drawn {} : {}'.format(keys[ind], ax[ind].lines[0].get_data()))
        if ind >= len(keys):
            log.verb('breaking')
            break

###
###     Old non optimized printing utilities
###     Should refactor input to match data_processor client workflow
###
def multi_init_print(data):
    log.info('Init multi printing')
    #plt.ion()
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

    multi_dic = {'dic_1':dic_1}#, 'dic_2':dic_2, 'dic_3':dic_1}

    def add_elem(dic, num):
        for key in dic:
            dic[key].append(num)
    type = 'fast'
    iter = 30

    if type == 'fast':
        print_data = multi_init_fast(multi_dic)
        ax = print_data['dic_1'][1]
        print ax
        for i in range(iter):
            #raw_input()
            start = time.time()
            multi_print_fast(multi_dic, print_data)
            stop = time.time()
            #data_int = ax[1].xaxis.get_data_interval()
            #view_int = ax[1].xaxis.get_view_interval()
            #print 'x_data_int: {}'.format(data_int)
            #print 'x_view_int: {}'.format(view_int)
            data_int = ax[0].yaxis.get_data_interval()
            view_int = ax[0].yaxis.get_view_interval()
            print 'y_data_int: {}'.format(data_int)
            print 'y_view_int: {}'.format(view_int)
            tics = ax[0].yaxis.get_ticklabels()
            print 'tic labels : {}'.format(tics[-1])
            print 'tic labels : {}'.format(tics[0])
            ##
            #print len(ax[0].lines)
            #print ax[0].lines[0].get_data()
            for key in multi_dic:
                add_elem(multi_dic[key], i)
            print stop - start


    else:
        fig, ax = multi_init_print(multi_dic)
        for i in range(iter):
            data_int = ax[0].xaxis.get_data_interval()
            view_int = ax[0].xaxis.get_view_interval()
            print 'data_x_int: {}'.format(data_int)
            print 'view__x_int: {}'.format(view_int)
            print ax[0].get_data()
            for key in multi_dic:
                add_elem(multi_dic[key], i)
            start = time.time()
            multi_print_dic(multi_dic, ax, fig)
            stop = time.time()
            print stop - start

    raw_input()

if __name__ == '__main__':
    log.real_time = False
    test_print_time()
