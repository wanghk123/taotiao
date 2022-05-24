

from flask import Blueprint
from flask_restful import Api
from . import login
from util.output import output_json

# user_bp = Blueprint('user_bp', __name__)
# user_api = Api(user_bp)

user_bp = Blueprint('user_bp', __name__,)
user_api = Api(user_bp, catch_all_404s=True)
user_api.representation('application/json')(output_json)


user_api.add_resource(login.SendSMS, '/app/v1_0/sms/codes/<string:mobile>')
user_api.add_resource(login.Login, '/app/v1_0/authorizations')
