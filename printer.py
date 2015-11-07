import numpy as np
import time
import matplotlib
matplotlib.use('GTKAgg')
from matplotlib import pyplot as plt
from helpers import Logger
from conf import *

N_COL = 2

CPU_LOG_FILE = os.path.join(LOCAL_DATA_DIR, 'cpu.log')
log = Logger(CPU_LOG_FILE)

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
    log.debug('len({})= {}'.format(target, n_elem))
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


def randomwalk(dims=(256, 256), n=20, sigma=5, alpha=0.95, seed=1):
    """ A simple random walk with memory """

    r, c = dims
    gen = np.random.RandomState(seed)
    pos = gen.rand(2, n) * ((r,), (c,))
    old_delta = gen.randn(2, n) * sigma

    while True:
        delta = (1. - alpha) * gen.randn(2, n) * sigma + alpha * old_delta
        pos += delta
        for ii in xrange(n):
            if not (0. <= pos[0, ii] < r):
                pos[0, ii] = abs(pos[0, ii] % r)
            if not (0. <= pos[1, ii] < c):
                pos[1, ii] = abs(pos[1, ii] % c)
        old_delta = delta
        yield pos




def run(niter=1000, doblit=True):
    """
    Display the simulation using matplotlib, optionally using blit for speed
    """

    fig, ax = plt.subplots(1,1)#(2, 8)
    ax.set_aspect('equal')
    ax.set_xlim(0, 255)
    ax.set_ylim(0, 255)
    ax.hold(True)
    rw = randomwalk()
    x, y = rw.next()

    plt.show(False)
    plt.draw()

    if doblit:
        # cache the background
        background = fig.canvas.copy_from_bbox(ax.bbox)

    points = ax.plot(x, y, 'o')[0]
    tic = time.time()

    for ii in xrange(niter):

        # update the xy data
        x, y = rw.next()
        points.set_data(x, y)

        if doblit:
            ax.draw()
            # restore background
            fig.canvas.restore_region(background)

            # redraw just the points
            ax.draw_artist(points)

            # fill in the axes rectangle
            fig.canvas.blit(ax.bbox)

        else:
            # redraw everything
            fig.canvas.draw()

    plt.close(fig)
    print "Blit = %s, average FPS: %.2f" % (
        str(doblit), niter / (time.time() - tic))


if __name__ == '__main__':


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
                'mem_info':[23,45,86,587]
    }

    def add_elem(dic):
        for key in dic:
            dic[key].append(0)

    multi_dic = {'dic_1':dic_1, 'dic_2': dic_2, 'dic_3':dic_1}
    fig, ax = multi_init_print(multi_dic)

    iter = 20

    for i in range(iter):
        for dic in multi_dic:
            add_elem(multi_dic[dic])
        start = time.time()
        multi_print_dic(multi_dic, ax, fig)
        stop = time.time()
        print stop - start
    raw_input()

    #run(doblit=False)
    #run(doblit=True)





