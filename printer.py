import numpy as np
import time
import matplotlib
matplotlib.use('GTKAgg')
from matplotlib import pyplot as plt
from helpers import Logger

N_COL = 2

def multi_init_print(data):
    plt.ion()
    fig_ret = []
    ax_ret = []
    for target in data:
        n_elem = len(data)
        n_col = N_COL
        if n_elem % n_col == 0:
            n_raw = int(n_elem / n_col)
        else:
            n_raw = int(n_elem / n_col) + 1
        fig, ax = plt.subplots(8,2)
        fig_ret.append(fig)
        ax_ret.append(ax)
    plt.show(False)
    plt.draw()
    return fig_ret, ax_ret

def init_print(dico):
    print dico
    n_elem = len(dico)
    print n_elem
    n_col = N_COL
    if n_elem % n_col == 0:
        n_raw = int(n_elem / n_col)
    else:
        n_raw = int(n_elem / n_col) + 1
    print n_raw
    print n_col
    fig, ax = plt.subplots(n_raw,n_col)
    plt.show(False)
    plt.draw()
    return fig, ax


def multi_print_dic(multi_dico, multi_ax, multi_fig):
    for dico, ax, fig in (multi_dico, multi_ax, multi_fig):
        print_dic(dico, ax, fig)

def print_dic(dico, ax, fig):
    keys = dico.keys()
    ind = 0
    for raw in ax:
        for column in raw:
            print '[PRINT THREAD] plot {}'.format(dico[keys[ind]])
            column.plot(dico[keys[ind]])
            column.set_title(keys[ind])
            ind += 1
            if ind >= len(keys):
                break
    print '[PRINT THREAD] Before drawing'
    fig.canvas.draw()
    print '[PRINT THREAD] has drawn'


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
    #run(doblit=False)
    run(doblit=True)





