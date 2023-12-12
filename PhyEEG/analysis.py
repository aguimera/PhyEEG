#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 30 16:28:59 2023

@author: aguimera
"""

from neo.core import AnalogSignal
from scipy.io import loadmat
import quantities as pq
import matplotlib.pyplot as plt
import numpy as np
import PhyREC.PlotWaves as Rplt
import PhyREC.SignalProcess as Spro
import PhyREC.SignalAnalysis as San


plt.style.use('MyStyle.mplstyle')

plt.close('all')

a = loadmat('20230519_S01_test-preliminar-3mm.mat')

Fs = (1/pq.Quantity(a['isi'][0], a['isi_units'][0]))[0].rescale('Hz')

SigsPl = []
for s, l, u in zip(a['data'].transpose(), a['labels'], a['units']):
    # if not l.startswith('notch'):
        # continue
    if not l.endswith('EMG100C'):
        continue
    
    sig = AnalogSignal(s,
                       units=u,
                       sampling_rate=Fs,
                       name=l)

    if l.endswith('ref') or l=='EMG - REF - EMG100C':
        sig.annotate(color='r')

    if l.endswith('tattoo')or l=='EMG - tattoo - EMG100C':
        sig.annotate(color='b')    

    SigsPl.append(sig)

# Generate figure
nSigs = len(SigsPl)
Figplot, Axs = plt.subplots(nSigs, 1, sharex=True)
Axs = Axs.flatten()

FiltEmpty = [{'function': Spro.Filter, 'args': {'Type': 'bandstop',
                                              'Order': 4,
                                              'Freqs': (49.5,50.5)}}, ]

# FiltEmpty = []

FiltEMG = FiltEmpty + [{'function': Spro.Filter, 'args': {'Type': 'highpass',
                                              'Order': 4,
                                              'Freqs': (5,)}}, ]

AxLEMG = {
    'ylim': (-0.2, 0.2),
    'facecolor': '#FFFFFF00',
    'autoscaley_on': False,
    'xaxis': {'visible': False,
              },
    'yaxis': {'visible': True,
              },
}

Procs = (

    {'ProcesChain':  FiltEmpty,
     'SlotFunc': Rplt.WaveSlot,
     'AxsType': 'Wave',
     'TwinAx': False,
     'FunctionKwarg': {'Units': 'mV',
                       'color': 'k',
                       # 'linewidth': 1,
                       'alpha': 0.5,
                       'AxKwargs': AxLEMG,
                       'clip_on': False,
                       }
     },
    {'ProcesChain':  FiltEMG,
     'SlotFunc': Rplt.WaveSlot,
     'AxsType': 'Wave',
     'TwinAx': False,
     'FunctionKwarg': {'Units': 'mV',
                       'color': 'auto',
                       'alpha': 1,
                       'AxKwargs': AxLEMG,
                       'clip_on': False,
                       }
     },
)


# %% Slots implementation
Slots = []
for ic, sig in enumerate(SigsPl):
    axp = None
    for proc in Procs:
        axi = Axs[ic]
        if proc['TwinAx']:
            axp = plt.twinx(axi)
        else:
            axp = axi

        fkwarg = proc['FunctionKwarg'].copy()
        if fkwarg['color'] == 'auto':
            fkwarg['color'] = sig.annotations['color']

        sp = Spro.ApplyProcessChain(sig, proc['ProcesChain'])
        Slots.append(proc['SlotFunc'](sp,
                                      Ax=axp,
                                      **fkwarg))


Splt = Rplt.PlotSlots(Slots,
                      Fig=Figplot,
                      LiveControl=True,
                      TimeAxis=-1,
                      )

Splt.PlotChannels(None)
Splt.AddLegend()

fig,ax = plt.subplots()
San.PlotPSD(Slots, Time=(60*pq.s, 67*pq.s), FMin=5, Ax=ax)
San.PlotPSD(Slots, Time=(123*pq.s, 147*pq.s), FMin=5, Ax=ax)
