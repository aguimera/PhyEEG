import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal
from neo.core import AnalogSignal
import quantities as pq
import numpy as np
from PhyREC import SignalProcess as Spro
from PhyREC import PlotWaves as Rplt
from PhyREC import SignalAnalysis as San


plt.close('all')

#something

Freqs = 250
Ts = 1/Freqs
freqs = Freqs/(0.5 * Freqs)
comparativa = []
# RAW
# Càrreguem les dades a un dataframe
electrode_laia = pd.read_table('231123.exp2.txt', sep=', ', header=4)
electrode_laia = electrode_laia.iloc[:, 1]


electrode_comercial = pd.read_table('231123.exp2.txt', sep=', ', header=4)
electrode_comercial = electrode_comercial.iloc[:, 2]

comparativa = pd.concat([electrode_laia ,electrode_comercial], axis=1)
comparativa= comparativa.fillna(0) 
comparativa.set_axis(['Electrode Laia', 'Electrode Comercial'], axis="columns")

# FILTRATGE
# Filtrem les dades amb un HPF 0.5 Hz


sigs = []
for c in comparativa.columns:
    print(c)
    sigs.append(AnalogSignal(comparativa[c],
                             units='uV',
                             sampling_rate=250*pq.Hz,
                             name=c))
    
    
    
# fig, ax = plt.subplots(2, 1, sharex=True)
# fig.subplots_adjust(hspace=0.4)

# def on_press(event):
#     if event.inaxes == ax[0]:
#         ax[1].set_xlim(ax[0].get_xlim())
#         ax[1].set_ylim(ax[0].get_ylim()) 
#         fig.canvas.draw_idle()

# cid_press = fig.canvas.mpl_connect('button_press_event', on_press)
#%%
      
# for ic, s in enumerate(sigs):
#     # print(ic, s.name)
#     s=s.time_slice(30*pq.s, s.t_stop-10*pq.s).rescale('mV')
#     ax[ic].plot(s.times, s, alpha=0.5)
#     ss = SPro.Filter(s, 'highpass', 3, (1,))
#     axs = plt.twinx(ax[ic])
#     axs.plot(ss.times, ss, label=s.name)
#     axs.legend()
     
SigsPl = sigs

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

FiltRMS = [{'function': Spro.Filter, 'args': {'Type': 'bandpass',
                                              'Order': 4,
                                              'Freqs': (30,32)}},
           {'function': Spro.sliding_window, 'args': {'timewidth': 1*pq.s}},
           ]


AxLEMG = {
    'ylim': (-1, 1),
    'facecolor': '#FFFFFF00',
    'autoscaley_on': True,
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

AxRms = {
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
    # {'ProcesChain':  FiltEMG,
    #  'SlotFunc': Rplt.WaveSlot,
    #  'AxsType': 'Wave',
    #  'TwinAx': True,
    #  'FunctionKwarg': {'Units': 'mV',
    #                    'color': 'r',
    #                    'alpha': 0.5,
    #                    'AxKwargs': AxLEMG,
    #                    'clip_on': True,
    #                    }
    #  },
    {'ProcesChain':  FiltRMS,
     'SlotFunc': Rplt.WaveSlot,
     'AxsType': 'Wave',
     'TwinAx': True,
     'FunctionKwarg': {'Units': 'mV',
                       'color': 'g',
                       'alpha': 1,
                       'AxKwargs': AxRms,
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
        # if fkwarg['color'] == 'auto':
        #     fkwarg['color'] = sig.annotations['color']

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

# fig,ax = plt.subplots()
# San.PlotPSD(Slots, Time=(60*pq.s, 67*pq.s), FMin=5, Ax=ax)
# San.PlotPSD(Slots, Time=(123*pq.s, 147*pq.s), FMin=5, Ax=ax)



