from flask import request, url_for
import requests
from db import db
from password import psw
from models.user_confirm import UserConfirmationModel
from utils.mailgun import Mailgun



class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key= True)
    username = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(256), nullable=False, unique=True)

    confirmed = db.relationship(
        "UserConfirmationModel", lazy="dynamic", cascade="all, delete-orphan"
    )

    def __init__(self, username, password, email):

        self.username = username
        self.password = password 
        self.email = email

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
        return cls.query.filter(cls.username == name).all()

    
    @classmethod
    def find_first_user_by_name(cls, name):
        return cls.query.filter(cls.username == name).first()
    
    def hash_password(self):
        return psw.generate_password_hash(self.password)
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def send_email(self):
        subject = "Registration Confirmation"
        link = request.url_root[:-1] + url_for("userconfirm") + "/" + str(self.recent_confirmation.confirmation_id)
        text = f"Please click the link to confirm your registration:{link}"
        html = f"<html>Click the link to confirm your registration:<a href={link}>Confirmation Token</a></html>"
        return Mailgun.send_email([self.email], subject, text, html)



    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
       return f"{self.id, self.username, self.email, self.password}"


class TokenBlacklist(db.Model):
    __tablename__ = 'blacklist'
    id = db.Column(db.Integer, primary_key = True)
    jti = db.Column(db.String(120))

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)    
    

    

