import pymysql
from configparser import ConfigParser, NoOptionError, NoSectionError
import os


class DatabaseConfig:
    def __init__(self):
        self.config = ConfigParser()
        try:
            self.config.read(os.path.join(os.getcwd(), 'config.ini'))
        except FileNotFoundError as e:
            print(f"配置文件未找到: {e}")

    def get_config(self):
        try:
            host = self.config.get('database', 'host')
            port = int(self.config.get('database', 'port'))
            user = self.config.get('database', 'user')
            password = self.config.get('database', 'password')
            database = self.config.get('database', 'database')
            return host, port, user, password, database
        except (NoOptionError, NoSectionError) as e:
            print(f"错误,获取配置失败: {e}")
            return None


class DatabaseConnection:
    def __init__(self):
        self.config = DatabaseConfig()
        self.conn = None

    def connect(self):
        db_config = self.config.get_config()
        if db_config:
            try:
                host, port, user, password, database = db_config
                self.conn = pymysql.connect(
                    host=host,
                    user=user,
                    password=password,
                    database=database,
                    port=port
                )
                return self.conn
            except pymysql.Error as e:
                print(f"错误,数据库连接失败: {e}")
                return None
        return None
