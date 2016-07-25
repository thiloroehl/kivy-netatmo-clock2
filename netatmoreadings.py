'''
Created on 11.07.2016

@author: muelthil
'''
import sys
import os
import json, time
import lnetatmo2
import urllib.parse, urllib.request
import configparser

######################## USER SPECIFIC INFORMATION ######################

# To be able to have a program accessing your netatmo data, you have to register your program as
# a Netatmo app in your Netatmo account. All you have to do is to give it a name (whatever) and you will be
# returned a client_id and secret that your app has to supply to access netatmo servers.

_CLIENT_ID     = ""   # Your client ID from Netatmo app registration at http://dev.netatmo.com/dev/listapps
_CLIENT_SECRET = ""   # Your client app secret   '     '
_USERNAME      = ""   # Your netatmo account username
_PASSWORD      = ""   # Your netatmo account password

#########################################################################

# Common definitions

_BASE_URL       = "https://api.netatmo.net/"
_AUTH_REQ       = _BASE_URL + "oauth2/token"
_GETUSER_REQ    = _BASE_URL + "api/getuser"
_DEVICELIST_REQ = _BASE_URL + "api/devicelist"
_GETSTATIONDATA_REQ = _BASE_URL + "api/getstationsdata"

class ClientAuth:
    "Request authentication and keep access token available through token method. Renew it automatically if necessary"

    def __init__(self, clientId=_CLIENT_ID,
                       clientSecret=_CLIENT_SECRET,
                       username=_USERNAME,
                       password=_PASSWORD):

        config = configparser.ConfigParser()
        config.sections()
        config.read('netatmo-pythonconfig.ini')
        if os.name == 'nt': # Windows Operating System
            self._CLIENT_ID     = config['WINDOWS']['CLIENT_ID']
            self._CLIENT_SECRET = config['WINDOWS']['CLIENT_SECRET']   # Your client app secret   '     '
            self._USERNAME      = config['WINDOWS']['USERNAME']   # Your netatmo account username
            self._PASSWORD      = config['WINDOWS']['PASSWORD']   # Your netatmo account password
        else:
            self._CLIENT_ID     = config['OTHER']['CLIENT_ID']  # Your client ID from Netatmo app registration at http://dev.netatmo.com/dev/listapps
            self._CLIENT_SECRET = config['OTHER']['CLIENT_SECRET']   # Your client app secret   '     '
            self._USERNAME      = config['OTHER']['USERNAME']   # Your netatmo account username
            self._PASSWORD      = config['OTHER']['PASSWORD']   # Your netatmo account password


        postParams = {
                "grant_type" : "password",
                "client_id" : self._CLIENT_ID,
                "client_secret" : self._CLIENT_SECRET,
                "username" : self._USERNAME,
                "password" : self._PASSWORD,
                "scope" : "read_station"
                }
        resp = postRequest(_AUTH_REQ, postParams)

        #self._clientId = clientId
        #self._clientSecret = clientSecret
        self._accessToken = resp['access_token']
        self.refreshToken = resp['refresh_token']
        self._scope = resp['scope']
        self.expiration = int(resp['expire_in'] + time.time())

    @property
    def accessToken(self):

        if self.expiration < time.time(): # Token should be renewed

            postParams = {
                    "grant_type" : "refresh_token",
                    "refresh_token" : self.refreshToken,
                    "client_id" : self._clientId,
                    "client_secret" : self._clientSecret
                    }
            resp = postRequest(_AUTH_REQ, postParams)

            self._accessToken = resp['access_token']
            self.refreshToken = resp['refresh_token']
            self.expiration = int(resp['expire_in'] + time.time())

        return self._accessToken

def postRequest(url, params):
    # Netatmo response body size limited to 64k (should be under 16k)
    
        req = urllib.request.Request(url)
        req.add_header("Content-Type","application/x-www-form-urlencoded;charset=utf-8")
        params = urllib.parse.urlencode(params).encode('utf-8')
        resp = urllib.request.urlopen(req, params,5).read(65535).decode("utf-8")
    
        return json.loads(resp)

_stationData=dict()

class DeviceList:

    def __init__(self, authData):
        
        self.getAuthToken = authData.accessToken
        #postParams = {
        #        "access_token" : self.getAuthToken,
        #        "app_type" : "app_station"
        #        }
        #resp = postRequest(_DEVICELIST_REQ, postParams)
        #self.rawData = resp['body']
        #self.stations = { d['_id'] : d for d in self.rawData['devices'] }
        #self.modules = { m['_id'] : m for m in self.rawData['modules'] }
        #self.default_station = list(self.stations.values())[0]['station_name']
        
    # TR testing
    def getStationdata(self,device_id):
        postParams = { "access_token" : self.getAuthToken }
        postParams['device_id']  = device_id
        return postRequest(_GETSTATIONDATA_REQ, postParams)
    
    def modulesNamesList(self, station=None):
        res = [m['module_name'] for m in self.modules.values()]
        res.append(self.stationByName(station)['module_name'])
        return res

    def stationByName(self, station=None):
        if not station : station = self.default_station
        for i,s in self.stations.items():
            if s['station_name'] == station : return self.stations[i]
        return None

    def stationById(self, sid):
        return None if sid not in self.stations else self.stations[sid]

    def moduleByName(self, module, station=None):
        s = None
        if station :
            s = self.stationByName(station)
            if not s : return None
        for m in self.modules:
            mod = self.modules[m]
            if mod['module_name'] == module :
                if not s or mod['main_device'] == s['_id'] : return mod
        return None

    def moduleById(self, mid, sid=None):
        s = self.stationById(sid) if sid else None
        if mid in self.modules :
            return self.modules[mid] if not s or self.modules[mid]['main_device'] == s['_id'] else None

    def lastData(self, station=None, exclude=0):
        print("lastData called")
        s = self.stationByName(station)
        
        if not s : return None
        lastD = dict()
        # Define oldest acceptable sensor measure event
        limit = (time.time() - exclude) if exclude else 0
        ds = s['dashboard_data']
        if ds['time_utc'] > limit :
            lastD[s['module_name']] = ds.copy()
            lastD[s['module_name']]['When'] = lastD[s['module_name']].pop("time_utc")
            lastD[s['module_name']]['wifi_status'] = s['wifi_status']
        for mId in s["modules"]:
            ds = self.modules[mId]['dashboard_data']
            if ds['time_utc'] > limit :
                mod = self.modules[mId]
                lastD[mod['module_name']] = ds.copy()
                lastD[mod['module_name']]['When'] = lastD[mod['module_name']].pop("time_utc")
                # For potential use, add battery and radio coverage information to module data if present
                for i in ('battery_vp', 'rf_status') :
                    if i in mod : lastD[mod['module_name']][i] = mod[i]
        return lastD

    def checkNotUpdated(self, station=None, delay=3600):
        res = self.lastData(station)
        ret = []
        for mn,v in res.items():
            if time.time()-v['When'] > delay : ret.append(mn)
        return ret if ret else None

    def checkUpdated(self, station=None, delay=3600):
        res = self.lastData(station)
        ret = []
        for mn,v in res.items():
            if time.time()-v['When'] < delay : ret.append(mn)
        return ret if ret else None

    def getMeasure(self, device_id, scale, mtype, module_id=None, date_begin=None, date_end=None, limit=None, optimize=False, real_time=False):
        postParams = { "access_token" : self.getAuthToken }
        postParams['device_id']  = device_id
        if module_id : postParams['module_id'] = module_id
        postParams['scale']      = scale
        postParams['type']       = mtype
        if date_begin : postParams['date_begin'] = date_begin
        if date_end : postParams['date_end'] = date_end
        if limit : postParams['limit'] = limit
        postParams['optimize'] = "true" if optimize else "false"
        postParams['real_time'] = "true" if real_time else "false"
        return postRequest(_GETMEASURE_REQ, postParams)

    
    
    def MinMaxTH(self, station=None, module=None, frame="last24"):
        if not station : station = self.default_station
        s = self.stationByName(station)
        if not s :
            s = self.stationById(station)
            if not s : return None
        if frame == "last24":
            end = time.time()
            start = end - 24*3600 # 24 hours ago
        elif frame == "day":
            start, end = todayStamps()
        if module and module != s['module_name']:
            m = self.moduleByName(module, s['station_name'])
            if not m :
                m = self.moduleById(s['_id'], module)
                if not m : return None
            # retrieve module's data
            resp = self.getMeasure(
                    device_id  = s['_id'],
                    module_id  = m['_id'],
                    scale      = "max",
                    mtype      = "Temperature,Humidity",
                    date_begin = start,
                    date_end   = end)
        else : # retrieve station's data
            resp = self.getMeasure(
                    device_id  = s['_id'],
                    scale      = "max",
                    mtype      = "Temperature,Humidity",
                    date_begin = start,
                    date_end   = end)
        if resp:
            T = [v[0] for v in resp['body'].values()]
            H = [v[1] for v in resp['body'].values()]
            return min(T), max(T), min(H), max(H)
        else:
            return None


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
    authorization = ClientAuth()
    devList = DeviceList(authorization)
    # Funktionen um die ID von Modulen und Device zu ermitteln
    #print(devList.modulesNamesList())
    # Niederschlag ist der Modulname meines Regenmessers
    #print(devList.moduleByName('70:ee:50:17:4e:dc'))
    #gardentemp=devList.lastData()['70:ee:50:17:4e:dc']['Temperature']
    #print (gardentemp)
    #print ("Station Data")
    sd =devList.getStationdata (device_id='70:ee:50:17:4e:dc')
    
    #rawData = sd['body']
    #stations = { d['_id'] : d for d in rawData['devices'] }
    #modules = { m['_id'] : m for m in stations['modules'] }
    #default_station = list(stations.values())[0]['station_name']
    
    
    #sd =DeviceList(authorization, device_id='70:ee:50:17:4e:dc')
    na=netatmoreadings(sd)
    #na.__init__(sd)
    
    print ("Outdoor Temperature "+str(na.na_TemperatureOutdoor)+" Humidity "+str(na.na_HumidityOutdoor)+ " Min "+str(na.na_TemperatureOutdoorMin) + " Max "+str(na.na_TemperatureOutdoorMax)+ " Trend "+str(na.na_TemperatureOutdoorTrend))
    print ("Indoor Temperature "+str(na.na_Temperature) + ", Temp Trend " + str(na.na_TempTrend)+ " Temp min "+ str(na.na_MinTemp) + " Temp max " + str(na.na_MaxTemp)+ " Humidity "+str(na.na_Humidity)) 
    print ("Rain "+ str(na.na_Rain)+ " last hour sum1 "+str(na.na_Rain_sum1)+" sum 24h "+str (na.na_Rain_sum24))
    print ("Batteries  Outdoor "+str(na.na_battery_outdoor_percent)+ " Rain "+str(na.na_battery_rain_percent))