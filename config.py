

class Config:
    # JWT
    JWT_SECRET = 'TPmi4aLWRbyVq8zu9v82dWYW17/z+UvRnYTt4P6fAXA'
    JWT_EXPIRY_HOURS = 24
    JWT_REFRESH_DAYS = 14

    # Snowflake ID Worker 参数
    DATACENTER_ID = 0
    WORKER_ID = 0
    SEQUENCE = 0

    # flask-sqlalchemy使用的参数
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@127.0.0.1/1909_db'  # 数据库
    SQLALCHEMY_BINDS = {
        'bj-m1': 'mysql+pymysql://root@127.0.0.1:3306/toutiao',
        'bj-s1': 'mysql+pymysql://root@127.0.0.1:3306/toutiao',
        # 'masters': ['bj-m1'],
        # 'slaves': ['bj-m1'],
        'default': 'bj-m1'
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 追踪数据的修改信号
    SQLALCHEMY_ECHO = False