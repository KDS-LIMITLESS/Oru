import traceback
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    get_jwt_identity, 
    jwt_required, 
    get_raw_jwt,
    jwt_refresh_token_required, 
    fresh_jwt_required, 
    verify_fresh_jwt_in_request, 
    verify_jwt_refresh_token_in_request
)
from flask import make_response, render_template
from flask_restful import Resource, request
from marshmallow import ValidationError
from werkzeug.security import safe_str_cmp

from db import db
from models.user import UserModel, TokenBlacklist
from schemas.user import UserSchema
from password import psw
from utils.mailgun import MailgunException

user_schema = UserSchema(many=True)

class User(Resource):
 
    @classmethod
    @jwt_refresh_token_required
    def get(cls, name):
        get_user = UserModel.find_user_by_name(name) 
        if not get_user:
            return {'Message': "User Not Found"}, 404
        print(user_schema.dump(get_user))
        return user_schema.dump(get_user), 200 
        
    @classmethod
    @fresh_jwt_required
    def put(cls,name):
        find_user = UserModel.find_user_by_name(name)
        if find_user:
            get_user = request.get_json()
            
            find_user[0].username = get_user["username"]
            find_user[0].password = psw.generate_password_hash(get_user["password"])
            find_user[0].email = get_user["email"]

            db.session.commit()
            return user_schema.dump(find_user), 200
        return {"message": "User not found"}, 400
           
    @classmethod
    @fresh_jwt_required
    def delete(cls, name):
        user = UserModel.find_first_user_by_name(name)
        if not user:
            return {"Message": "User Not Found"}, 400
        user.delete_from_db()
        return {"message": "User Deleted!"},200


class UserRegister(Resource):
    @classmethod
    def post(cls):
        new_user = request.get_json()

        if UserModel.find_user_by_email(new_user['email']):
            return {"message": "A User already exists with that email"}, 404
        password = psw.generate_password_hash(new_user['password'])
        user = UserModel(new_user['username'], password ,new_user['email'])

        try:
            user.save_to_db()
            user.send_email()
            return {"Message": f"User {new_user['username']} Created Sucessfully. Check your email for your confirmation token"}, 200

        except MailgunException as e:
            user.delete_from_db()
            return {"message": str(e)}, 500

        except:
            traceback.print_exc()
            user.delete_from_db()
            return {"message": "Internal Server Error"}, 500
        


class UserLogin(Resource):
    @classmethod
    def post(cls):
        get_user_details = request.get_json()
        get_user_from_db = UserModel.find_user_by_email(get_user_details['email'])

        if not get_user_from_db:
            return {"message": f"Invalid Email Address. A user with {get_user_details['email']} does not exist in the database"}, 404
        
        if psw.check_password_hash(get_user_from_db.password, get_user_details['password']):
            if get_user_from_db.is_activated:
                access_token = create_access_token(identity=get_user_from_db.email,fresh=True)
                refresh_token = create_refresh_token(get_user_from_db.email)

                return {
                    "Access_Token": access_token,
                    "Refresh_Token": refresh_token
                }, 200

            return {"message": "Your account has not been activated "}, 400
        return {"message": "Incorrect Password"}, 401


class UserLogout(Resource): 
    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = TokenBlacklist(jti = jti)
            revoked_token.add()
            return {"message": "You have been logged out"}, 200
        except:
            return {"message": "Something went wrong"}, 500
        
    
class TokenRefresh(Resource):
    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200

class UserConfirmation(Resource):

    def get(self, id:int):
        print(id)

        find_user = UserModel.find_user_by_id(id)
        print(find_user.email)

        if not find_user:
            return {"message": "User not found"}, 404
        
        find_user.is_activated = True
        find_user.save_to_db()
        # return redirect("http://localhost:3000/", code=302)  # redirect to separate web app
        headers = {"Content-Type": "text/html"}
        return make_response(
            render_template("confirmation_page.html", email=find_user.email), 200, headers
        )