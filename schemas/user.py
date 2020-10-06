from marshmallow import Schema, fields
from models.user import UserModel

from marshmallow_sqlalchemy import SQLAlchemySchema,SQLAlchemyAutoSchema,auto_field



#class UserSchema(Schema):
#    id = fields.Integer()
#    username = fields.String(required=True)
#    password = fields.String(required=True)
#    email = fields.Email()

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        load_only = ("password","is_activated","id",)
    id = fields.Integer()
    username = fields.String(required=True,)
    password = fields.String(required=True)
    email = fields.Email(required=True)
