import numpy as np
import redis
from .UserService import UserService #相对导入

# 连接Redis
def conRedis():
    # 注意这里将decode_responses设置为False
    redis_client = redis.Redis(host='localhost', port=6380, db=0, decode_responses=False)
    return redis_client

def cache_use_redis():
    # 创建Redis客户端连接
    redis_client = conRedis()
    user_service = UserService()
    # 获取所有用户数据
    users = user_service.get_all_users()
    # 创建Redis管道
    pipeline = redis_client.pipeline()
    # 清空Redis中的users键（如果存在）
    pipeline.delete('users')
    # 将用户数据存储到Redis中
    for user in users:
        user_id = user.id  # 假设用户对象有一个id属性
        user_data = {
            'phone': user.phone.encode('utf-8'),  # 转换为字节串
            'password': user.password.encode('utf-8'),  # 转换为字节串
            'name': user.name.encode('utf-8'),  # 转换为字节串
            'account': str(user.account).encode('utf-8')  # 将decimal转换为字符串并编码为字节串
        }
        if isinstance(user.encoding, np.ndarray):
            user_data['encoding'] = user.encoding.tobytes()
        else:
            user_data['encoding'] = user.encoding
        # 使用管道中的HSET存储用户信息
        for field, value in user_data.items():
            pipeline.hset(f'users:{user_id}'.encode('utf-8'), field.encode('utf-8'), value)
    # 执行管道中的所有命令
    pipeline.execute()

# 获取Redis中的所有人脸特征
def get_face_data_from_redis():
    # 创建Redis客户端连接
    redis_client = conRedis()

    # 获取所有用户ID
    user_ids = redis_client.keys('users:*')
    image_encoding_content = []
    ids=[]
    names=[]
    phones=[]
    accounts=[]

    for user_id in user_ids:
        # 获取用户信息
        ids.append(user_id)
        user_info = redis_client.hgetall(user_id)
        # 从Redis中获取encoding数据
        encoding_bytes = user_info.get(b'encoding')  # 注意这里使用字节串作为键
        # 将bytes数据还原为numpy数组
        if encoding_bytes:
            encoding_array = np.frombuffer(encoding_bytes, dtype=np.float64)
            image_encoding_content.append(encoding_array)
        ids.append(user_id.decode('utf-8'))  # 将字节串解码为字符串
        names.append(user_info.get(b'name').decode('utf-8'))
        phones.append(user_info.get(b'phone').decode('utf-8'))
        accounts.append(user_info.get(b'account').decode('utf-8'))
    return ids, names, phones, accounts, image_encoding_content

if __name__ == "__main__":
    cache_use_redis()
    ids, names, phones, accounts, encodings = get_face_data_from_redis()
    print("IDs:", ids)
    print("Names:", names)
    print("Phones:", phones)
    print("Accounts:", accounts)
    print("Encodings:", encodings)