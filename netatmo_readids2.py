'''
Created on 11.07.2016

@author: muelthil
'''
import sys
import lnetatmo2
from kivy.modules.screen import devices
 

_stationData=dict()


class netatmoreadings():
    na_Temperature=0
    na_MaxTemp=0
    na_MinTemp=0
    na_TempTrend=""
    na_Humidity=0
    na_Pressure=0
    na_rain=None
    
    
    def __init__(self, stationData=_stationData):
        print (sd)
        print (len(sd))
        body=sd["body"]
        print (body)
        devices=body["devices"]
        print (devices)
        #print ("Length of devices "+len(devices))
        device=devices[0]
        print (device)
        
        i=0
        for item in device:
            print ("Device i "+str(i))
            print (item)
            i=i+1
            
        dashboard=device["dashboard_data"]

        j=0
        for d in dashboard:
            print ("Dashboard j "+str(j))
            print (d)
            j=j+1
                
                

        print ("Temperature "+str(dashboard["Temperature"]))
        self.na_Temperature=dashboard["Temperature"]
        print ("MaxTemp "+str(dashboard["max_temp"]))
        self.na_MaxTemp=dashboard["max_temp"]
        print ("MinTemp "+str(dashboard["min_temp"]))
        self.na_MinTemp=dashboard["min_temp"]
        print ("TempTrend "+str(dashboard["temp_trend"]))
        self.na_TempTremp=dashboard["temp_trend"]
        print ("Humidity "+str(dashboard["Humidity"]))
        self.na_humidity=dashboard["Humidity"]
        print ("Pressure "+str(dashboard["Pressure"]))
        self.na_Pressure=dashboard["Pressure"]

        modules=device["modules"]
        print (modules)

        k=0
        for m in modules:
            print ("Module m "+str(k))
            #print (m)
            #print ("Count of Rain in data_type " +str(m["data_type"].count('Rain')))
            if (m["data_type"].count('Rain')) > 0 :
                print ("Rain found")
                print (m["dashboard_data"]["Rain"])
                print (m["dashboard_data"]["sum_rain_1"])
                print (m["dashboard_data"]["sum_rain_24"])
                    
                print (m["data_type"])
                if m["data_type"]=="Rain":
                    print ("Rain found")
                    dbrain=m["dashboard_data"]
                    print ("Rain "+str(dbrain["Rain"]))
                    print ("Sum Rain 1"+str(dbrain["sum_rain_1"]))
                    print ("Sum Rain 2"+str(dbrain["sum_rain_2"]))
                    pass
            k=k+1
    
    

                            # Module
                            # 02:00:00:17:d9:24
                            # Basisstion
                            #05:00:00:02:67:b4
                            # Rain
                            #
                            # Dashboard Data Rain, sum_rain_1, sum_rain_24
                            #
                            # 
                            # 
                            # 06:00:00:00:68:5a
                            # Wind
                            # Dashboard Data
                            #
                            #{'_id': '05:00:00:02:67:b4',
                            # 'battery_vp': 5860,
                            # 'dashboard_data': {'Rain': 0,
                            #                    'sum_rain_1': 1.212,
                            #                    'sum_rain_24': 5.454,
                            #                    'time_utc': 1469088631},
                            # 'data_type': ['Rain'],
                            # 'date_setup': {'sec': 1455649369, 'usec': 610000},
                            # 'firmware': 8,
                            # 'last_message': 1469088657,
                            # 'last_seen': 1469088657,
                            # 'main_device': '70:ee:50:17:4e:dc',
                            # 'module_name': 'GardenRain',
                            # 'rf_status': 79,
                            # 'type': 'NAModule3'}#

                            # 
                            #
                            #'battery_vp': 5613,
                            # 'dashboard_data': {'GustAngle': 270,
                            #                    'GustStrength': 2,
                            #                    'WindAngle': 307,
                            
                            #gardenTemp=devices["GardenTemp"]
                            #print (gardenTemp)

        

                            # Define oldest acceptable sensor measure event
if __name__ == "__main__":
    print ("Starting netatmo call")
    # Device-Liste von Netatmo abholen
    authorization = lnetatmo2.ClientAuth()
    devList = lnetatmo2.DeviceList(authorization)
    # Funktionen um die ID von Modulen und Device zu ermitteln
    print(devList.modulesNamesList())
    # Niederschlag ist der Modulname meines Regenmessers
    print(devList.moduleByName('70:ee:50:17:4e:dc'))
    #gardentemp=devList.lastData()['70:ee:50:17:4e:dc']['Temperature']
    #print (gardentemp)
    print ("Station Data")
    sd =devList.getStationdata (device_id='70:ee:50:17:4e:dc')
    na=netatmoreadings()
    na.__init__(sd)
    
    
    print ("Current Temperature")
    print (na.na_Temperature)
    






