import os
import cv2 as cv
from PIL import Image
import face_recognition
import pickle
import threading
from database.user import User
import pickle

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
            name = user["name"]
            encoding = pickle.loads(user["encoding"])
            name_content.append(name)
            image_encoding_content.append(encoding)
    print(name_content)
    return name_content, image_encoding_content


# 人脸识别
def face_recognitions(data_base_image, frame):
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    for face_encoding in face_encodings:
        results = face_recognition.compare_faces(data_base_image[1], face_encoding)
        if True in results:
            index = results.index(True)
            names = data_base_image[0][index]
            print(f"人脸验证成功,身份是{names}")
            for (top, right, bottom, left) in face_locations:
                cv.putText(frame, names, (left, top - 10), cv.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                cv.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        else:
            print("验证失败")

    cv.imshow('Video', frame)


def stream_delay_test(video_capture):
    if not video_capture.isOpened():
        print("Error opening video stream or file")
    while True:
        ret, frame = video_capture.read()
        if ret:
            cv.imshow('RTMP Stream', frame)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break
    video_capture.release()
    cv.destroyAllWindows()


# 新的视频处理函数，每隔几帧处理一次人脸识别
def process_video(video_capture, tuple_data):
    frame_interval = 10  # 每5帧处理一次
    frame_count = 0
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break
        frame_count += 1
        if frame_count % frame_interval == 0:
            face_recognitions(tuple_data, frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    video_capture.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    video_capture = cv.VideoCapture("rtmp://localhost/live/livestream")
    tuple_data = get_face_data()

    # 使用多线程，一个线程读取视频，一个线程做人脸识别
    video_thread = threading.Thread(target=process_video, args=(video_capture, tuple_data))
    video_thread.start()
    video_thread.join()