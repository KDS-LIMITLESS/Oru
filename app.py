from datetime import timedelta
from os import environ

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from db import db
from models.user import TokenBlacklist, UserModel
from password import psw
from resources.user import (TokenRefresh, User, UserConfirm, UserLogin,
                            UserLogout, UserRegister, TestConfirmation)

app = Flask(__name__)
CORS(app)
jwt = JWTManager(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = environ.get("JWT_SECRET_KEY")
app.config['JWT_ERROR_MESSAGE_KEY'] = "Error"
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=1)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=5)

#SECRET_KEY = environ.get("FLASK_SECRET_KEY")

api = Api(app)
#flask_bcrypt = Bcrypt(app)


@app.before_first_request
def create_tables():
    db.create_all()

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return TokenBlacklist.is_jti_blacklisted(jti)

api.add_resource(User, "/users/<string:name>")
api.add_resource(UserRegister, "/register")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout/access")
api.add_resource(TokenRefresh, "/refresh/access")
api.add_resource(UserConfirm, "/userconfirm", "/userconfirm/<string:confirmation_id>")
api.add_resource(TestConfirmation, "/resendconfirmationtoken/<int:user_id>")




if __name__ == "__main__":
    db.init_app(app)
    psw.init_app(app)
    app.run(port=5000, debug=True)
