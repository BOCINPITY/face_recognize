from.db import DatabaseConnection
import pymysql
import pickle

class User:
    def __init__(self):
        self.db_conn = DatabaseConnection()

    def register(self, phone, password, encoding, name):
        connection = self.db_conn.connect()
        if connection:
            try:
                cursor = connection.cursor()
                sql = "INSERT INTO users (phone, password, encoding,name) VALUES (%s, %s, %s,%s)"
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
                    user_info = {
                        "id":  result["id"],
                        "phone": result["phone"],
                        "password": result["password"],
                        "account": result["account"],
                        "encoding": pickle.loads(result["encoding"]) if result["encoding"] else None
                    }
                    return user_info
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
                return results
            except pymysql.Error as e:
                print(f"错误,查询所有用户数据失败: {e}")
                return None
        return None