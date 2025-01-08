import os
import cv2 as cv
from PIL import Image
import face_recognition
import pickle
import threading
from database.user import User
import asyncio
import websockets

# 将识别到的人脸绘制出来
def print_image(face, image):
    for face_location in face:
        top, right, bottom, left = face_location
        face_image = image[top:bottom, left:right]
        pil_image = Image.fromarray(face_image)
        pil_image.show()

def print_image_tru(images, image_list):
    image = cv.imread(images)
    for one in image_list:
        y1 = one[0]
        x1 = one[3]
        y2 = one[2]
        x2 = one[1]
        cv.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
    cv.imshow("fff", image)
    cv.waitKey()

# 加载缓存的人脸数据特征值
def load_face_data_cache():
    cache_file = 'face_data_cache.pkl'
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            data = pickle.load(f)
        return data
    return None

# 保存人脸数据特征值到缓存
def save_face_data_cache(data):
    cache_file = 'face_data_cache.pkl'
    with open(cache_file, 'wb') as f:
        pickle.dump(data, f)

# 将目录中的图片加载到已知人脸库中
def get_face_data():
    user = User()
    all_users = user.get_all_users()  # 假设这个方法获取所有用户记录
    name_content = []
    image_encoding_content = []
    if all_users:
        for user in all_users:
            id=user["id"]
            name = user["name"]
            encoding = pickle.loads(user["encoding"])
            name_content.append(name)
            image_encoding_content.append(encoding)
    print(name_content)
    return name_content, image_encoding_content

# 人脸识别
async def face_recognitions(data_base_image, frame, websocket,face_count):
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    for face_encoding in face_encodings:
        results = face_recognition.compare_faces(data_base_image[1], face_encoding)
        if True in results:
            index = results.index(True)
            names = data_base_image[0][index]
            if names in face_count:
                face_count[names] += 1
                print(face_count[names])
            else:
                face_count[names] = 1

                # 当某个人脸的计数达到8次时，发送websocket请求到前端服务器
            if face_count[names] >= 8:
                print("发送数据" + str(names))
                await websocket.send(str(names))
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