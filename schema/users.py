from marshmallow import validate, Schema, fields


class UserSchema(Schema):
    id = fields.Integer()
    username = fields.String(required=True, validate=validate.Length(
        min=4, max=16
    ))
    password = fields.String(required=True, validate=validate.Length(
        min=8, max=16
    ))
    email = fields.Email(required=True)
    country = fields.String(required=True)
    phone_number = fields.String(required=True)
    state = fields.String(required=True)
    city = fields.String(required=True)


class UserLoginSchema(Schema):
    password = fields.String(required=True, validate=validate.Length(
        min=8, max=16
    ))
    email = fields.Email(required=True)


class UsernameSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(
        min=4, max=16
    ))


class EmailSchema(Schema):
    email = fields.Email(required=True)


class PasswordSchema(Schema):
    password = fields.String(required=True, validate=validate.Length(
        min=8, max=16
    ))


class LocationSchema(Schema):
    country = fields.String(required=True)
    phone_number = fields.String(required=True)
    state = fields.String(required=True)
    city = fields.String(required=True)
