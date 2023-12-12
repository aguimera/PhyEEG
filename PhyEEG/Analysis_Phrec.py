# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 16:24:09 2023

@author: User
"""

import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal
from neo.core import AnalogSignal
import quantities as pq
import numpy as np
from PhyREC import SignalProcess as Spro
from PhyREC import PlotWaves as Rplt
from PhyREC import SignalAnalysis as San

plt.style.use('MyStyle.mplstyle')
plt.close('all')


Freqs = 250
Ts = 1/Freqs
freqs = Freqs/(0.5 * Freqs)

# FILTRATGE
# Filtrem les dades amb un HPF 0.5 Hz
FilesIn = (
        ('electrode_comercial.txt', 'r'),
        ('TPU.txt', 'g'),
        ('TPU_Kapton.txt', 'b'),
    )



SigsPl = []
for FileIn, color in FilesIn:
    name = FileIn.split('.')[0]
    data = pd.read_table(FileIn, sep=', ', header=4)

    sig = AnalogSignal(data.iloc[:, 1],
                             units='uV',
                             sampling_rate=250*pq.Hz,
                             name=name)

    
    sig.annotate(color=color)

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
    'ylim': (-1, 1),
    'facecolor': '#FFFFFF00',
    'autoscaley_on': False,
    'xaxis': {'visible': False,
              },
    'yaxis': {'visible': True,
              },
}

AxDC = {
    'ylim': (-0.2, 0.2),
    'facecolor': '#FFFFFF00',
    'autoscaley_on': True,
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
                       'AxKwargs': AxDC,
                       'clip_on': False,
                       }
     },
    {'ProcesChain':  FiltEMG,
     'SlotFunc': Rplt.WaveSlot,
     'AxsType': 'Wave',
     'TwinAx': True,
     'FunctionKwarg': {'Units': 'mV',
                       'color': 'auto',
                       'alpha': 1,
                       'AxKwargs': AxLEMG,
                       'clip_on': True,
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

    