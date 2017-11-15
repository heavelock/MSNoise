"""
This plot shows the cross-correlation functions (CCF) vs frequency. The
parameters allow to plot the daily or the mov-stacked CCF. Filters and
components are selectable too. The ``--ampli`` argument allows to increase the
vertical scale of the CCFs. Passing ``--refilter`` allows to bandpass filter
CCFs before plotting. Passing ``--startdate`` and ``--enddate`` parameters
allows to specify which period of data should be plotted. By default the plot
uses dates determined in database.

.. include:: clickhelp/msnoise-plot-ccffreq.rst


Example:

``msnoise plot ccftime ID.KWUI ID.POSI`` will plot all defaults:

.. image:: .static/ccffreq.png
"""
# plot ccffreq

import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
from matplotlib.widgets import Cursor
from obspy.signal.filter import bandpass

from msnoise.api import build_movstack_datelist, connect, get_config, \
    get_filters, get_results, get_maxlag_samples


def main(sta1, sta2, filterid, components, mov_stack=1, show=False,
         outfile=None, refilter=None, vmax=None, vmin=None, alphafactor=None):

    db = connect()
    cc_sampling_rate = float(get_config(db, 'cc_sampling_rate'))
    maxlag = float(get_config(db, 'maxlag'))
    samples = get_maxlag_samples(db)
    start, end, datelist = build_movstack_datelist(db)
    sta1 = sta1.replace('.', '_')
    sta2 = sta2.replace('.', '_')

    fig, ax = plt.subplots(figsize=(12, 9))

    if refilter:
        freqmin, freqmax = refilter.split(':')
        freqmin = float(freqmin)
        freqmax = float(freqmax)

    t = np.arange(samples)/cc_sampling_rate - maxlag


    if not sta2 >= sta1:
        raise Exception("Station names are not in alphabetical order!")

    pair = "%s:%s" % (sta1, sta2)

    print("New Data for %s-%s-%i-%i" % (pair, components, filterid,
                                        mov_stack))
    nstack, stack_total = get_results(db, sta1, sta2, filterid, components,
                                      datelist, mov_stack, format="matrix")

    curves = []
    dates = []


    for i, (line, day) in enumerate(zip(stack_total,datelist)):
        if np.all(np.isnan(line)):
            continue

        if refilter:
            line = bandpass(line, freqmin, freqmax, cc_sampling_rate,
                            zerophase=True)

        curves.append(line)
        dates.append(day)

    for filterdb in get_filters(db, all=True):
        if filterid == filterdb.ref:
            low = float(filterdb.low)
            high = float(filterdb.high)
            break

    if check_same_length_of_stacks(curves):
        curves = np.array(curves)

    if alphafactor is not None:
        applicator = np.vectorize(f)
        curves = applicator(curves, alphafactor)

    if vmax is None:
        vmax = np.max(np.abs(curves))
    if vmin is None:
        vmin = -vmax

    pc = ax.pcolormesh(t, dates, curves, cmap='seismic', vmax=vmax, vmin=vmin)

    fig.colorbar(pc)

    ax.set_xlabel("Lag Time (s)")

    title = '%s : %s, %s, Filter %d (%.2f - %.2f Hz), Stack %d' %\
            (sta1.replace('_', '.'), sta2.replace('_', '.'), components,
             filterid, low, high, mov_stack)
    if refilter:
        title += ", Re-filtered (%.2f - %.2f Hz)" % (freqmin, freqmax)
    ax.set_title(title)

    if outfile:
        if outfile.startswith("?"):
            pair = pair.replace(':', '-')
            outfile = outfile.replace('?', '%s-%s-f%i-m%i' % (pair,
                                                              components,
                                                              filterid,
                                                              mov_stack))
        outfile = "ccffreq_" + outfile
        print("output to:", outfile)
        fig.savefig(outfile)
    if show:
        fig.show()
    else:
        plt.close(fig)


def check_same_length_of_stacks(all_curves):
    """
    Checks if all provided lines are equal in length

    :type all_curves: list(float)
    :param all_curves: List of all curves containing loaded stacks

    :rtype: bool
    :return: Returns if all rows in list are equal in length
    """
    return all([len(all_curves[0]) == len(x) for x in all_curves])


def f(x, alphafactor):
    return np.sign(x)*(np.abs(x)**alphafactor)