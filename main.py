from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.uix.carousel import Carousel
from kivy.uix.boxlayout import BoxLayout
import urllib.error


import time
import lnetatmo
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
    callnetatmotime=""
    

    def on_start(self):
        Clock.schedule_interval(self.update, 1)
        threading.Thread(target=self.callnetatmo, args="1").start()
        
        
    def callnetatmo(self,nap):
        while self.running:
        
            print("Calling Netatmo at "+strftime('%H:%M:%S'))
            self.callnetatmotime=strftime('%H:%M:%S')

            # Device-Liste von Netatmo abholen
            try:
                authorization = lnetatmo.ClientAuth()
                devList = lnetatmo.DeviceList(authorization)
                print("Connected to Netatmo")
                # Funktionen um die ID von Modulen und Device zu ermitteln
                print("DeviceList ")
                print(devList.modulesNamesList())
                # Niederschlag ist der Modulname meines Regenmessers
                print("GardenTemp ")
                print(devList.moduleByName('GardenTemp'))
                print("--")
                print("GardenRain ")
                print(devList.moduleByName('GardenRain'))

 
 
 
                ## Ermittlung der aktuellen Wetterdaten ---------------------------------------------
                
                # Aktuelle Aussentemperatur ausgeben
                print("GardenTemperature ")
                gardentemp=devList.lastData()['GardenTemp']['Temperature']
                print("GardenTemperature called.")
            
        
                # Wetterdaten des Vortages ermitteln: -----------------------------------------------
                now = time.time()               # Von Jetzt
                start = now - 2* 24 * 3600

                #Ermittlung der Temperaturen als Liste
                resp = devList.getMeasure( device_id='70:ee:50:17:4e:dc',      
                                           module_id='02:00:00:17:d9:24',    
                                           scale="1day",
                                           mtype="min_temp,max_temp",
                                           date_begin=start,
                                           date_end=now)
 
                        # Extraieren von Zeit, minTemp und Maxtemp
                result = [(int(k),v[0],v[1]) for k,v in resp['body'].items()]
                        # Liste sortieren (nach Zeit, da erstes Element)
                result.sort()
        
                messdatum = time.localtime(result[0][0])
                #Ermittlung des Datums des Vortages der Min/Max Temperaturen vom Vortag
                messdatum = time.localtime(result[0][0])
 
                #Ermittlung der Min- und Max-Temperaturen des Vortages
                last_temp_min = result[0][1]
                last_temp_max = result[0][2]

            
                #self.root.ids.time.text = strftime('[b]%H:%M[/b]:%S')+"   {:.2f}°C".format(devList.lastData()['GardenTemp']['Temperature'])
                self.time_started=True
                self.outsidetemp="   {:.2f}°C".format(devList.lastData()['GardenTemp']['Temperature'])
                self.outsidetempminmax = "{:.2f}°C".format(devList.lastData()['GardenTemp']['min_temp']) +" - {:.2f}°C".format(devList.lastData()['GardenTemp']['max_temp'])+"    Gestern: "+" {:.2f}°C".format(last_temp_min) + " - {:.2f}°C".format(last_temp_max)
            
                rain=devList.lastData()['GardenRain']['Rain']
                sumrain24=devList.lastData()['GardenRain']['Rain']
            
                if rain > 0 or sumrain24 > 0 :
                    self.humidity="Feuchtigkeit {:.2f}%".format(devList.lastData()['GardenTemp']['Humidity'])+"Regen {:.2f}".format(devList.lastData()['GardenRain']['Rain'])+"- 24h {:.2f}".format(devList.lastData()['GardenRain']['Rain'])
                else:
                    self.humidity="Feuchtigkeit {:.2f}%".format(devList.lastData()['GardenTemp']['Humidity'])
                
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
        

            time.sleep (60*60)
        
    def update(self, nap):
        
        
        if self.sw_started:
            self.sw_seconds += nap

        
        
            self.time_started=True
            
            self.root.ids.outsidetempminmax.text = self.outsidetempminmax 
            self.root.ids.humidity.text=self.humidity

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
