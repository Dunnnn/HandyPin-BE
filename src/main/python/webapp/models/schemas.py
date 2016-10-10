from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema, field_for
from models import *

class UserSchema(ModelSchema):
    class Meta:
        model = User
        exclude = ('search_vector',)

class PinSchema(ModelSchema):
    class Meta:
        model = Pin
        exclude = ('search_vector',)

class VoteSchema(ModelSchema):
    class Meta:
        model = Vote

class CommentSchema(ModelSchema):
    class Meta:
        model = Comment
        exclude = ('search_vector',)


class TagSchema(ModelSchema):
    class Meta:
        model = Tag
        exclude = ('search_vector',)

class PinTagSchema(ModelSchema):
    class Meta:
        model = PinTag



