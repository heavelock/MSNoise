"""
This plot shows the result of the MWCS calculations in two superposed images.
One is the dt calculated vs time lag and the other one is the coherence. The
image is constructed by horizontally stacking the MWCS of different days. The
two right panels show the mean and standard deviation per time lag of the whole
image. The selected time lags for the dt/t calculation are presented with green
horizontal lines, and the minimum coherence or the maximum dt are in red.

The ``filterid``, ``comp`` and ``mov_stack`` allow filtering the data used.

.. include:: clickhelp/msnoise-plot-mwcs.rst

Example:

``msnoise plot mwcs ID.KWUI ID.POSI -m 3`` will plot all defaults with the
mov_stack = 3:

.. image:: .static/mwcs.png

"""

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
from matplotlib import colors, cm
from matplotlib.dates import date2num, AutoDateFormatter, AutoDateLocator

import datetime

import pandas as pd

df = pd.read_csv('/media/dam/3de09425-8a7e-454a-8c5a-4f2eba33a8d9/testdata/STR/01/005_DAYS/EE/RT_BETS_RT_RITT.csv')

fig, ax = plt.subplots(1)
ax2 = ax.twinx()

df.plot('Date', 'Delta', ax=ax, legend=False)
df.plot('Date', 'Coeff', ax=ax, legend=False)
df.plot('Date', 'Error', ax=ax2, legend=False)

lines =

fig.autofmt_xdate()

ax.legend(loc=0)
ax2.legend(loc=0)
