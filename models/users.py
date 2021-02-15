from quart import request, url_for

from libs.db import db
from models.user_confirmation import UserConfirmationModel
from libs.mailgun import Mailgun
from libs.phone import Country
from libs.password import psw


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(256), nullable=False, unique=True)

    country = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(30), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)

    confirmed = db.relationship(
        "UserConfirmationModel", lazy="dynamic", cascade="all, delete-orphan"
    )

    def __init__(self, username, password, email, country: str, phone_number, state, city, *args):
        self.username = username
        self.password = psw.generate_password_hash(password).decode('utf8')
        self.email = email
        self.country = Country.get_country_name(Country, country)
        self.region = Country.get_country_region(Country)
        self.phone_number = Country.get_user_phonenumber(Country, phone_number)
        self.state = Country.get_states(Country, state)
        self.city = Country.get_city(Country, city)

    @property
    def recent_confirmation(self) -> "UserConfirmationModel":
        return self.confirmed.order_by(db.desc(UserConfirmationModel.token_expires_at)).first()

    @classmethod
    def find_user_by_id(cls, id) -> "UserModel":
        return cls.query.filter(cls.id == id).first()

    @classmethod
    def find_user_by_email(cls, email):
        return cls.query.filter(cls.email == email).first()

    @classmethod
    def find_user_by_name(cls, name):
        return cls.query.filter(cls.username == name).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    async def send_email(self):
        subject = "Registration Confirmation"
        link = request.url_root[:-1] + url_for("user_confirm.user_confirm") + "/" + str(self.recent_confirmation.confirmation_id)
        text = f"Please click the link to confirm your registration:{link}"
        html = f"<html>Click the link to confirm your registration:<a href={link}>Confirmation Token</a></html>"
        return await Mailgun.send_email([self.email], subject, text, html), "Done Here"

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f"{self.id, self.username, self.email, self.password}"


class TokenBlacklist(db.Model):
    __tablename__ = 'blacklist'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120))

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)
