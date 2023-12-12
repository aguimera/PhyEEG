import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
#%% Creació funció per generar un asenyal modulada AM
def GenAMSignal( t , Fcar , Fsig , Amp, ModFact, Noise=0) :
    AmpMod = Amp*ModFact
    Msig = AmpMod#es crea la senyal de missatge
    Carr = Amp*np.cos(Fcar*2*np.pi*t ) #es crea la senyal portadora
    AMsig = (1+Msig)*Carr # es crea la senyal AM
    RLoad = 1e3
    AMsig = RLoad*Carr
    AMsig += np.random.normal( 0 , Noise , AMsig.size ) #afegim un soroll a la senyal AM
    return AMsig



#%% Plot del vector de temps
plt.close('all')

Fs = 5e6
Fcar = 100e3
Fsig = 500
Amp = 20
ModFact = 2
Noise = 1e-2
Ts = 1/Fs
nSamples = ((1/Fsig)*1000)/Ts 
t = np.arange(0, Ts*nSamples, Ts) #llargada que tindrà la senyal

AMsig = GenAMSignal(t, Fcar, Fsig, Amp, ModFact, Noise)
plt.figure()
plt.plot(t, AMsig)
plt.title('AM signal')
plt.xlabel('Time [s]')
plt.ylabel('Amp [V]')

#%% Compute and plot Gràfic de la FFT
Fmin = 10
nFFT = int(2**(np.around(np.log2(Fs/Fmin))+1)) #Càlcul de la longitud que ha de tenri la FFT
ff, psd = signal.welch(x=AMsig,fs=Fs,
                       axis=0,
                       nperseg=nFFT,
                       scaling='density') #Càlcul de la FFT
#S'hauria de veure com la freq de la portadora (carrier) està present sense canvis i els components
#de la freq del missatge tindràn dues bandes laterals

plt.figure()
plt.semilogy(ff, psd)
plt.title('AM spectral density')
plt.xlabel('Frequency [Hz]')
plt.ylabel('PSD [V**2/Hz]')
plt.xlim(1000-500,1000+500)


#%% Creem una funció per demodular la senyal
# Mètode de product detector: injectem una senyal que fa que s'elimini l'ona Carrier i ens quedem amb
# l'ona del missatge
def Demodulation( t , Fs, Fcar , Sig , LFPFreq=2e3) :
    Cdem = ( 1*np.cos((Fcar)*2*np.pi*t) + 1*np.sin((Fcar)*2*np.pi*t)*1j)
    Dem = Sig*Cdem # productori de la senyal AM i una amb la freq de la portadora
    plt.figure()
    plt.plot(Dem)
    #el resultat és una senyal amn un pic a la FFT al centre i amplitud del missatge 
   
    Ffilt = LFPFreq/(0.5*Fs) #
    sos = signal.butter( 4 , Ffilt ,'lowpass', output='sos') #creació dels coeficients del filtre
    return signal.sosfiltfilt(sos, Dem, axis=0) #apliquem filtre digital, ens quedem amb la senyal 
    #del missatge


#%% Plot real-imaginari o modul-fase
Sig = Demodulation( t , Fs, Fcar +1, AMsig)
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

#%% FFT de la senyal demodulada
Fmin = 10
nFFT = int(2**(np.around(np.log2(Fs/Fmin))+1)) 
ff, psd = signal.welch(x=Sig,fs=Fs,
                       axis=0,
                       nperseg=nFFT,
                       scaling='density') 
plt.figure()
plt.semilogy(ff, psd)
plt.title('SIG spectral density')
plt.xlabel('Frequency [Hz]')
plt.ylabel('PSD [V**2/Hz]')