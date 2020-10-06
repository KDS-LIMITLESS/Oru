from flask import request, url_for
import requests
from db import db
from password import psw
from utils.mailgun import Mailgun



class UserModel(db.Model):
    __tablename__ = "User"

    id = db.Column(db.Integer, primary_key= True)
    username = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(256), nullable=False, unique=True)
    is_activated = db.Column(db.Boolean, default=False, nullable=True)

    def __init__(self, username, password, email):

        self.username = username
        self.password = password 
        self.email = email

    
    @classmethod
    def find_user_by_id(cls, id):
        return cls.query.filter_by(id=id).first()


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
    
    def send_email(self, email):
        subject = "Registration Confirmation"
        link = request.url_root[:-1] + url_for("userconfirmation", user_id=self.id)
        text = f"Please click the link to confirm your registration: {link}"
        html = f"<html>Please click the link to confirm your registration: <a href={link}>link</a></html>"
        return Mailgun.send_email([email], subject, text, html)



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
    

    

