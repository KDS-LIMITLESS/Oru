from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, ModelSchema
from models.user import UserModel




#class UserSchema(Schema):
#    id = fields.Integer()
#    username = fields.String(required=True)
#    password = fields.String(required=True)
#    email = fields.Email()

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        load_only = ("password","is_activated","id",)

