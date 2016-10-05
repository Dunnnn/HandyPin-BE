from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema, field_for
from models import *

class UserSchema(ModelSchema):
    contacts = fields.Nested('UserSchema', only=('id'), many=True)
    class Meta:
        model = User
        exclude = ('search_vector',)

class PinSchema(ModelSchema):
    reviews = fields.Nested('PinSchema', many=True, exclude=('pin',))
    class Meta:
        model = Pin
        exclude = ('search_vector',)

class VoteSchema(ModelSchema):
    user = fields.Nested(UserSchema, only=('id', 'username', 'email'))
    class Meta:
        model = Vote

class CommentSchema(ModelSchema):
    user = fields.Nested(UserSchema, only=('id', 'username', 'email'))
    class Meta:
        model = Comment
        exclude = ('search_vector',)


class TagSchema(ModelSchema):
    tag = fields.Nested('TagSchema', only=('id'), many=True)
    class Meta:
        model = Tag
        exclude = ('search_vector',)

class PinTagSchema(ModelSchema):
    pin = fields.Nested(TagSchema, only=('id'))
    class Meta:
        model = PinTag



