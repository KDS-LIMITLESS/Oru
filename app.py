from datetime import timedelta
from os import environ
from dotenv import load_dotenv

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import configure_uploads, patch_request_class

from db import db
from models.user import TokenBlacklist, UserModel
from password import psw
from resources.user import (TokenRefresh, User, UserConfirm, UserLogin, DeleteUser,
                            UserLogout, UserRegister, TestConfirmation, UpdateUserUsername,
                            UpdateUserPassword, UpdateUserLocation, UpdateUserEmail)
from resources.image import ImageUpload
from libs.image import IMAGE_SET


app = Flask(__name__)
load_dotenv('.env', verbose=True)
app.config.from_object('default_config')
app.config.from_envvar('APPLICATION_SETTINGS')
jwt = JWTManager(app)

api = Api(app)

patch_request_class(app, 10 * 1024 * 1024)
configure_uploads(app, IMAGE_SET)

@app.before_first_request
def create_tables():
    db.create_all()

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return TokenBlacklist.is_jti_blacklisted(jti)

api.add_resource(User, "/users/<string:name>")
api.add_resource(UpdateUserUsername, "/username")
api.add_resource(UpdateUserPassword, "/password")
api.add_resource(UpdateUserLocation, "/location")
api.add_resource(UpdateUserEmail, "/email")
api.add_resource(DeleteUser, "/delete")
api.add_resource(UserRegister, "/register")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout/access")
api.add_resource(TokenRefresh, "/refresh/access")
api.add_resource(UserConfirm, "/userconfirm", "/userconfirm/<string:confirmation_id>")
api.add_resource(TestConfirmation, "/resendconfirmationtoken/<int:user_id>")
api.add_resource(ImageUpload, "/upload/image")



if __name__ == "__main__":
    db.init_app(app)
    psw.init_app(app)
    app.run(port=5000)
