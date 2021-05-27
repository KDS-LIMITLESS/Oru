import asyncio

import quart.flask_patch
from dotenv import load_dotenv
from quart_jwt_extended import JWTManager
from quart_openapi import Pint

from libs.db import db
from libs.password import psw
from models.users import TokenBlacklist
from resources.user_confirmation import user_confirm
from resources.users import user

app = Pint(__name__)

# Register Blueprints
app.register_blueprint(user)
app.register_blueprint(user_confirm)


load_dotenv('.env', verbose=True)
app.config.from_object('default_config')
app.config.from_envvar('APPLICATION_SETTINGS')
jwt = JWTManager(app)


@app.before_first_request
async def create_tables():
    async with app.app_context():
        db.create_all()


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return TokenBlacklist.is_jti_blacklisted(jti)


if __name__ == "__main__":
    psw.init_app(app)
    db.init_app(app)
    asyncio.create_task(app.run())
