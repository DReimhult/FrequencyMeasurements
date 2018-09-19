# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 19:14:47 2018

@author: Daniel Reimhult

@version: 0.1
"""

import matplotlib.pyplot as plt
from test_signal_generation import Signal, read_ref_signal_from_xls, \
                                   generate_test_signal
import frequency_methods as fm
import numpy as np


""" Synthetized signal """

fnom = 50

dists = []
dists.append({'name': 'superposed frequency', 'params': [0.1, 213.3421]})
variations = []
variations.append({'name': 'phase jump and slow mod', 'params': [500.3, 214.5, 0.5]})
#variations.append({'name': 'slow mod', 'params': [50, 4.5, 2]})

sig = generate_test_signal(num_cycles = 1000, variations = variations, disturbances = dists)

f_bergeron = fm.bergeron_derivate(sig, startup_periods = 10)
f_synchrophasor = fm.synchrophasor_frequency(sig)
f_zerocrossing= fm.filtered_zerocrossing(sig, startup_periods = 10)
f_separation = fm.separated_frequency(sig)

f = plt.figure()
ax = f.add_subplot(111)

f_bergeron.plot(ax, label='Bergeron')
f_synchrophasor.plot(ax, label='Synchrophasor')
f_zerocrossing.plot(ax, label='Zero crossing')
f_separation.plot(ax, label='Phase separation')
ax.legend()
ax.set_ylabel('Frequency (Hz)')
ax.set_xlabel('Time (s)')

""" Signal read from Roger Bergeron's xls file """

sig = read_ref_signal_from_xls('Reference signal for testing.xlsx')

f_bergeron = fm.bergeron_derivate(sig, startup_periods = 10)
f_synchrophasor = fm.synchrophasor_frequency(sig)
f_zerocrossing= fm.filtered_zerocrossing(sig, startup_periods = 10)
f_separation = fm.separated_frequency(sig)

f = plt.figure()
ax = f.add_subplot(111)

f_bergeron.plot(ax, label='Bergeron')
f_synchrophasor.plot(ax, label='Synchrophasor')
f_zerocrossing.plot(ax, label='Zero crossing')
f_separation.plot(ax, label='Phase separation')
ax.legend()
ax.set_ylabel('Frequency (Hz)')
ax.set_xlabel('Time (s)')
