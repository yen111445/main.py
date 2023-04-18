import speech_recognition as sr
import time
import threading
import re
import requests

import pyttsx3
import datetime
import pandas as pd
import sys

engine = pyttsx3.init()
rate = engine.getProperty('rate')
engine.setProperty('rate', rate)
volume = engine.getProperty('volume')
engine.setProperty('volume', volume)

## 抓取天氣資料
url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-D0047-091?Authorization=rdec-key-123-45678-011121314'
r = requests.get(url)
data = pd.read_json(r.text)
data = data.loc['locations', 'records']
data = data[0]['location']
loc_data = data[9] # 第十個資料為台北市
weather_data = loc_data['weatherElement']
ele_data_dict = weather_data[10] # 天氣描述資料
ele_data = ele_data_dict['time']
weather_value = ele_data[0]['elementValue'][0]['value']

## 番茄鐘函數
def tomato_clock(minutes, rounds, rest):
    
    engine.say('第1個番茄鐘開始!')
    engine.runAndWait()
    
    sys.stdout.write("\r第1個番茄鐘開始!            \n")

    for remaining in range(minutes*60, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("{:2d} seconds remaining.".format(remaining))
        sys.stdout.flush()
        time.sleep(1)
        
    sys.stdout.write("\r第1個番茄鐘完成!            \n")
    engine.say('第1個番茄鐘完成!')
    engine.runAndWait()
        
    for i in range(1, rounds):
        
        engine.say('休息時間!!')
        engine.runAndWait()
        sys.stdout.write("\r休息時間!            \n")
        
        for rest_min in range(rest*60, 0, -1):
            sys.stdout.write("\r")
            sys.stdout.write("{:2d} seconds remaining.".format(rest_min))
            sys.stdout.flush()
            time.sleep(1)
            
        engine.say('休息結束!!')
        sys.stdout.write("\r休息結束!                \n")
        
        
        engine.say("第{}個番茄鐘開始!".format(i+1))
        engine.runAndWait()
        sys.stdout.write("\r第{}個番茄鐘開始!            \n".format(i+1))
            
        for remaining in range(minutes*60, 0, -1):
            sys.stdout.write("\r")
            sys.stdout.write("{:2d} seconds remaining.".format(remaining))
            sys.stdout.flush()
            time.sleep(1)
        
        engine.say("第{}個番茄鐘完成!".format(i+1))
        engine.runAndWait()
        sys.stdout.write("\r第{}個番茄鐘完成!            \n".format(i+1))
        
    engine.say("完成本次的番茄鐘!")
    engine.runAndWait()
    print('完成本次的番茄鐘!')

try:

    while True:

        r = sr.Recognizer()
        m = sr.Microphone()
        m.RATE = 44100
        m.CHUNK = 512

        print("請稍候")
        with m as source:
            r.adjust_for_ambient_noise(source)
            if (r.energy_threshold < 2000):
                r.energy_threshold = 2000
            # print("Set minimum energy threshold to {}".format(r.energy_threshold))

            print("請下指令")
            audio = r.listen(source)
            print("語音辨識中")

            speechtext = r.recognize_google(audio,language='zh',show_all=True) #Load Google Speech Recognition API
            print(type(speechtext)) #dict
            if len(speechtext) == 0:
                pass
            else:
                speechtext = speechtext['alternative'][0]['transcript']
                speechtext = speechtext.replace(' ', '')
                print("收到指令: " + speechtext)

                if re.search('\s*日期\s*',speechtext) or re.search('\s*幾號\s*',speechtext) :
                    
                    now = datetime.datetime.now()
                    engine.say('今天是，{}月，{}日'.format(now.month, now.day))
                    engine.runAndWait()
                
                elif re.search('\s*時間\s*',speechtext) or re.search('\s*幾點\s*',speechtext) :

                    now = datetime.datetime.now()
                    engine.say('現在時間是，{}點，{}分'.format(now.hour, now.minute))
                    engine.runAndWait()

                elif re.search('\s*天氣\s*',speechtext):

                    engine.say(weather_value)
                    engine.runAndWait()

                elif re.search('\s*番茄\s*',speechtext):

                    engine.say('輸入要設定的番茄鐘數量 ')
                    engine.runAndWait()
                    rounds = int(input('輸入要設定的番茄鐘數量 '))
                    engine.say('輸入一次番茄鐘的時間（分鐘） ')
                    engine.runAndWait()
                    minutes = int(input('輸入一次番茄鐘的時間（分鐘）'))
                    engine.say('輸入休息的時間（分鐘）')
                    engine.runAndWait()
                    rest = int(input('輸入休息的時間（分鐘）'))

                    print('\n')
                    tomato_clock(minutes, rounds, rest)
                    
                elif re.search('\s*結束程式\s*',speechtext):
                    print('結束程式運作')
                    break
                    
except KeyboardInterrupt:
    print("Quit")



