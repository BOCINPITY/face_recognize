import numpy as np
import redis
from UserService import UserService  # 使用绝对导入

def cache_use_redis():
    # 创建Redis客户端连接
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
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
            'phone': user.phone,
            'password': user.password,
            'name': user.name
        }
        if isinstance(user.encoding, np.ndarray):
            user_data['encoding'] = user.encoding.tobytes()
        else:
            user_data['encoding'] = user.encoding
        # 使用管道中的HSET存储用户信息
        for field, value in user_data.items():
            pipeline.hset(f'users:{user_id}', field, value)

    # 执行管道中的所有命令
    pipeline.execute()

    #

    print("用户数据已成功存储到Redis中")

if __name__ == "__main__":
    cache_use_redis()