"""
This plot shows the cross-correlation functions (CCF) vs time. The parameters
allow to plot the daily or the mov-stacked CCF. Filters and components are
selectable too. The ``--ampli`` argument allows to increase the vertical scale
of the CCFs. The ``--seismic`` shows the up-going wiggles with a black-filled
background (very heavy !). Passing ``--refilter`` allows to bandpass filter
CCFs before plotting (new in 1.5). Passing ``--startdate`` and ``--enddate``
parameters allows to specify which period of data should be plotted. By default
the plot uses dates determined in database.

.. include:: clickhelp/msnoise-plot-ccftime.rst


Example:

``msnoise plot ccftime ID.KWUI ID.POSI`` will plot all defaults:

.. image:: .static/ccftime.png
"""
# plot interferogram

import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Cursor
from obspy.signal.filter import bandpass
from obspy.signal.filter import envelope as obspy_envelope

from msnoise.api import connect, get_config, get_maxlag_samples, \
    build_movstack_datelist, get_filters, get_results


def main(sta1, sta2, filterid, components, mov_stack=1, ampli=5, seismic=False,
         show=False, outfile=None, envelope=False, refilter=None,  startdate=None, enddate=None):
    db = connect()
    maxlag = float(get_config(db, 'maxlag'))
    samples = get_maxlag_samples(db)
    cc_sampling_rate = float(get_config(db, 'cc_sampling_rate'))

    start, end, datelist = build_movstack_datelist(db, startdate, enddate)
    base = mdates.date2num(start) 

    fig = plt.figure(figsize=(12, 9))

    sta1 = sta1.replace('.', '_')
    sta2 = sta2.replace('.', '_')
    t = np.arange(samples) / cc_sampling_rate - maxlag

    if refilter:
        freqmin, freqmax = refilter.split(':')
        freqmin = float(freqmin)
        freqmax = float(freqmax)

    if sta2 >= sta1:
        pair = "%s:%s" % (sta1, sta2)

        print("New Data for %s-%s-%i-%i" % (pair, components, filterid,
                                            mov_stack))
        nstack, stack_total = get_results(db, sta1, sta2, filterid, components,
                                          datelist, mov_stack, format="matrix")
        ax = fig.add_subplot(111)
        for i, line in enumerate(stack_total):
            if np.all(np.isnan(line)):
                continue

            if refilter:
                line = bandpass(line, freqmin, freqmax, cc_sampling_rate,
                                zerophase=True)
            if envelope:
                line = obspy_envelope(line)

            line /= line.max()
            ax.plot(t, line * ampli + i + base, c='k')

            if seismic:
                y1 = np.ones(len(line)) * i
                y2 = line * ampli + i + base
                ax.fill_between(t, y1, y2, where=y2 >= y1, facecolor='k',
                                interpolate=True)

        for filterdb in get_filters(db, all=True):
            if filterid == filterdb.ref:
                low = float(filterdb.low)
                high = float(filterdb.high)
                break

        ax.set_xlabel("Lag Time (s)")
        ax.axhline(0, lw=0.5, c='k')
        ax.grid()
        ax.scatter(0, [start, ], alpha=0)
        ax.set_ylim(start - datetime.timedelta(days=ampli),
                    end + datetime.timedelta(days=ampli))
        ax.set_xlim(-maxlag, maxlag)
        ax.fmt_ydata = mdates.DateFormatter('%Y-%m-%d')
        cursor = Cursor(ax, useblit=True, color='red', linewidth=1.2)

        title = '%s : %s, %s, Filter %d (%.2f - %.2f Hz), Stack %d' % \
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
            outfile = "ccftime " + outfile
            print("output to:", outfile)
            fig.savefig(outfile)

        if show:
            fig.show()
        else:
            plt.close(fig)
