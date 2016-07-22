'''
Created on 11.07.2016

@author: muelthil
'''
import sys
import json, time
import lnetatmo2
import urllib.parse, urllib.request


 

_stationData=dict()


class netatmoreadings():
    na_Temperature=None
    na_MaxTemp=None
    na_MinTemp=None
    na_TempTrend=None
    na_TemperatureOutdoor=None
    na_TemperatureOutdoorMax=None
    na_TemperatureOutdoorMin=None
    na_TemperatureOutdoorTrend=None
    na_HumidityOutdoor=None
    na_Humidity=None
    na_Pressure=None
    na_Rain=None
    na_Rain_sum1=None
    na_Rain_sum24=None
    na_battery_base_percent=None
    na_battery_rain_percent=None
    na_battery_outdoor_percent=None
    modulecount=0
    
    def __init__(self, stationData):
        body=stationData["body"]
        devices=body["devices"]
        device=devices[0]
        

        self.na_Temperature=device["dashboard_data"]["Temperature"]
        self.na_MaxTemp=device["dashboard_data"]["max_temp"]
        self.na_MinTemp=device["dashboard_data"]["min_temp"]
        self.na_TempTrend=device["dashboard_data"]["temp_trend"]
        self.na_Humidity=device["dashboard_data"]["Humidity"]
        self.na_Pressure=device["dashboard_data"]["Pressure"]
        
        #dashboard=device["dashboard_data"]
        modules=device["modules"]
        
        
        for m in modules:
            if (m["data_type"].count('Rain')) > 0 :
                self.na_Rain=(m["dashboard_data"]["Rain"])
                self.na_Rain_sum1=(m["dashboard_data"]["sum_rain_1"])
                self.na_Rain_sum24=(m["dashboard_data"]["sum_rain_24"])
                self.na_battery_rain_percent=m["battery_percent"]
                pass
                    
            if (m["data_type"].count('Temperature')) > 0 :
                self.na_TemperatureOutdoor=m["dashboard_data"]["Temperature"]
                self.na_HumidityOutdoor=m["dashboard_data"]["Humidity"]
                self.na_TemperatureOutdoorMax=m["dashboard_data"]["max_temp"]
                self.na_TemperatureOutdoorMin=m["dashboard_data"]["min_temp"]
                self.na_TemperatureOutdoorTrend=m["dashboard_data"]["temp_trend"]
                self.na_battery_outdoor_percent=m["battery_percent"]
                pass
        
        self.modulecount=self.modulecount+1
    
    

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
    #print(devList.modulesNamesList())
    # Niederschlag ist der Modulname meines Regenmessers
    #print(devList.moduleByName('70:ee:50:17:4e:dc'))
    #gardentemp=devList.lastData()['70:ee:50:17:4e:dc']['Temperature']
    #print (gardentemp)
    #print ("Station Data")
    sd =devList.getStationdata (device_id='70:ee:50:17:4e:dc')
    na=netatmoreadings(sd)
    #na.__init__(sd)
    
    print ("Outdoor Temperature "+str(na.na_TemperatureOutdoor)+" Humidity "+str(na.na_HumidityOutdoor)+ " Min "+str(na.na_TemperatureOutdoorMin) + " Max "+str(na.na_TemperatureOutdoorMax)+ " Trend "+str(na.na_TemperatureOutdoorTrend))
    print ("Indoor Temperature "+str(na.na_Temperature) + ", Temp Trend " + str(na.na_TempTrend)+ " Temp min "+ str(na.na_MinTemp) + " Temp max " + str(na.na_MaxTemp)+ " Humidity "+str(na.na_Humidity)) 
    print ("Rain "+ str(na.na_Rain)+ " last hour sum1 "+str(na.na_Rain_sum1)+" sum 24h "+str (na.na_Rain_sum24))
    print ("Batteries  Outdoor "+str(na.na_battery_outdoor_percent)+ " Rain "+str(na.na_battery_rain_percent))
    
    




