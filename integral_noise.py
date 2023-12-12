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
prova = pd.read_table('Prova_10s.txt', sep=', ', header=4)
# Ens quedem amb les columnes que ens interessen
prova = prova.iloc[:, list(range(1, 9))]
nSamples = int(prova.size/8)
print(type(nSamples))

# FILTRATGE
# Filtrem les dades amb un HPF 0.5 Hz


sigs = []
for c in prova.columns:
    sigs.append(AnalogSignal(prova[c],
                             units='uV',
                             sampling_rate=250*pq.Hz,
                             name=c))


#%%

fig, ax = plt.subplots(len(sigs))
for ic, s in enumerate(sigs):
    # print(ic, s.name)
    s=s.time_slice(1*pq.s, None).rescale('mV')
    ax[ic].plot(s.times, s, alpha=0.5)
    ss = SPro.Filter(s, 'highpass', 3, (1,))
    axs = plt.twinx(ax[ic])
    axs.plot(ss.times, ss, label=s.name)
    axs.legend()
    
#%% 
# Transformada de Fourier



figfft, axfft = plt.subplots(len(sigs), sharex=True)
# xf = np.fft.fftfreq(nSamples, Ts)[:nSamples//2]
for ic, s in enumerate(sigs):
    print(ic)
   
    ss = SPro.Filter(s, 'highpass', 3, (1,))
    f, p = signal.welch(ss, ss.sampling_rate, nperseg=2**9, axis=0)
    axfft[ic].loglog(f, p)
    
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