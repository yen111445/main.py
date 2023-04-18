import cv2
import torch
import os
import time
import datetime
import numpy as np
import json
import requests
import threading
import serial
import time
import cProfile



#---------------------------------------------------------------------------------------


#讀取onnx格式內按索引值去發對應信息
labels = ['t1', 't2', 't3', 't4', 't5']
num_classes = len(labels)
# print("Number of classes:", num_classes)
# signals = {'t1': 'TT', 't2': 'YY', 't3': 'UU', 't4': 'PP'}
signals = {'t1': '人類', 't2': '腳踏車', 't3': '汽車', 't4': '摩托車'}
model = torch.hub.load('ultralytics/yolov5', 'custom', path='C:\\Users\\tfr52\\OneDrive\\桌面\\yolov5-master\\weights\\yolov5s.onnx')
cap = cv2.VideoCapture(0)
file_count = 0


#---------------------------------------------------------------------------------------
#這方法不要亂動會烙賽
#這方法把detections值抓出來朝這網站發POST
# def Fish_Json(detections):
#     detections_json = json.dumps({'detections': detections})
#     # 打印json字符串
#     print(detections_json)
# #一個迴圈一直跑
#     # 連接ㄉ路徑
# ser = serial.Serial('COM21', 9600, timeout=1)
#     # 等等啦
#     #     time.sleep(0.5)     # 發送資料到接口
#         ser.write(detections_json.encode())
#         response = ser.readline().decode('utf-8').strip()
#         print(response)
#     ser.close()
#---------------------------------------------------------------------------------------

#底下執行緒至抓到後的字串會被抓出來傳給RS232端口
def Fish_Json(detections):
    detections_json = json.dumps({'detections': detections})
    print(detections_json)
    # 你各位ㄉ連接接口號  9600那ㄍ是傳輸速度
    ser = serial.Serial('COM3', 9600, timeout=1)
    # 發送資料到接口
    ser.write(detections_json.encode())
    # response = ser.readline().decode('utf-8').strip()   如果想要RS232回傳ㄉ東西這兩串就要開&但開ㄌ卡爆
    # print(response)
    ser.close()

#---------------------------------------------------------------------------------------

# 程式一打開這個執行緒就會開始跑，對應最底下ㄉ

def detect_and_upload():
    # 取label位數  取出物件ID對應上面的信號丟到detections內後不管是不是空的都會一直跑
    while True:
        ret, frame = cap.read()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = cv2.resize(rgb, (640, 640))
        results = model(rgb[:, :, ::-1])
        detections = []
        for obj in results.xyxy[0]:
            class_id = int(obj[5])
            if class_id >= 0 and class_id < num_classes:
                label = labels[class_id]
                if label in signals:
                    signal = signals[label]
                    print('檢測到' + signal)
                    detections.append(signal)
            else:
                continue
        if detections:
            Fish_Json(detections)
        detections = []
        for obj in results.xyxy[0]:
            class_id = int(obj[5])
            if class_id >= 0 and class_id < num_classes:
                label = labels[class_id]
                if label in signals:
                    detections.append(signals[label])
            else:
                continue
        cv2.imshow('test', results.render()[0])
        if cv2.waitKey(1) == ord('q'):
            break
        # time.sleep(0.5)  # 0.5秒後繼續執行檢測 到時候如果是1秒檢查2條應該就要設定


# ---------------------------------------------------------------------------------------

if __name__ == "__main__":      #如果這支是主程式就會執行底下ㄉ執行緒
    t = threading.Thread(target=detect_and_upload)
    t.start()
    if cap.isOpened():
        cap


