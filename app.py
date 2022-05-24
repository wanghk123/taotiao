import os
from flask import Flask
from resources.user import user_bp
from config import Config
from util.middlewares import jwt_authentication
from util.snowflake.id_worker import IdWorker

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.register_blueprint(user_bp)
app.config.from_object(Config)
app.before_request(jwt_authentication)

# 创建Snowflake ID worker
app.id_worker = IdWorker(app.config['DATACENTER_ID'],
                         app.config['WORKER_ID'],
                         app.config['SEQUENCE'])

# MySQL数据库连接初始化
from models import db

db.init_app(app)


@app.route('/')
def index():
    return 'ok'


if __name__ == '__main__':
    app.run()

