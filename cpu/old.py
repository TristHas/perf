#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        ax[ind].xaxis.set_view_interval(0, len(xdata))                  # Should not need if fixed-size input

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
