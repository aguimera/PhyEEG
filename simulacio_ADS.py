"""
@author: Eva Casals
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import pandas as pd
#%% Creaóci funció per generar un asenyal modulada AM
def GenAMSignal(t , Fcar , R, Amp) :
    Carr = Amp*np.cos(Fcar*2*np.pi*t ) #es crea la senyal portadora en el nostre cas I=6nA i 
    AMsig = R*Carr
    return AMsig


#%% Creem una funció per demodular la senyal
# Mètode de product detector: injectem una senyal que fa que s'elimini l'ona Carrier i ens quedem amb
# l'ona del missatge
def Demodulation( t , Fs, Fcar2 , AMsig , LFPFreq, Amp) :
    Cdem = 2/(Amp)*(np.cos(Fcar2*2*np.pi*t) + np.sin(Fcar2*2*np.pi*t)*1j)
    Dem = AMsig*Cdem # productori de la senyal AM i una amb la freq de la portadora
    #el resultat és una senyal amn un pic a la FFT al centre i amplitud del missatge 
    Ffilt = LFPFreq/(0.5*Fs) #
    sos = signal.butter( 4 , Ffilt ,'lowpass', output='sos') #creació dels coeficients del filtre
    return signal.sosfiltfilt(sos, Dem, axis=0) #apliquem filtre digital, ens quedem amb la senyal 
    #del missatge
    
    
#%% Definició de els valors de la nostra senyal
plt.close('all')

Fs = 250
Ts = 1/Fs 


Fcar = 31.25
Amp = 6e-6
R = 18e3
fallo=0
Fcar2 = Fcar+fallo
LFPFreq=5


t = np.arange(0, 2.5, Ts) #llargada que tindrà la senyal
AMsig = GenAMSignal(t , Fcar , R, Amp)
Sig = Demodulation( t , Fs, Fcar2 , AMsig, LFPFreq, Amp)

#%% Plot de la senyal que volem demodular
plt.figure()
plt.plot(t, AMsig)
plt.title('AM signal')
plt.xlabel('Time [s]')
plt.ylabel('Amp [V]')
   
#%% FFT de la senyal demodulada vs AM
Fmin = 1
nFFT = int(2**(np.around(np.log2(Fs/Fmin))+1)) #Càlcul de la longitud que ha de tenri la FFT
ff1, psd1 = signal.welch(x=AMsig,fs=Fs,
                       axis=0,
                       nperseg=nFFT,
                       scaling='density',
                    return_onesided=False) #Càlcul de la FFT

ff2, psd2 = signal.welch(x=Sig,fs=Fs,
                       axis=0,
                       nperseg=nFFT,
                       scaling='density',
                        return_onesided=False)


plt.figure()
plt.semilogy(ff1, psd1)
plt.semilogy(ff2, psd2)
plt.xlim(-125,125)
plt.title('Spectral density')
plt.xlabel('Frequency [Hz]')
plt.ylabel('PSD [V**2/Hz]')
    
    
#%% Plot real-imaginari o modul-fase
fig, (AxR, AxI) = plt.subplots( 2 , 1 , sharex =True)
AxR.plot(t, np.real(Sig))
AxR. set_ylabel('Real[ V]')
AxI.plot(t, np.imag(Sig))
AxI.set_ylabel('Imag [V]')
AxI.set_xlabel('Time[s]')
fig , ( AxM, AxP) = plt.subplots( 2 , 1 , sharex=True)
AxM.plot( t , np.abs(Sig))
AxM.set_ylabel( ' Abs [V] ' )
AxP.plot( t , np.angle( Sig , deg=True) )
AxP.set_ylabel('Angle [Deg]')
AxP.set_xlabel('Time [s]')


#%% Diferència entre els valors si es falla amb la freq de mostreig de la senyal injectada
errors = (
            (0, '#12aa3d'),
            (0.1, '#34b659'),
            (0.2, '#56c274'),
            (0.5, '#78ce90'),
            (1, '#99dbac'),
            (2, '#bbe7c8'),
            (4,'#ddf3e3')
            
            )
noms = []
fig1, (AxR, AxI) = plt.subplots( 2 , 1 , sharex =True)
fig2 , ( AxM, AxP) = plt.subplots( 2 , 1 , sharex=True)
for fallo, colors in errors:
    Fcar2 = Fcar+fallo 
    Sig = Demodulation( t , Fs, Fcar2 , AMsig, LFPFreq, Amp)
    AxR.plot(t, np.real(Sig), colors)
    AxR. set_ylabel('Real[ V]')
    AxI.plot(t, np.imag(Sig), colors)
    AxI.set_ylabel('Imag [V]')
    AxI.set_xlabel('Time[s]')
    AxM.plot( t , np.abs(Sig), colors)
    AxM.set_ylabel( ' Abs [V] ' )
    AxP.plot( t , np.angle( Sig , deg=True), colors )
    AxP.set_ylabel('Angle [Deg]')
    AxP.set_xlabel('Time [s]')
    noms.append('f real'+' + '+str(fallo)+' Hz')

plt.title('Desviació respecte la Fcar per demodular')
AxR.legend(noms, loc='right', bbox_to_anchor=(1.2, 0.5),
          fancybox=True, shadow=True, ncol=1)
fig1.tight_layout()
AxM.legend(noms, loc='right', bbox_to_anchor=(1.2, 0.5),
          fancybox=True, shadow=True, ncol=1)
fig2.tight_layout()

plt.show()
