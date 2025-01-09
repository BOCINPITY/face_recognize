import os
import cv2 as cv
from PIL import Image
import face_recognition
import pickle
import threading

from database.Redis import get_face_data_from_redis
from database.user import User
import asyncio
import websockets
import json


# 人脸识别
async def face_recognitions( frame, websocket,face_count):
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)
    tuple_data=get_face_data_from_redis()
    for face_encoding in face_encodings:
        results = face_recognition.compare_faces(tuple_data[4], face_encoding)
        if True in results:
            index = results.index(True)
            names = tuple_data[1][index]
            id = tuple_data[0][index]
            #解码id并提取数字
            id_str = id.decode('utf-8')  # 将字节串解码为字符串
            id_number_str = id_str.split(':')[1]  # 使用冒号 ':' 分割字符串，并获取第二部分，即数字部分
            id_number = int(id_number_str)  # 将数字字符串转换为整数类型
            phone_number = tuple_data[2][index]
            account = tuple_data[3][index]
            account_str = str(account)

            # print(names)
            # print(id_number)
            # print(phone_number)
            # print(account_str)

            data_dict = {
                "name": names,
                "id": id_number,
                "phone_number": phone_number,
                "account": account_str
            }
            json_string = json.dumps(data_dict)
            if names in face_count:
                face_count[names] += 1
                print(face_count[names])
            else:
                face_count[names] = 1

                # 当某个人脸的计数达到8次时，发送websocket请求到前端服务器
            if face_count[names] >= 4:
                print("发送数据" + str(names))
                await websocket.send(json_string)
                face_count[names] = 0  # 重置该人脸的计数


            for (top, right, bottom, left) in face_locations:
                cv.putText(frame, names, (left, top - 10), cv.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                cv.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        else:
            print("验证失败")

    cv.imshow('Video', frame)

# 新的视频处理函数，每隔几帧处理一次人脸识别
async def process_video(video_capture, websocket):
    frame_interval = 10  # 每10帧处理一次
    frame_count = 0
    face_count={}
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break
        frame_count += 1
        if frame_count % frame_interval == 0:
            await face_recognitions( frame, websocket,face_count)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    video_capture.release()
    cv.destroyAllWindows()

# WebSocket 服务器处理函数
async def handle_client(websocket):
    video_capture = cv.VideoCapture(0)
    await process_video(video_capture, websocket)

# 启动 WebSocket 服务器
async def start_server():
    server = await websockets.serve(handle_client, "localhost", 8087)
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(start_server())