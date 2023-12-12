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


FilesIn = ('47_ohms.txt','330_ohms.txt','2200_ohms.txt')



sigs = []
for FileIn in FilesIn:
    name = FileIn.split('.')[0]
    data = pd.read_table(FileIn, sep=', ', header=4)

    sig = AnalogSignal(data.iloc[:, 1],
                             units='uV',
                             sampling_rate=250*pq.Hz,
                             name=name)

    sigs.append(sig)
# FILTRATGE
# Filtrem les dades amb un HPF 0.5 Hz

#%%

fig, ax = plt.subplots(len(sigs))
for ic, s in enumerate(sigs):
        # print(ic, s.name)
    s=s.time_slice(5*pq.s, None).rescale('mV')
    ax[ic].plot(s.times, s, alpha=0.5)
    ss = SPro.Filter(s, 'highpass', 3, (1,))
    axs = plt.twinx(ax[ic])
    axs.plot(ss.times, ss, label=s.name)
    axs.legend()
    
    
 

impedance=[]
for i in sigs:
    i=i.time_slice(3*pq.s, None).rescale('mV')
    print(np.std(i))
    # impedance.append(np.std(i)*np.sqrt(2) /(6*10^-3)-2200)



#%% 
#Transformada de Fourier soroll + senyal biològica



# figfft, axfft = plt.subplots(len(sigs), sharex=True)
# # xf = np.fft.fftfreq(nSamples, Ts)[:nSamples//2]
# for ic, s in enumerate(sigs):
#     s1=s.time_slice(0*pq.s, None).rescale('mV')
#     ss1 = SPro.Filter(s1, 'highpass', 3, (1,))
#     fs, ps = signal.welch(ss1, ss1.sampling_rate, nperseg=2**9, axis=0)
#     axfft[ic].loglog(fs, ps, label='FFT')
    
    
   
   
 


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