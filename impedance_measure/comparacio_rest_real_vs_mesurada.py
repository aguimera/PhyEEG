# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 08:55:12 2023

@author: User
"""

import function 
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np
diccionari = [
    {'arxiu': '47prova2.txt',
     'resistencia':47},
    {'arxiu': '270prova2.txt',
     'resistencia':270},
    {'arxiu': '330prova2.txt',
     'resistencia':330},
    {'arxiu': '560prova2.txt',
     'resistencia':560},
    {'arxiu': '18kprova2.txt',
     'resistencia':18000},
    {'arxiu': '68kprova2.txt',
     'resistencia':68000},
    {'arxiu': '100kprova2.txt',
     'resistencia':100000}]


# iterem per conseguir el resultat de la resistència experimental
for item in diccionari:
    arxiu = item["arxiu"]
    resistencia_exp = function.measure_resistence(arxiu)
    item['resistencia experimetnal'] = resistencia_exp
    
#exportem dades per fer grafics
resistencies = [item['resistencia'] for item in diccionari]
resultats = [item['resistencia experimetnal'] for item in diccionari]


#regresió lineal 
slope, intercept, r_value, p_value, std_err = stats.linregress(resistencies, resultats) 
#slope: pendent de la regressió
#intercept: punt tall eix y
#r_value: coeficient de correlació (aprop 1 correlació positiva forta)
#p_value: hipotesis nula que la pendent de regresió es igual a zero
#std_err: error estàndard de l'estimació de la pendent   
#fem gràfic Resistència teòrica vs. Resistència mesurada
plt.figure()




plt.plot(resistencies, resultats,marker='o', linestyle='-', color="blue", label="Resultats")
plt.plot(resistencies, slope * np.array(resistencies) + intercept, color="red", label="Regressió Lineal")
desviacions = [0.05 * valor for valor in resultats]
plt.bar(resistencies, resultats, yerr=desviacions, capsize=5, linestyle='-', color="blue", label="Barra error")
plt.xlabel('X')
plt.xlabel('Resistencia teòrica')
plt.ylabel('Resistència mesurada')
plt.title('Gràfic Resistència teòrica vs. Resistència mesurada')
plt.grid(True)
plt.legend()
plt.show()




#modificació de les nostres dades per a que encaixin amb les dades teòriques 
#la pendent es quasi igual a 1 per tant no la modificarem però si el punt de tall
plt.figure()
resultats_modificats = resultats - intercept
plt.plot(resistencies, resultats_modificats,marker='o', linestyle='-', color="blue", label="Resultats modificats")
desviacions = [0.05 * valor for valor in resultats_modificats]
plt.bar(resistencies, resultats_modificats, yerr=desviacions, capsize=5, linestyle='-', color="blue", label="Barra error")
plt.xlabel('Resistencia teòrica')
plt.ylabel('Resistència mesurada i modificada')
plt.title('Gràfic Resistència teòrica vs. Resistència mesurada i modificada')
plt.grid(True)
plt.show()
