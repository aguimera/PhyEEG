# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 08:51:31 2023

@author: User
"""
import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal
from neo.core import AnalogSignal
import quantities as pq
import numpy as np
from PhyREC import SignalProcess as SPro
import statistics

def measure_resistence(arxiu):
    Fs = 250/(1*pq.s)
    Ts = 1/Fs 
    Amp = 6e-6
    LFPFreq=5
    #%% RAW
    # Càrreguem les dades a un dataframe
    data = pd.read_table(arxiu, sep=', ', header=4) #els noms dels fitxer xx_k -> fets amb tres resistències iguals de valor xx
                                                            # noms dels fitxers xxprova2 -> fets amb una resitència de valor xx en paral·lel amb una de 10 ohms
    sig = AnalogSignal(data.iloc[:, 1],
                                 units='uV',
                                 sampling_rate=250*pq.Hz,
                                 name='18k')
    sig = sig.rescale('V')
    
    #%% FILTRATGE
    # Filtrem les dades amb un HPF 0.5 Hz
    
    sig = SPro.Filter(sig, 'highpass', 3, (1,))
    
    
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
            
        
        sig=sig.time_slice(tall, sig.t_stop-tall)
    
        Fcar = (cicles_1+cicles_2)/2/(sig.times[-1]-sig.times[0])
       
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
               
    #%% Caluclem la senyal demodulada, pas previ a conèixer la resistència
    Dem = sig_m.flatten()*(sig_inj_m)
    Dem = np.nan_to_num(Dem, 0)
    
    #%% Apliquem el filtre superheterodino per coneixer la resistència
    Ffilt = LFPFreq/(0.5*Fs) #
    sos = signal.butter( 4 , Ffilt ,'lowpass', output='sos')
    resistence = signal.sosfiltfilt(sos, Dem, axis=0)
    
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
        
        
    return mitjana

  
  
    
