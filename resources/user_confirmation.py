import time
import traceback

from libs.mailgun import MailgunException
from models.user_confirmation import UserConfirmationModel
from models.users import UserModel
from quart import make_response, render_template
from quart_openapi import PintBlueprint, Resource
from schema.user_confirmation import UserConfirmationSchema
from strings.constants import (CONFIRMATION_TOKEN_NOT_FOUND, EXPIRED_TOKEN,
                               TOKEN_ALREADY_CONFIRMED, RESEND_SUCCESSFULL,
                               USER_NOT_FOUND, RESEND_FAILED)

user_confirm = PintBlueprint("user_confirm", __name__)


@user_confirm.route("/user_confirm")
@user_confirm.route("/user_confirm/<string:confirmation_id>")
class UserConfirm(Resource):
    async def get(self, confirmation_id: str):

        confirmation = UserConfirmationModel.find_by_id(confirmation_id)

        if not confirmation:
            return{'message': CONFIRMATION_TOKEN_NOT_FOUND}, 404

        if confirmation.token_expires_at < int(time.time()):
            return{'message': EXPIRED_TOKEN}, 400

        if confirmation.confirmed:
            return{'message': TOKEN_ALREADY_CONFIRMED}, 400

        confirmation.confirmed = True
        confirmation.save_to_db()
        headers = {"Content-Type": "text/html"}
        return await make_response(
            await render_template("confirmation_page.html", email=confirmation.user.email), 200, headers
        )


@user_confirm.route("/resendconfirmationtoken/<string:email>")
class TestConfirmation(Resource):    # Test Class
    @classmethod
    async def get(cls, email):
        user = UserModel.find_user_by_email(email)

        if not user:
            return {'message': USER_NOT_FOUND}, 404
        return (
            {
                "Current Time": int(time.time()),
                "confirmation": [
                    UserConfirmationSchema.dump(each)
                    for each in user.confirmed.order_by(UserConfirmationModel.token_expires_at)
                ],
            },
            200,
        )

    @classmethod
    async def post(cls, email):     # Resend_confirmation_token resource
        user = UserModel.find_user_by_email(email)

        if not user:
            return {'message': USER_NOT_FOUND}, 404

        try:
            confirmation = user.recent_confirmation
            if confirmation:
                if confirmation.confirmed:
                    return {"message": TOKEN_ALREADY_CONFIRMED}, 404
                confirmation.force_expire()

            new_confirmation = UserConfirmationModel(user.id)
            new_confirmation.save_to_db()
            await user.send_email()
            print("Done")
            return {"message": RESEND_SUCCESSFULL}, 200

        except MailgunException as e:
            return {"message": str(e)}, 500
        except EnvironmentError:
            traceback.print_exc()
            return{"message": RESEND_FAILED}, 500
