import traceback

from libs.db import db
from libs.mailgun import MailgunException
from libs.password import psw
from libs.phone import Country
from marshmallow import ValidationError
from models.user_confirmation import UserConfirmationModel
from models.users import TokenBlacklist, UserModel
from quart import request
from quart_jwt_extended import (create_access_token, create_refresh_token,
                                fresh_jwt_required, get_jwt_identity,
                                get_raw_jwt, jwt_refresh_token_required)
from quart_openapi import PintBlueprint, Resource
from requests_async.adapters import ConnectionError
from strings.constants import (ACCOUNT_UPDATED, EMAIL_TAKEN, EMAIL_UPDATED,
                               INCORRECT_EMAIL_OR_PASSWORD, LOGGED_OUT,
                               NOT_ACTIVATED, USER_CREATED, USER_DELETED,
                               USER_NOT_FOUND)

from .schema import (EmailSchema, LocationSchema, PasswordSchema,
                     UserLoginSchema, UsernameSchema, UserSchema)

user = PintBlueprint("user", __name__)
user_schema = UserSchema(load_only=('password', 'id',))
login_schema = UserLoginSchema()


@user.route("/users/<name>")
class User(Resource):
    @classmethod
    @jwt_refresh_token_required
    async def get(cls, name):
        get_user = await UserModel.find_user_by_name(name)
        if not get_user:
            return {'message': USER_NOT_FOUND}, 404
        return user_schema.dump(get_user), 200


@user.route('/delete')
class DeleteUser(Resource):
    @classmethod
    @fresh_jwt_required
    def delete(cls):
        user_identity = get_jwt_identity()
        user = UserModel.find_user_by_email(user_identity)
        if not user:
            return {"Message": USER_NOT_FOUND}, 400
        user.delete_from_db()
        return {"message": USER_DELETED.format(user.username)}, 200


@user.route('/updates/username')
class UpdateUserUsername(Resource):
    @fresh_jwt_required
    async def put(self):
        username_schema = UsernameSchema()
        user_identity = get_jwt_identity()
        current_user = UserModel.find_user_by_email(user_identity)

        if current_user:
            user = await request.get_json()
            try:
                get_user = username_schema.load(user)
            except ValidationError as err:
                return err.messages, 404

            current_user.username = get_user["username"]

            db.session.commit()

            return {"message": ACCOUNT_UPDATED}, 200
        return {"message": USER_NOT_FOUND}, 404


@user.route('/updates/email')
class UpdateUserEmail(Resource):
    @fresh_jwt_required
    async def put(self):
        email_schema = EmailSchema()
        user_identity = get_jwt_identity() 
        current_user = UserModel.find_user_by_email(user_identity)

        if current_user:
            user = await request.get_json()
            try:
                get_user = email_schema.load(user)
            except ValidationError as err:
                return err.messages, 404

            try:
                current_user.email = get_user["email"]

                if get_user['email'] == current_user.email or UserModel.find_user_by_email(get_user['email']):
                    return {"message": EMAIL_TAKEN.format(get_user['email'])}, 400

                new_confirmation = UserConfirmationModel(current_user.id)
                new_confirmation.save_to_db()
                current_user.send_email()

                db.session.commit()
                return {"message": EMAIL_UPDATED}, 200

            except (MailgunException, traceback.print_exc()) as err:
                return {'message': str(err)}, 500

        return {"message": USER_NOT_FOUND}, 404


@user.route('/updates/password')
class UpdateUserPassword(Resource):
    @fresh_jwt_required
    async def put(self):
        password_schema = PasswordSchema()
        user_identity = get_jwt_identity() 
        current_user = UserModel.find_user_by_email(user_identity) 

        if current_user:
            user = await request.get_json()
            try:
                get_user = password_schema.load(user)
            except ValidationError as err:
                return err.messages, 404

            current_user.password = psw.generate_password_hash(get_user["password"])

            db.session.commit()

            return {"message": ACCOUNT_UPDATED}, 200
        return {"message": USER_NOT_FOUND}, 404


@user.route('/updates/location')
class UpdateUserLocation(Resource):
    @fresh_jwt_required
    async def put(self):
        location_schema = LocationSchema()
        user_identity = get_jwt_identity() 
        current_user = UserModel.find_user_by_email(user_identity)

        if current_user:
            user = await request.get_json()
            try:
                get_user = location_schema.load(user)
            except ValidationError as err:
                return err.messages, 404

            current_user.country = Country.get_country_name(Country, get_user['country'])
            _ = Country.get_country_region(Country)
            current_user.phone_number = Country.get_user_phonenumber(Country, get_user["phone_number"])
            current_user.state = await Country.get_states(Country, get_user['state'])
            current_user.city = await Country.get_city(Country, get_user['city'])

            db.session.commit()

            return {"message": ACCOUNT_UPDATED}, 200
        return {"message": USER_NOT_FOUND}, 404


@user.route('/register')
class UserRegister(Resource):
    @classmethod
    async def post(cls):
        user_details = await request.get_json()

        try:
            user = user_schema.load(user_details)
        except ValidationError as err:
            return err.messages, 404

        if await UserModel.find_user_by_email(user['email']):
            return {"message": EMAIL_TAKEN.format(user['email'])}, 404

        try:
            c_user = UserModel()
            await c_user.init(**user)
            await c_user.save_to_db()
            confirmation = UserConfirmationModel(c_user.id)
            confirmation.save_to_db()
            await c_user.send_email()
            return {"message": USER_CREATED.format(c_user.username)}, 200

        except(
                MailgunException, UnboundLocalError,
                TypeError, ConnectionError
                ) as e:
            await c_user.delete_from_db()
            return {"message": str(e)}, 500


@user.route('/login')
class UserLogin(Resource):
    @classmethod
    async def post(cls):
        get_user_details = await request.get_json()
        try:
            user = login_schema.load(get_user_details)
        except ValidationError as err:
            return err.messages, 404

        get_user_from_db = await UserModel.find_user_by_email(get_user_details['email'])

        if get_user_from_db and psw.check_password_hash(get_user_from_db.password, user['password']):
            confirmation = get_user_from_db.recent_confirmation
            if confirmation and confirmation.confirmed:
                access_token = create_access_token(identity=get_user_from_db.email,fresh=True)
                refresh_token = create_refresh_token(get_user_from_db.email)

                return {
                    "Access_Token": access_token,
                    "Refresh_Token": refresh_token
                }, 200

            return {"message": NOT_ACTIVATED.format(get_user_from_db.email)}, 404
        return {"message": INCORRECT_EMAIL_OR_PASSWORD}, 400


@user.route('/users/logout')
class UserLogout(Resource):
    @classmethod
    @jwt_refresh_token_required
    async def post(cls):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = TokenBlacklist(jti=jti)
            revoked_token.add()
            return {"message": LOGGED_OUT}, 200
        except (EnvironmentError, ConnectionError) as e:
            return {"message": str(e)}, 500


@user.route('/token/refresh')
class TokenRefresh(Resource):
    @classmethod
    @jwt_refresh_token_required
    async def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
