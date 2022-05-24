from configparser import ConfigParser

from flask_restful import Resource
from flask import current_app
from flask_restful.reqparse import RequestParser
from celery_tasks.sms.tasks import send_message
from datetime import datetime, timedelta
from util.jwt_util import generate_jwt
from util import parser
from redis import Redis
from models import db
from models.user import User, UserProfile



class SendSMS(Resource):
    def get(self, mobile):
        exp_time = 5 * 60

        try:
            parser.mobile(mobile_str=mobile)
        except ValueError:
            return {'message': 'mobile is not a valid mobile'}, 404

        mobile_code = f'sms_mobile_{mobile}'
        flag_mobile = f'sms_flag_{mobile}'
        redis_conn = Redis(host='127.0.0.1', port=6379, db=0)
        flag = redis_conn.get(flag_mobile)
        if flag:
            return {'message': 'cannot be sent frequently'}, 429
        code = SendSMS.my_code()
        pl = redis_conn.pipeline()
        pl.setex(name=mobile_code, value=code, time=exp_time)
        pl.setex(name=flag_mobile, value=1, time=exp_time)
        pl.execute()
        ret = send_message.delay(mobile=mobile, code=code, time=exp_time)
        if ret:
            return {'message': 'ok', 'mobile': mobile}, 200
        return {'message': 'not ok', 'mobile': mobile}, 429

    @staticmethod
    def my_code():
        import random
        import string
        return ''.join(random.choices(string.digits, k=6))



class Login(Resource):
    def _generate_token(self, user_id, refresh=True):
        """生成token以及refresh_token"""
        payload = {
            'user_id': user_id,
            'refresh': refresh
        }
        expiry = datetime.utcnow() + \
                 timedelta(hours=current_app.config['JWT_EXPIRY_HOURS'])
        print(expiry)
        token = generate_jwt(payload, expiry)

        if refresh:
            expiry = datetime.utcnow() + \
                     timedelta(days=current_app.config['JWT_REFRESH_DAYS'])
            refresh_token = generate_jwt(payload, expiry)
        else:
            refresh_token = None
        return token, refresh_token

    def post(self):
        json_parser = RequestParser()
        json_parser.add_argument('mobile', required=True, location='json',
                                 type=parser.mobile)
        json_parser.add_argument('code', required=True, location='json',
                                 type=parser.code)
        args = json_parser.parse_args()  # args 是一个字典   上述参数合法的话  会存入到字典中
        mobile = args.get('mobile')
        code = args.get('code')

        mobile_code = f'sms_mobile_{mobile}'
        flag_mobile = f'sms_flag_{mobile}'
        redis_conn = Redis(host='127.0.0.1', port=6379, db=0)
        mobile_cod = redis_conn.get(mobile_code)
        # if code != mobile_cod.decode() if mobile_cod else 0:
        #     return {'message': 'code is invalid'}, 400

        user = User.query.filter_by(mobile=mobile).first()
        if not user:
            # 用户不存在，注册用户
            # 采用雪花算法生成分布式id
            # 其他会用到雪花算法生成id的地方：文章id 评论id
            # 这三个id在代码中直接操作数据库使用，所以要全局唯一，使用雪花算法生成
            user_id = current_app.id_worker.get_id()
            user = User(id=user_id, mobile=mobile, name=mobile, last_login=datetime.now())
            db.session.add(user)
            profile = UserProfile(id=user.id)
            db.session.add(profile)
            db.session.commit()
        else:
            if user.status == User.STATUS.DISABLE:
                return {'message': 'Invalid user.'}, 403
        token, refresh_token = self._generate_token(user.id)  # 生成token
        return {'token': token, 'refresh_token': refresh_token}, 201



