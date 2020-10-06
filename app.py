from datetime import timedelta
from flask import Flask
from flask_restful import Api
from db import db
from password import psw
from flask_jwt_extended import JWTManager
from resources.user import User, UserRegister, UserLogin, UserLogout,TokenRefresh, UserConfirmation
from flask_sqlalchemy import SQLAlchemy
from os import environ
from models.user import TokenBlacklist,UserModel


app = Flask(__name__)
jwt = JWTManager(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = environ.get("JWT_SECRET_KEY")
app.config['JWT_ERROR_MESSAGE_KEY'] = "Error"
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=1)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=1)

SECRET_KEY = environ.get("FLASK_SECRET_KEY")

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
api.add_resource(UserConfirmation, "/userconfirm")




if __name__ == "__main__":
    db.init_app(app)
    psw.init_app(app)
    app.run(port=5000, debug=True)

