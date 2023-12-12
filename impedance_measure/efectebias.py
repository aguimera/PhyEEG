# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 10:48:43 2023

@author: User
"""

import function 
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np
from neo.core import AnalogSignal
import quantities as pq
import pandas as pd
from scipy import signal


diccionari = [
    {'arxiu': '18knobias.txt',
     'tipus': 'BIAS no connectat',
     'color' : 'r'},
    {'arxiu': '18kbiascc.txt',
     'tipus': 'BIAS curtcircuitat',
     'color' : 'b'},
    {'arxiu': '330prova2.txt',
     'tipus': 'BIAS connectat a una resistència molt més petita', 
     'color' : 'g'}
    ]
   
#variables per la FFT
Fmin = 1*pq.Hz
Fs = 250/(1*pq.s)
nFFT = int(2**(np.around(np.log2(Fs.magnitude/Fmin.magnitude))+1))
# graficarem la FFT de les dades RAW per comparar-ho millor
plt.figure()
for item in diccionari:
    arxiu = item["arxiu"]
    color = item["color"]
    name = item["tipus"]
    data = pd.read_table(arxiu, sep=', ', header=4) 
    sig = AnalogSignal(data.iloc[:, 1],
                       
                                 units='uV',
                                 sampling_rate=250*pq.Hz,
                                 name='18k')
    sig = sig.rescale('V')
    ff1, psd1 = signal.welch(x=sig,fs=Fs,
                           axis=0,
                           nperseg=nFFT,
                           scaling='density') #Càlcul de la FFT 
    
    
    plt.semilogy(ff1, psd1, color = color, label = name)
    plt.xlim(-125,250)
    plt.title('Spectral density')
    plt.xlabel('Frequency [Hz]')
    
    plt.ylabel('PSD [V**2/Hz]')
    plt.legend()
    plt.grid()
    

