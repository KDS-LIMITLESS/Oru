
from uuid import uuid4
from db import db

import time

# Q. What type of data does Models return......
# Ans: objects of the class

EXPIRATION_TIME = 1200


class UserConfirmationModel(db.Model):
    __tablename__ = "confirm_user"

    confirmation_id = db.Column(db.String(50), primary_key=True)
    confirmed = db.Column(db.Boolean, nullable=False)
    token_expires_at = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("UserModel")

    def __init__(self, user_id:int, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.confirmation_id = uuid4().hex
        self.confirmed = False
        self.token_expires_at = int(time.time()) + EXPIRATION_TIME

    @classmethod
    def find_by_id(cls, _id:str) -> "UserConfirmationModel":
        return cls.query.filter_by(confirmation_id = _id).first()

    def force_expire(self) -> None:
        if self.token_expires_at > int(time.time()):
            self.token_expires_at = int(time.time()) # check well here
            self.save_to_db()
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    




# Do not use brackets when the function you are calling isn't modifiying things