
import cv2
import time
import face_recognition
from database.Redis import get_face_data_from_redis
import asyncio
import websockets
import json


class DishDetector:
    def __init__(self):
        # 设置合适的推理参数，和训练时尽量匹配
        self.cap = cv2.VideoCapture(0)
        self.send=False

    async def detection_loop(self):
        frame_interval = 5  # 每10帧处理一次
        frame_count = 0
        face_count = {}
        result_set=""
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("无法获取摄像头画面，可能摄像头已断开连接。")
                break
            frame_count += 1
            if frame_count % frame_interval == 0:
                face_locations = face_recognition.face_locations(frame)
                face_encodings = face_recognition.face_encodings(frame, face_locations)
                tuple_data = get_face_data_from_redis()
                for face_encoding in face_encodings:
                    results = face_recognition.compare_faces(tuple_data[4], face_encoding)
                    if True in results:
                        index = results.index(True)
                        names = tuple_data[1][index]
                        id = tuple_data[0][index]
                        # 解码id并提取数字
                        id_str = id.decode('utf-8')  # 将字节串解码为字符串
                        id_number_str = id_str.split(':')[1]  # 使用冒号 ':' 分割字符串，并获取第二部分，即数字部分
                        id_number = int(id_number_str)  # 将数字字符串转换为整数类型
                        phone_number = tuple_data[2][index]
                        account = tuple_data[3][index]
                        account_str = str(account)
                        data_dict = {"name": names,"id": id_number,"phone_number": phone_number,"account": account_str}
                        json_string =data_dict # json.dumps(data_dict)
                        if names in face_count:
                            face_count[names] += 1
                        else:
                            face_count[names] = 1
                        print(face_count[names])
                            # 当某个人脸的计数达到8次时，发送websocket请求到前端服务器
                        if face_count[names] >= 8:
                            self.send=True
                            result_set = json_string
                            # print("发送数据" + str(result_set))
                            face_count[names] = 0  # 重置该人脸的计数
                        for (top, right, bottom, left) in face_locations:
                            cv2.putText(frame, names, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    else:
                            print("验证失败")
                cv2.imshow('Video', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # result_set="dgfd"
            yield result_set
            await asyncio.sleep(0.01)

    async def handle_receive(self, websocket):
        try:
            peer_info = websocket.remote_address
            print(f"客户端 {peer_info} 已连接")
            try:
                while True:
                    client_message = await websocket.recv()
                    print(f"Received from client {peer_info}: {client_message}")
            except websockets.exceptions.ConnectionClosed:
                print(f"客户端 {peer_info} 已断开连接")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error receiving client message: {e}")
        finally:
            await websocket.close()

    async def send_data(self, websocket):
        receive_task = asyncio.create_task(self.handle_receive(websocket))
        try:
            async for result_set in self.detection_loop():
                data_to_send = json.dumps(result_set)

                if self.send:
                    self.send = False
                    print(data_to_send)
                    await websocket.send(data_to_send)

        except Exception as e:
            print(f"WebSocket 数据发送异常: {e}")
        finally:
            receive_task.cancel()
            await websocket.close()

    def run(self):
        try:
            start_server = websockets.serve(self.send_data, "localhost", 8765)
            asyncio.get_event_loop().run_until_complete(start_server)
            asyncio.get_event_loop().run_forever()
        except Exception as e:
            print(f"程序运行出现异常: {e}")
        finally:
            cv2.destroyAllWindows()
            self.cap.release()
            # self.dishes.close()


if __name__ == "__main__":
    detector = DishDetector()
    detector.run()