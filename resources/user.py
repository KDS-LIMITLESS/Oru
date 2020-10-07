import traceback

from flask import make_response, render_template
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                fresh_jwt_required, get_jwt_identity,
                                get_raw_jwt, jwt_refresh_token_required,
                                jwt_required, verify_fresh_jwt_in_request,
                                verify_jwt_refresh_token_in_request)
from flask_restful import Resource, request
from marshmallow import ValidationError
from werkzeug.security import safe_str_cmp

from db import db
from models.user import TokenBlacklist, UserModel
from password import psw
from schemas.user import UserSchema
from utils.mailgun import MailgunException


USER_NOT_FOUND = "User not Found!"
USER_DELETED = "User {} has been deleted"
EMAIL_TAKEN = "{} has been taken by another user"
EMAIL_DOES_NOT_EXIST = "{} does not exist in our database"
USER_CREATED = "Account created for {}. check your email for procedures to activate your account."
INTERNAL_SERVER_ERROR = "We are having some issues with our servers at the moment. Please come back later" 
NOT_ACTIVATED = "Account for { has not yet been activated. Click the link sent to your email to activate your account."
INCORRECT_PASSWORD = "Is this your password?"
LOGGED_OUT = "You have been logged out."

user_schema = UserSchema(many=True)


class User(Resource):
 
    @classmethod
    @jwt_refresh_token_required
    def get(cls, name):
        get_user = UserModel.find_user_by_name(name) 
        if not get_user:
            return {'message': USER_NOT_FOUND }, 404
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
        return {"message": USER_NOT_FOUND}, 400
           
    @classmethod
    @fresh_jwt_required
    def delete(cls, name):
        user = UserModel.find_first_user_by_name(name)
        if not user:
            return {"Message": USER_NOT_FOUND }, 400
        user.delete_from_db()
        return {"message": USER_DELETED.format(user.username)},200


class UserRegister(Resource):
    @classmethod
    def post(cls):
        new_user = request.get_json()

        if UserModel.find_user_by_email(new_user['email']):
            return {"message": EMAIL_TAKEN.format(new_user['email'])}, 404
        password = psw.generate_password_hash(new_user['password'])
        user = UserModel(new_user['username'], password ,new_user['email'])

        try:
            user.save_to_db()
            user.send_email()
            return {"Message": USER_CREATED.format(new_user['username'])}, 200

        except MailgunException as e:
            user.delete_from_db()
            return {"message": str(e)}, 500

        except:
            traceback.print_exc()
            user.delete_from_db()
            return {"message": INTERNAL_SERVER_ERROR}, 500
        


class UserLogin(Resource):
    @classmethod
    def post(cls):
        get_user_details = request.get_json()
        get_user_from_db = UserModel.find_user_by_email(get_user_details['email'])

        if not get_user_from_db:
            return {"message": EMAIL_DOES_NOT_EXIST.format(get_user_details['email'])}, 404
        
        if psw.check_password_hash(get_user_from_db.password, get_user_details['password']):
            if get_user_from_db.is_activated:
                access_token = create_access_token(identity=get_user_from_db.email,fresh=True)
                refresh_token = create_refresh_token(get_user_from_db.email)

                return {
                    "Access_Token": access_token,
                    "Refresh_Token": refresh_token
                }, 200

            return {"message": NOT_ACTIVATED.format(get_user_from_db.email)}, 400
        return {"message": INCORRECT_PASSWORD}, 401


class UserLogout(Resource): 
    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = TokenBlacklist(jti = jti)
            revoked_token.add()
            return {"message": LOGGED_OUT}, 200
        except:
            return {"message": INTERNAL_SERVER_ERROR}, 500
        
    
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
            return {"message": USER_NOT_FOUND}, 404
        
        find_user.is_activated = True
        find_user.save_to_db()
        # return redirect("http://localhost:3000/", code=302)  # redirect to separate web app
        headers = {"Content-Type": "text/html"}
        return make_response(
            render_template("confirmation_page.html", email=find_user.email), 200, headers
        )
