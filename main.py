from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.uix.carousel import Carousel
from kivy.uix.boxlayout import BoxLayout
import urllib.error


import time
#import netatmoreadings
from netatmoreadings import ClientAuth
from netatmoreadings import netatmoreadings
from netatmoreadings import DeviceList
import traceback
import socket
import os
import struct
import threading


from time import strftime


class KivyNetatmoClock (Carousel):
    def  update (self,dt):
        self.load_next()

class KivyNetatmoClockApp(App):
    debug=True
    ip="x.x.x.x"
    sw_started = False
    sw_seconds = 2
    ipfetched=False
    GardenTemperature=1.5
    time_started=False
    title="Starting..."
    outsidetemp="0"
    outsidetempminmax="0"
    humidity="0"
    running = True
    pressurehumidity=0
    callnetatmotime=""
    thilo_presence=None
    

    def on_start(self):
        Clock.schedule_interval(self.update, 1)
        threading.Thread(target=self.callnetatmo, args="1").start()
        
        
    def callnetatmo(self,nap):
        while self.running:
            print ("Calling FHEM at "+strftime('%H:%M:%S'))
            
            try:
                server="http://16.22.34.138"
                port="8083"
                fhem_request="/fhem?cmd="
                variable="thilo_presence"
                #"http://16.22.34.138:8083/fhem?cmd=set%20thilo_dummy%20off"
                #http://16.22.34.138:8083/fhem?cmd=%7BValue%28%22thilo_dummy%22%29%7D&XHR=1 -> on, XHR is no HTML
                req = urllib.request.Request(server+":"+ port+fhem_request+"%7BValue%28%22"+variable+"%22%29%7D&XHR=1")
                req.add_header("Content-Type","application/x-www-form-urlencoded;charset=utf-8")
                #params = urllib.parse.urlencode(params).encode('utf-8')
                resp = urllib.request.urlopen(req,None, 5).read(65535).decode("utf-8")
                print ("FHEM Response "+resp)
                if (resp=="present\n") :
                    self.thilo_presence=True
                    print ("Thilo set presence true")

            except Exception as err:
                print("Error occured {0}".format(err))
                print (traceback.format_exc())
        
            
            print("Calling Netatmo at "+strftime('%H:%M:%S'))
            self.callnetatmotime=strftime('%H:%M:%S')

            # Device-Liste von Netatmo abholen
            try:
                
                authorization = ClientAuth()
                devList = DeviceList(authorization)
                sd =devList.getStationdata (device_id='70:ee:50:17:4e:dc')
                na=netatmoreadings(sd)
                
                
                
                print ("Outdoor Temperature "+str(na.na_TemperatureOutdoor)+" Humidity "+str(na.na_HumidityOutdoor)+ " Min "+str(na.na_TemperatureOutdoorMin) + " Max "+str(na.na_TemperatureOutdoorMax)+ " Trend "+str(na.na_TemperatureOutdoorTrend))
                print ("Indoor Temperature "+str(na.na_Temperature) + ", Temp Trend " + str(na.na_TempTrend)+ " Temp min "+ str(na.na_MinTemp) + " Temp max " + str(na.na_MaxTemp)+ " Humidity "+str(na.na_Humidity)) 
                print ("Rain "+ str(na.na_Rain)+ " last hour sum1 "+str(na.na_Rain_sum1)+" sum 24h "+str (na.na_Rain_sum24))
                print ("Batteries  Outdoor "+str(na.na_battery_outdoor_percent)+ " Rain "+str(na.na_battery_rain_percent))


                print("Connected to Netatmo")
                # Funktionen um die ID von Modulen und Device zu ermitteln
                #print("DeviceList ")
                #print(devList.modulesNamesList())
                # Niederschlag ist der Modulname meines Regenmessers
                #print("GardenTemp ")
                ##print(devList.moduleByName('GardenTemp'))
                #print("--")
                #print("GardenRain ")
                #print(devList.moduleByName('GardenRain'))

 
 
 
                ## Ermittlung der aktuellen Wetterdaten ---------------------------------------------
                
                # Aktuelle Aussentemperatur ausgeben
                #print("GardenTemperature ")
                #gardentemp=devList.lastData()['GardenTemp']['Temperature']
                #print("GardenTemperature called.")
            
        
                #self.root.ids.time.text = strftime('[b]%H:%M[/b]:%S')+"   {:.2f}°C".format(devList.lastData()['GardenTemp']['Temperature'])
                self.time_started=True
                self.outsidetemp="   {:.2f}°C".format(na.na_TemperatureOutdoor)
                self.outsidetempminmax = "Aussen Min {:.2f}°C".format(na.na_TemperatureOutdoorMin) +" - Max {:.2f}°C".format(na.na_TemperatureOutdoorMax)
                self.pressurehumidity="Luftdruck   {:.2f}".format(na.na_Pressure)+" Feuchtigkeit {:.2f}%".format(na.na_HumidityOutdoor)
            
                rain=na.na_Rain
                sumrain24=na.na_Rain_sum24
            
                if rain > 0 or sumrain24 > 0 :
                    self.rain=" Regen {:.2f} ".format(na.na_Rain)+"- 24h {:.2f}".format(na.na_Rain_sum24)
                else:
                    pass
                
                
            #m, s = divmod(self.sw_seconds, 60)
            #           self.root.ids.stopwatch.text = ('%02d:%02d.[size=40]%02d[/size]' %
            #                                      (int(m), int(s), int(s * 100 % 100)))
       
            except urllib.error.URLError as e:
                print('URLError {0}'.format(e))
            except socket.error as e:
                print('Socket error {0}'.format(e))
            except socket.timeout as e:
                print('Socket Timeout {0}'.format(e))
            except UnicodeEncodeError as e:
                print('Unicode Error {0}'.format(e))
            except urllib.error.URLError as e:
                print('URLError {0}'.format(e))
                #ResponseData = e.read().decode("utf8", 'ignore')
            except Exception as err:
                print("Error occured {0}".format(err))
                print (traceback.format_exc())
        
            print("Everything okay")
            self.sw_started=True
        

            time.sleep (60)
        
    def update(self, nap):
        
        
        if self.sw_started:
            self.sw_seconds += nap

        
        
            self.time_started=True
            
            self.root.ids.outsidetempminmax.text = self.outsidetempminmax 
            self.root.ids.pressurehumidity.text=self.pressurehumidity
            if self.thilo_presence :
                self.root.ids.status.text="Thilo ist anwesend"
            

        if self.time_started:
            self.root.ids.time.text = strftime('[b]%H:%M[/b]:%S')+ self.outsidetemp
        
        if self.debug:
                if self.ipfetched: 
                    self.root.ids.debug.text="Netatmo called at - "+self.callnetatmotime + "- IP {0}".format(self.ip)
                else:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.connect(("8.8.8.8", 80))
                    self.ip= s.getsockname()
                    self.ipfetched=True
            
            
    def updateTime(self,nap):
        if self.time_started:
            self.root.ids.time.text = strftime('[b]%H:%M[/b]:%S')+ self.outsidetemp
                
    
    def reset(self):
        if self.sw_started:
            self.root.ids.start_stop.text = 'Start'
            self.sw_started = False

        self.sw_seconds = 0
    
    def appstop(self):
        print ("Restarting..")
        self.running=False
        self.stop()
        
    
    def start_debug(self):
        print ("Enter debug mode")
        self.debug=True
    
    def testme(self):
        print ("Testing")
    

    def build(self):
        self.title="Kivy Netatmo Clock"
        kivyNetatmoClock=KivyNetatmoClock()
        return kivyNetatmoClock
        
    def on_stop(self):
        self.running=False

if __name__ == '__main__':
    Window.clearcolor = get_color_from_hex('#101216')
    LabelBase.register(name='Roboto',
                       fn_regular='Roboto-Light.ttf',
                       fn_bold='Roboto-Medium.ttf')

            
    KivyNetatmoClockApp().run()
