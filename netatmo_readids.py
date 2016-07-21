'''
Created on 11.07.2016

@author: muelthil
'''
import sys
import lnetatmo
 
# Device-Liste von Netatmo abholen
authorization = lnetatmo.ClientAuth()
devList = lnetatmo.DeviceList(authorization)
# Funktionen um die ID von Modulen und Device zu ermitteln
print(devList.modulesNamesList())
# Niederschlag ist der Modulname meines Regenmessers
print(devList.moduleByName('GardenTemp'))
gardentemp=devList.lastData()['GardenTemp']['Temperature']
print (gardentemp)


