# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 10:53:53 2023

@author: User
"""

import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal
from neo.core import AnalogSignal
import quantities as pq
import numpy as np
from PhyREC import SignalProcess as SPro



Freqs = 250
Ts = 1/Freqs
freqs = Freqs/(0.5 * Freqs)

# RAW
# Càrreguem les dades a un dataframe
data = pd.read_table('rutinaelectrodebias.txt', sep=', ', header=4)
sig = AnalogSignal(data.iloc[:, 1],
                   
                             units='uV',
                             sampling_rate=250*pq.Hz,
                             name='rutina')
sig = sig.rescale('V')
sig = SPro.Filter(sig, 'highpass', 3, (1,))
plt.figure()
plt.plot(sig.times, sig)
plt.show()