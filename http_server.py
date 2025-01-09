from flask import Flask, request, jsonify

from database.Redis import cache_use_redis
from database.UserService import UserService
from database.DaoUser import User
import face_recognition
app = Flask(__name__)

@app.route('/api/register', methods=['POST'])
def register():
    # 获取表单数据
    phone = request.form.get('phone')
    password = request.form.get('password')
    name = request.form.get('name')

    # 检查必填字段是否存在
    if not phone or not password:
        return jsonify({"message": "phone and password are required"}), 400

    # 获取上传的照片
    photo = request.files.get('photo')
    if photo is None:
        return jsonify({"message": "Photo is required"}), 400
    # 这里就不存储照片了，减少IO
    # 获取人脸编码
    load = face_recognition.load_image_file(photo)
    encodings = face_recognition.face_encodings(load)[0]
    # 将用户信息存入数据库
    serviceUser= UserService()
    if serviceUser.register(phone, password,encodings,name):
        cache_use_redis()
        return jsonify({"message": "Registration successful"}), 200
    else:
        return jsonify({"message": "Registration failed"}), 500

@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    service = UserService()
    result = service.get_user_by_id(user_id)
    if result:
        del result["encoding"]  # 不返回密码
        del result["password"]  
        return jsonify(result), 200
    return jsonify({"message": "User not found"}), 404


@app.route('/')
def index():

    return 'api list:\
        <ul>\
            <li>/api/register   用户注册接口</li>\
            <li>/api/user/:id   获取指定用户信息接口</li>\
        </ul>'




if __name__ == '__main__':
    app.run(debug=True)