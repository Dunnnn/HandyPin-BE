from sqlalchemy import func
from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema, ModelConverter, field_for
from geoalchemy2 import Geometry
from models import *

class GeoConverter(ModelConverter):
    SQLA_TYPE_MAPPING = ModelConverter.SQLA_TYPE_MAPPING.copy()
    SQLA_TYPE_MAPPING.update({
        Geometry: fields.Str
    })

class GeographySerializationField(fields.String):
    def _serialize(self, value, attr, obj):
        if value is None:
            return value
        else:
            if attr == 'geo':
                return {'lng': db.session.scalar(func.ST_X(value)), 'lat': db.session.scalar(func.ST_Y(value)), 'longitude': db.session.scalar(func.ST_X(value)), 'latitude': db.session.scalar(func.ST_Y(value))}
            else:
                return None

    def _deserialize(self, value, attr, data):
        """Deserialize value. Concrete :class:`Field` classes should implement this method.

        :param value: The value to be deserialized.
        :param str attr: The attribute/key in `data` to be deserialized.
        :param dict data: The raw input data passed to the `Schema.load`.
        :raise ValidationError: In case of formatting or validation failure.
        :return: The deserialized value.

        .. versionchanged:: 2.0.0
            Added ``attr`` and ``data`` parameters.
        """
        if value is None:
            return value
        else:
            if attr == 'geo':
                return WKTGeographyElement('POINT({0} {1})'.format(str(value.get('longitude')), str(value.get('latitude'))))
            else:
                return None

class UserSchema(ModelSchema):
    profile_photo = fields.Nested('FileSchema')
    class Meta:
        model = User
        exclude = ('search_vector',)

class PinSchema(ModelSchema):
    owner = fields.Nested('UserSchema', exclude=("password",))
    geo = GeographySerializationField(attribute='geo')
    comments = fields.Nested('CommentSchema', many=True)
    pin_photo = fields.Nested('FileSchema')
    vote_score = fields.Integer()
    pin_tags = fields.Nested('PinTagSchema', many=True)
    vote_by_current_user = fields.Nested('VoteSchema', only=('id', 'vote'))
    class Meta:
        model = Pin
        sqla_session = db.session
        model_converter = GeoConverter
        exclude = ('search_vector',)

class VoteSchema(ModelSchema):
    class Meta:
        model = Vote

class CommentSchema(ModelSchema):
    owner = fields.Nested('UserSchema', only=('id', 'username', 'nickname', 'profile_photo'))
    class Meta:
        model = Comment
        exclude = ('search_vector',)

class TagSchema(ModelSchema):
    class Meta:
        model = Tag
        exclude = ('search_vector',)

class PinTagSchema(ModelSchema):
    tag = fields.Nested('TagSchema')
    class Meta:
        model = PinTag

class FileSchema(ModelSchema):
    class Meta:
        model = File
