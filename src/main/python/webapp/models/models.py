from flask import Flask
from flask_sqlalchemy import SQLAlchemy, BaseQuery
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy_searchable import make_searchable, SearchQueryMixin
from sqlalchemy_utils.types import TSVectorType
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from geoalchemy2 import Geometry, Geography

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

    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    nickname = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20), nullable=False)
    email    = db.Column(db.String(120), unique=True, nullable=False)
    
    #Seach Vector
    search_vector = db.Column(TSVectorType('username', 'email'))

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
    id          = db.Column(db.Integer, primary_key=True)
    geo         = db.Column(Geography(geometry_type='POINT', srid=4326))
    title       = db.Column(db.String(20), nullable=False)
    short_title = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(120))
    owner_id       = db.Column(db.Integer, db.ForeignKey('user.id'))

    #Relationships
    owner = db.relationship('User', backref=db.backref('pin'))

    #Seach Vector
    search_vector = db.Column(TSVectorType('title', 'description', 'short_title'))


class Vote(db.Model, CRUD):
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'))
    pin_id      = db.Column(db.Integer, db.ForeignKey('pin.id'))
    Vote        = db.Column(db.Boolean, nullable=False)
    
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








