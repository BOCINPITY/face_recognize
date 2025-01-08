import os
import cv2 as cv
from PIL import Image
import face_recognition
import pickle
import threading
from database.user import User
import asyncio
import websockets
import json
from decimal import Decimal


# 将目录中的图片加载到已知人脸库中
def get_face_data():
    user = User()
    all_users = user.get_all_users()  # 假设这个方法获取所有用户记录
    name_content = []
    image_encoding_content = []
    id_content = []
    phone_content = []
    account_content = []
    if all_users:
        for user in all_users:
            id=user["id"]
            phone=user["phone"]
            name = user["name"]
            account=user["account"]
            encoding = pickle.loads(user["encoding"])
            name_content.append(name)
            image_encoding_content.append(encoding)
            id_content.append(id)
            phone_content.append(phone)
            account_content.append(account)

    # print(name_content)
    return name_content, image_encoding_content, id_content, phone_content, account_content

# 人脸识别
async def face_recognitions(data_base_image, frame, websocket,face_count):
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    for face_encoding in face_encodings:
        results = face_recognition.compare_faces(data_base_image[1], face_encoding)
        if True in results:
            index = results.index(True)
            names = data_base_image[0][index]
            id = data_base_image[2][index]
            phone_number = data_base_image[3][index]
            account = data_base_image[4][index]
            account_str = str(account)
            data_dict = {
                "name": names,
                "id": id,
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
async def process_video(video_capture, tuple_data, websocket):
    frame_interval = 10  # 每10帧处理一次
    frame_count = 0
    face_count={}
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break
        frame_count += 1
        if frame_count % frame_interval == 0:
            await face_recognitions(tuple_data, frame, websocket,face_count)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    video_capture.release()
    cv.destroyAllWindows()

# WebSocket 服务器处理函数
async def handle_client(websocket, path):
    video_capture = cv.VideoCapture(0)
    tuple_data = get_face_data()
    await process_video(video_capture, tuple_data, websocket)

# 启动 WebSocket 服务器
async def start_server():
    server = await websockets.serve(handle_client, "localhost", 8087)
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(start_server())