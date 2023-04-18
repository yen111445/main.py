#%%
import os
import cv2
import sys
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import torch

ROOT_DIR = os.path.abspath(os.getcwd())
sys.path.append(ROOT_DIR)

from models.experimental import attempt_load
from utils.datasets import LoadStreams
from utils.general import  non_max_suppression, scale_coords
from utils.plots import colors
#%% GPU
device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
print('GPU State:', device)
#%%
WEIGHTPATH = os.getcwd() + '/weight/best.pt'
model = attempt_load(WEIGHTPATH, map_location = device)
model.to(device)
#%%
def detect_person(det):
    '''
    狀態偵測 : 偵測到 "Person" 回傳True，其餘皆回傳False
    '''
    for info in det:
        if info[5] == 0:
            return True
        else:
            return False

def plot_item(img, det):
    '''
    顯示偵測物品 label & probability (針對 "Person" 做偵測)
    '''
    img = Image.fromarray(img)
    draw = ImageDraw.Draw(img)
    fontsize = max(round(max(img.size) / 40), 12)
    font = ImageFont.truetype(os.getcwd() + '/text/Arial.ttf', fontsize)
    names = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
             'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
             'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
             'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
             'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
             'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
             'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
             'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear',
             'hair drier', 'toothbrush']

    for info in det:
        target, prob = int(info[5].cpu().numpy()), np.round(info[4].cpu().numpy(), 2)
        color = colors(1)
        if names[target] == 'person' and prob > 0.5:
            xmin, ymin, xmax, ymax = info[0], info[1], info[2], info[3]
            draw.rectangle([xmin, ymin, xmax, ymax], width = 3, outline = color)
            draw.text((xmin, ymin), names[target] + ':' + str(prob), fill = color, font = font)
    return np.array(img)
    
def webcam_show(d_in):
    cnt = 0 #計數狀態幀數
    for path, img, im0s, vid_cap in d_in:
        numpy_img = img.copy()
        img = torch.from_numpy(img).to(device)
        img = img.float() 
        img /= 255.0
        pred = model(img)[0]
        pred = non_max_suppression(pred, 0.25, 0.45)

        for i, det in enumerate(pred):  
            im0 = im0s[i].copy()
            det[:, :4] = scale_coords(numpy_img.shape[2:], det[:, :4], im0.shape).round()
            im0 = plot_item(im0, det)
            if detect_person(det) == False or detect_person(det) == None : cnt += 1
            else : 
                cnt = 0
                print('Wake up!!!')
                time.sleep(1)
                sys.stdout.flush()

        if(cnt > 100) : break#無人狀態幀數累積100關閉 webcam & 鬧鐘
        cv2.imshow('frame', im0)
    cv2.destroyAllWindows()
    return False

def Alarm_clock(t_in): #智慧鬧鐘功能
    wake_up_time = t_in
    while True:
        localtime = str(time.localtime()[3]) + ':' + str(time.localtime()[4]) #電腦主機時間
        if(localtime == wake_up_time):
            dataset = LoadStreams('0')
            status = webcam_show(dataset)
            if(status == False): break

    print(time.localtime())
    return [i for i in time.localtime()]
#%%
if __name__ == '__main__':
    while True:
        print('0 : Stop')
        print('1 : Alarm_clock')
        print('2 : Voice & Tomato_clock')
        n = int(input('Select Func = '))
        if n == 0:
            break

        elif n == 1:
            from mylib import google_sheet
            ws = google_sheet.GoogleSheet('mylib/python-digit-aa0bcbb1a168.json', 'digit')
            set_time = str(input('設定鬧鐘時間 XX : XX = '))
            ws.set_time(set_time + ':0') #設定鬧鐘時間
            wake_up_time = Alarm_clock(set_time)
            Date = str(wake_up_time[0]) + '-' + str(wake_up_time[1]) + '-' + str(wake_up_time[2])#Y M D
            Time = str(wake_up_time[3]) + ':' + str(wake_up_time[4]) + ':' + str(wake_up_time[5])#H M S
            ws.wake_up(Date + ' ' + Time)#離開床時間

        elif n == 2:
            from mylib import voice_clock

        else:
            print('No Function')

# %%
# %%
