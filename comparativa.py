import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal
from neo.core import AnalogSignal
import quantities as pq
import numpy as np
from PhyREC import SignalProcess as SPro
plt.close('all')


Freqs = 250
Ts = 1/Freqs
freqs = Freqs/(0.5 * Freqs)
comparativa = []
# RAW
# Càrreguem les dades a un dataframe
electrode_comercial = pd.read_table('electrode_comercial.txt', sep=', ', header=4)
electrode_comercial = electrode_comercial.iloc[:, 1]

TPU_Kapton = pd.read_table('TPU_Kapton.txt', sep=', ', header=4)
TPU_Kapton = TPU_Kapton.iloc[:, 1]
TPU = pd.read_table('TPU.txt', sep=', ', header=4)
TPU = TPU.iloc[:, 1]
comparativa = pd.concat([electrode_comercial, TPU_Kapton, TPU], axis=1)
comparativa= comparativa.fillna(0) 
comparativa.set_axis(['Electrode Comercial','TPU Kapton' , 'TPU'], axis="columns", inplace=True)
# FILTRATGE
# Filtrem les dades amb un HPF 0.5 Hz


sigs = []
for c in comparativa.columns:
    print(c)
    sigs.append(AnalogSignal(comparativa[c],
                             units='uV',
                             sampling_rate=250*pq.Hz,
                             name=c))
    

#%%

fig, ax = plt.subplots(len(sigs))
for ic, s in enumerate(sigs):
    # print(ic, s.name)
    s=s.time_slice(63*pq.s, 100*pq.s).rescale('mV')
    ax[ic].plot(s.times, s, alpha=0.5)
    ss = SPro.Filter(s, 'highpass', 3, (1,))
    axs = plt.twinx(ax[ic])
    axs.plot(ss.times, ss, label=s.name)
    axs.legend()
    
#%% 
# Transformada de Fourier soroll + senyal biològica



figfft, axfft = plt.subplots(len(sigs), sharex=True)
# xf = np.fft.fftfreq(nSamples, Ts)[:nSamples//2]
for ic, s in enumerate(sigs):
    s1=s.time_slice(63*pq.s, 87*pq.s).rescale('mV')
    ss1 = SPro.Filter(s1, 'highpass', 3, (1,))
    fs, ps = signal.welch(ss1, ss1.sampling_rate, nperseg=2**9, axis=0)
    axfft[ic].loglog(fs, ps, label='Soroll')
    s2=s.time_slice(90*pq.s, 100*pq.s).rescale('mV')
    ss2 = SPro.Filter(s2, 'highpass', 3, (1,))
    fb, pb = signal.welch(ss2, ss2.sampling_rate, nperseg=2**9, axis=0)
    axfft[ic].loglog(fb, pb,label='Biologica', color='green')
    # axffts = plt.twinx(axfft[ic])
    # axffts.loglog(fb, pb,label='Biologica', color='green')
    axfft[ic].set_title(s.name)
    # axffts.legend(loc = 'upper right')
    axfft[ic].legend(loc='upper left')
 


#%%
# Integral de la senyal BW=150 comprovar Integral Noise


    # yf = fft(s)
    # axs = plt.twinx(ax[ic])
    # plt.plot(xf,2.0/nSamples * np.abs((ffty[c])[0:nSamples//2]))
    


# fftysigs= np.array([]) 
# fftxsigs  = []
# for ac in sigs:
#     fftysigs= np.append(fftysigs,fft(sigs[ac]))
#     fftxsigs = fftfreq(nSamples, Ts)[:nSamples//2]  