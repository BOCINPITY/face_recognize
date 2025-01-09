from database.DaoDish import Dish
from database.db import  DatabaseConnection

import pymysql

class DishService:
    def __init__(self):
        self.db_conn = DatabaseConnection()

    def get_dish_by_id(self, dish_id):
        connection = self.db_conn.connect()
        if connection:
            try:
                cursor = connection.cursor(pymysql.cursors.DictCursor)
                sql = "SELECT * FROM dish WHERE id = %s"
                cursor.execute(sql, (dish_id,))
                result = cursor.fetchone()
                cursor.close()
                connection.close()
                if result:
                    dish = Dish(
                        id=result["id"],
                        cname=result["cname"],
                        price=result["price"],
                    )
                    return dish
                return None
            except pymysql.Error as e:
                print(f"错误,查询用户数据失败: {e}")
                return None
        return None