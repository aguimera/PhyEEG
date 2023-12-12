# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 14:54:59 2023

@author: Eva Casals
"""

import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal
from neo.core import AnalogSignal
import quantities as pq
import numpy as np
from PhyREC import SignalProcess as SPro
import statistics
plt.close('all')

Fs = 250/(1*pq.s)
Ts = 1/Fs 
Amp = 6e-6
LFPFreq=5
#%% RAW
# Càrreguem les dades a un dataframe
data = pd.read_table('pista_cc_gruixut_2.txt', sep=', ', header=4) #els noms dels fitxer xx_k -> fets amb tres resistències iguals de valor xx
                                                        # noms dels fitxers xxprova2 -> fets amb una resitència de valor xx en paral·lel amb una de 10 ohms
sig = AnalogSignal(data.iloc[:, 1],
                   
                             units='uV',
                             sampling_rate=250*pq.Hz,
                             name='18k')
sig = sig.rescale('V')

#%% FILTRATGE
# Filtrem les dades amb un HPF 0.5 Hz

sig = SPro.Filter(sig, 'highpass', 3, (1,))
plt.plot(sig.times, sig)
plt.show()

#%% Càlcul freq 
cicles_1=10
cicles_2=0
Fcar=40*pq.Hz
while True: 
    if abs(cicles_1 - cicles_2) <= 2 and 22.88 * pq.Hz <= Fcar <= 34.33 * pq.Hz:
        break 
    resultat=[]
    cicles_1=0
    cicles_2=0
    comp=[0,0]
    m=-1
    n=0
    sen=10
    tall = 2*pq.s

    for m, i in enumerate(sig):
        m=(m+1)%2
        if i>0:
            comp[m]=i
        if i<0:
            comp[m]=i
        if comp[0]>0 and comp[1]<0:
            cicles_1=cicles_1+1
        if comp[0]<0 and comp[1]>0:
            cicles_2=cicles_2+1
        
    print(cicles_1)
    print(cicles_2)

    sig=sig.time_slice(tall, sig.t_stop-tall)

    Fcar = (cicles_1+cicles_2)/2/(sig.times[-1]-sig.times[0])
    print(Fcar)

Amp=6*pq.nA
Amp = Amp.rescale('A')
#%%CCREA SENYAL A INJECTAR
t = np.arange(sig.t_start,2*32*sig.t_stop-sig.t_start/Fcar.magnitude,1/sig.sampling_rate)*pq.s
sig_inj = 2/(Amp)*(np.cos(2*np.pi*Fcar.rescale('rad/s')*t) + np.sin(2*np.pi*Fcar.rescale('rad/s')*t )*1j)

# Treballarem sense quantitats per facilitat
sig_m = sig.magnitude
sig_inj_m = sig_inj.magnitude

#%% CORRELACIÓ CREUADA
lags = signal.correlation_lags(sig_m.size ,sig_inj_m.size)  #calcul del retras de les dues senyals
correlation = signal.correlate(sig_m.flatten(),np.real(sig_inj_m), mode='same') #calcul correlació creuada
lag = lags[np.argmax(correlation)]  #calcul del lag que te maxima correlació
sig_inj_m = np.roll(sig_inj_m, lag) 
sig_inj_m = sig_inj_m[:len(sig_m)]

# Gràfic correlació
max(correlation)
plt.figure()
plt.plot(correlation)

# Gràfic senyals sincronitzades
fig, ax = plt.subplots()
ax.plot(np.real(sig_m), color='r')
axs = plt.twinx(ax)
axs.plot(sig_inj_m)
       
#%% Caluclem la senyal demodulada, pas previ a conèixer la resistència
Dem = sig_m.flatten()*(sig_inj_m)
Dem = np.nan_to_num(Dem, 0)

#%% Apliquem el filtre superheterodino per coneixer la resistència
Ffilt = LFPFreq/(0.5*Fs) #
sos = signal.butter( 4 , Ffilt ,'lowpass', output='sos')
resistence = signal.sosfiltfilt(sos, Dem, axis=0)

# Gràfica de la resistència 
t = np.arange(sig.t_start,sig.t_stop,1/sig.sampling_rate)*pq.s      
fig, (AxR, AxI) = plt.subplots( 2 , 1 , sharex =True)
AxR.plot(t, np.real(resistence))
AxR. set_ylabel('Real[ohms]')
AxI.plot(t,np.imag(resistence))
AxI.set_ylabel('Imag [ohms]')
AxI.set_xlabel('Time[s]')
fig , ( AxM, AxP) = plt.subplots( 2 , 1 , sharex=True)
AxM.plot( t ,  np.abs(resistence))
AxM.set_ylabel( ' Abs [ohms] ' )
AxP.plot( t , np.angle( resistence , deg=True) )
AxP.set_ylabel('Angle [Deg]')
AxP.set_xlabel('Time [s]')


#%% Mitjana resitència
abs_r = np.abs(resistence)
while True:
    mitjana = statistics.mean(abs_r)
    desviacio_estandar = statistics.stdev(abs_r)
    limit_desviacio = 0.05 * mitjana
    if desviacio_estandar <= limit_desviacio:
        break
    abs_r.pop(0)
    abs_r.pop(-1)
    
    
mitjana_resitencia = mitjana
intercep=2700
print(mitjana_resitencia-intercep)
#%% FFT de la senyal demodulada vs AM
Fmin = 1*pq.Hz
nFFT = int(2**(np.around(np.log2(Fs.magnitude/Fmin.magnitude))+1)) #Càlcul de la longitud que ha de tenri la FFT
ff1, psd1 = signal.welch(x=sig_m,fs=Fs,
                       axis=0,
                       nperseg=nFFT,
                       scaling='density') #Càlcul de la FFT 

ff2, psd2 = signal.welch(x=np.real(resistence),fs=Fs,
                       axis=0,
                       nperseg=nFFT,
                       scaling='density') 

# Gràfica de la FFT senyal demodulada vs AM 
plt.figure()
plt.semilogy(ff1, psd1, color = 'r')
plt.semilogy(ff2, psd2)
plt.xlim(-125,250)
plt.title('Spectral density')
plt.xlabel('Frequency [Hz]')
plt.ylabel('PSD [V**2/Hz]')