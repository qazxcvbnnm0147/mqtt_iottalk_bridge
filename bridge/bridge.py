# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 15:11:08 2021

@author: user
"""


import DAN
import paho.mqtt.client as mqtt 
import time
import paho.mqtt.subscribe as subscribe
import os
import threading 


def register_me(MAC,TOPIC,URL):    
    DAN.profile['df_list']=[Topic_deal(TOPIC,'df_list')]
    DAN.profile['d_name']=Topic_deal(TOPIC,'d_name')
    DAN.profile['dm_name']=Topic_deal(TOPIC,'dm_name')
    DAN.bridge_register(URL,MAC)
        
def Topic_deal(Topic,ouput):
    Topic,df_list=os.path.split(Topic)
    Topic,d_name=os.path.split(Topic)
    Topic,dm_name=os.path.split(Topic)
    if ouput=='dm_name':
        return dm_name
    if ouput=='d_name':
        return d_name
    if ouput=='df_list':
        return df_list


ListURL = "http://iottalk.cmoremap.com.tw:9999/list_all"
ServerURL = 'http://iottalk.cmoremap.com.tw:9999'      #with non-secure connection
#ServerURL = 'https://DomainName' #with SSL connection
#Reg_addr = None #if None, Reg_addr = MAC address

host="13.213.7.109"
auth={}
MQTT_TOPIC = "iottalk/Dummy_Device/#"
client_id=''

client = mqtt.Client()
# # 設定連線資訊(IP, Port, 連線時間)
client.connect("13.213.7.109", 1883, 60)

DAN.set_URL(ServerURL)
        

done = False

def listen_for_enter_key_press():    
    global done
    input()
    done=True
    
key_break = threading.Thread(target = listen_for_enter_key_press)

def iottomqtt():
    key_break.start()
    while(done!=True):
        iottalk_list,iottalk_value=DAN.get_iottalk_list(ListURL,ServerURL)
        for i in range(len(iottalk_list)):
             client.publish(iottalk_list[i],iottalk_value[i])
        print("done")
    key_break.join()
        
t = threading.Thread(target = iottomqtt)
t.start()

while (done !=True):
    try:
        msg = subscribe.simple(MQTT_TOPIC, qos=1, hostname=host, client_id=client_id, auth=auth)
        Reg_addr=Topic_deal(msg.topic,"d_name")
        df_list=Topic_deal(msg.topic,"df_list")
        register_me(Reg_addr,msg.topic,ServerURL)
        print("%s %s" % (msg.topic, msg.payload.decode('utf-8')))
        value=msg.payload.decode('utf-8')
        if (value != "" and value != "none"):
            DAN.push_me(Reg_addr,df_list,float(value))        
        
    except Exception as e:
        print(e)
        if str(e).find('mac_addr not found:') != -1:
            print('Reg_addr is not found. Try to re-register...')
            DAN.device_registration_with_retry(ServerURL, Reg_addr)
        else:
            print('Connection failed due to unknow reasons.')
            time.sleep(1)    
            
    time.sleep(0.1)
    
t.join()

print('bridge closed')