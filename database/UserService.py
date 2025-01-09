from database.DaoUser import User
from database.db import  DatabaseConnection

import pymysql
import pickle

class UserService:
    def __init__(self):
        self.db_conn = DatabaseConnection()

    def register(self, phone, password, encoding, name):
        connection = self.db_conn.connect()
        if connection:
            try:
                cursor = connection.cursor()
                sql = "INSERT INTO users (phone, password, encoding, name) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (phone, password, pickle.dumps(encoding), name))
                connection.commit()
                cursor.close()
                connection.close()

                return True
            except pymysql.Error as e:
                print(f"错误,插入用户数据失败: {e}")
                return False
        return False

    def get_user_by_id(self, user_id):
        connection = self.db_conn.connect()
        if connection:
            try:
                cursor = connection.cursor(pymysql.cursors.DictCursor)
                sql = "SELECT * FROM users WHERE id = %s"
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()
                cursor.close()
                connection.close()
                if result:
                    user = User(
                        id=result["id"],
                        phone=result["phone"],
                        password=result["password"],
                        encoding=pickle.loads(result["encoding"]) if result["encoding"] else None,
                        name=result["name"],
                        account=result["account"]
                    )
                    return user
                return None
            except pymysql.Error as e:
                print(f"错误,查询用户数据失败: {e}")
                return None
        return None

    def get_all_users(self):
        connection = self.db_conn.connect()
        if connection:
            try:
                cursor = connection.cursor(pymysql.cursors.DictCursor)
                sql = "SELECT * FROM users"
                cursor.execute(sql)
                results = cursor.fetchall()
                cursor.close()
                connection.close()
                users = []
                for result in results:
                    user = User(
                        id=result["id"],
                        phone=result["phone"],
                        password=result["password"],
                        encoding=pickle.loads(result["encoding"]) if result["encoding"] else None,
                        name=result["name"],
                        account=result["account"]
                    )
                    users.append(user)
                return users
            except pymysql.Error as e:
                print(f"错误,查询所有用户数据失败: {e}")
                # 可以在这里返回一个空列表，而不是None
                return []
        else:
            print("数据库连接失败")
            return []