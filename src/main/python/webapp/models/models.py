from flask import Flask
from flask_sqlalchemy import SQLAlchemy, BaseQuery
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy_searchable import make_searchable, SearchQueryMixin
from sqlalchemy_utils.types import TSVectorType
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from geoalchemy2 import Geometry

import datetime
from .. import app

#TODO Hard coded here for now, will be placed somewhere else in the future
db = SQLAlchemy(app)

make_searchable(options={'regconfig': 'pg_catalog.simple'})

#Query classes for full text searching
class UserQuery(BaseQuery, SearchQueryMixin):
    pass

#Class to add, update and delete data via SQLALchemy sessions
class CRUD():

    def add(self, resource):
        db.session.add(resource)
        return db.session.commit()

    def update(self):
        return db.session.commit()

    def delete(self, resource):
        db.session.delete(resource)
        return db.session.commit()

# Editable tables must have those four columns
# The inheritance approach is from: http://docs.sqlalchemy.org/en/rel_1_0/orm/extensions/declarative/mixins.html#mixing-in-columns
class TableTemplate():
    @declared_attr
    def created_at(cls):
        return db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)

    @declared_attr
    def modified_at(cls):
        return db.Column(db.DateTime, onupdate=datetime.datetime.now)

class User(TableTemplate, db.Model, CRUD):
    query_class = UserQuery

    id               = db.Column(db.Integer, primary_key=True)
    username         = db.Column(db.String(20), unique=True, nullable=False)
    nickname         = db.Column(db.String(20), unique=True)
    password         = db.Column(db.String(20), nullable=False)
    email            = db.Column(db.String(120), unique=True, nullable=False)
    profile_photo_id = db.Column(db.Integer, db.ForeignKey('file.id'), unique=True)
    
    #Seach Vector
    search_vector = db.Column(TSVectorType('username', 'email'))
    profile_photo = db.relationship('File')

    def get_id(self):
        return unicode(self.id)

    def get_email(self):
        return self.email;

    #Functions reserved for login manager
    def is_active(self):
            return self.is_active;

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

class Pin(TableTemplate, db.Model, CRUD):
    id               = db.Column(db.Integer, primary_key=True)
    geo              = db.Column(Geometry(geometry_type='POINT', srid=4326))
    title            = db.Column(db.String(50), nullable=False)
    short_title      = db.Column(db.String(20), nullable=False)
    description      = db.Column(db.String(256))
    owner_id         = db.Column(db.Integer, db.ForeignKey('user.id'))
    pin_photo_id = db.Column(db.Integer, db.ForeignKey('file.id'), unique=True)

    #Relationships
    owner = db.relationship('User', backref=db.backref('pin'))
    pin_photo = db.relationship('File')

    #Seach Vector
    search_vector = db.Column(TSVectorType('title', 'description', 'short_title'))

    @hybrid_property
    def vote_score(self):
        if(self.votes):
            return sum((1 if vote.vote else -1) for vote in self.votes)
        else:
            return 0

    def load_hybrid_properties(self):
        self.vote_score

class Vote(db.Model, CRUD):
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'))
    pin_id      = db.Column(db.Integer, db.ForeignKey('pin.id'))
    vote        = db.Column(db.Boolean, nullable=False)
    
    #Relationships
    user = db.relationship('User', backref=db.backref('votes'))
    pin  = db.relationship('Pin', backref=db.backref('votes'))

    #Constraints
    __table_args__ = (
        db.UniqueConstraint('user_id', 'pin_id'),
        {})
    

class Tag(db.Model, CRUD):
    id           = db.Column(db.Integer, primary_key=True)
    label          = db.Column(db.String(32), nullable=False)

    #Seach Vector
    search_vector = db.Column(TSVectorType('label'))

class PinTag(db.Model, CRUD):
    id      = db.Column(db.Integer, primary_key=True)
    pin_id  = db.Column(db.Integer, db.ForeignKey('pin.id'),nullable = False)
    tag_id  = db.Column(db.Integer, db.ForeignKey('tag.id'),nullable = False)

    #Relationships
    tag = db.relationship('Tag')
    pin = db.relationship('Pin', backref=db.backref('tags'))

    #Constraints
    __table_args__ = (
        db.UniqueConstraint('pin_id', 'tag_id'),
        {})


class Comment(TableTemplate, db.Model, CRUD):
    id                       = db.Column(db.Integer, primary_key=True)
    pin_id                   = db.Column(db.Integer, db.ForeignKey('pin.id'),nullable = False)
    owner_id                 = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    content                  = db.Column(db.String(120), nullable = False)
   
    #Relationships
    owner = db.relationship('User', backref=db.backref('comments'))
    pin   = db.relationship('Pin', backref=db.backref('comments'))

class File(TableTemplate, db.Model, CRUD):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(1024), nullable=False)
    download_url = db.Column(db.String(1024), nullable=False)
