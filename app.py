import asyncio

import quart.flask_patch
from dotenv import load_dotenv
from flask_uploads import configure_uploads, patch_request_class
from quart_jwt_extended import JWTManager
from quart_openapi import Pint

from images import images
from libs.db import db
from libs.image import IMAGE_SET
from libs.password import psw
from models.users import TokenBlacklist
from user_confirmation.resources import user_confirm
from users.resources import user

app = Pint(__name__)

# Register Blueprints
app.register_blueprint(user)
app.register_blueprint(user_confirm)
app.register_blueprint(images)


@app.before_first_request
async def create_tables():
    async with app.app_context():
        db.create_all()


load_dotenv('.env', verbose=True)
app.config.from_object('default_config')
app.config.from_envvar('APPLICATION_SETTINGS')
jwt = JWTManager(app)

patch_request_class(app, 10 * 1024 * 1024)
configure_uploads(app, IMAGE_SET)


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return TokenBlacklist.is_jti_blacklisted(jti)


if __name__ == "__main__":
    psw.init_app(app)
    db.init_app(app)
    asyncio.create_task(app.run())
