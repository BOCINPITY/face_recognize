from decimal import Decimal
from database.DaoUser import User
from flask import Flask, request, jsonify, json
from database.DishService import DishService
from database.Redis import cache_use_redis
from database.UserService import UserService
import face_recognition
app = Flask(__name__)


@app.route('/api/fish/<int:fish_id>', methods=['GET'])
def get_fish(fish_id):
    service = DishService()
    dish = service.get_dish_by_id(fish_id)

    if dish:
        # 假设 dish 是一个 Dish 类的实例
        dish_dict = {
            'id': dish.id,
            'cname': dish.cname,
            'price': str(dish.price)  # 将 decimal 转换为字符串
            # 添加其他需要的字段
        }
        return jsonify(dish_dict), 200

    return jsonify({"message": "Dish not found"}), 404

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

#用户支付接口
from flask import Flask, request, jsonify

app = Flask(__name__)


from decimal import Decimal

@app.route("/api/orderPay", methods=['POST'])
def order_pay():
    # 检查请求中是否有 JSON 数据
    total_price = Decimal(0)  # 初始化为 Decimal 类型
    if request.is_json:
        # 获取 JSON 数据
        data = request.get_json()
        userId = data.get('userId')
        dishList = data.get('dishList', [])
        for item in dishList:
            price = Decimal(item.get('price'))  # 转换为 Decimal
            num = item.get('num')
            total_price += price * num
        total_price = round(total_price, 2)
        service = UserService()
        user = service.get_user_by_id(userId)
        print(user)
        if total_price > user.account:
            return jsonify({"message": "余额不足", "account": float(user.account)}), 200
        else:
            current_account = user.account - total_price
            user.account = current_account
            service.update_user_account(userId, current_account)
            response_data = {
                "phone": user.phone,
                "orderId": "",
                "orderdetails": [
                    {
                        "dishName": "西餐",
                        "num": item.get('num'),
                        "price": item.get('price'),
                        "payStatus": True
                    } for item in dishList
                ],
                "payStatus": True
            }
            return jsonify(response_data), 200
    else:
        # 如果请求体不是 JSON 格式，返回错误
        return jsonify({"error": "Request body must be JSON"}), 400

if __name__ == "__main__":
    app.run(debug=True)

@app.route('/')
def index():

    return 'api list:\
        <ul>\
            <li>/api/register   用户注册接口</li>\
            <li>/api/user/:id   获取指定用户信息接口</li>\
        </ul>'




if __name__ == '__main__':
    app.run(debug=True)