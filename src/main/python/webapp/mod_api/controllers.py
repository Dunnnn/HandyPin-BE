from flask import Blueprint, request, render_template, redirect, url_for, Flask, jsonify
import flask_restful
from sqlalchemy import and_, or_, exc
from flask_restful import reqparse
from flask_restful_swagger import swagger
from datetime import datetime
from sqlalchemy_searchable import search, parse_search_query
from geoalchemy2 import WKTElement

from ..models.models import *
from ..models.schemas import *

API_VERSION = 1

HTTP_BAD_REQUEST                     = 400
HTTP_UNAUTHORIZED                    = 401
HTTP_PAYMENT_REQUIRED                = 402
HTTP_FORBIDDEN                       = 403
HTTP_NOT_FOUND                       = 404
HTTP_METHOD_NOT_ALLOWED              = 405
HTTP_NOT_ACCEPTABLE                  = 406
HTTP_PROXY_AUTHENTICATION_REQUIRED   = 407
HTTP_REQUEST_TIMEOUT                 = 408
HTTP_CONFLICT                        = 409
HTTP_GONE                            = 410
HTTP_LENGTH_REQUIRED                 = 411
HTTP_PRECONDITION_FAILED             = 412
HTTP_REQUEST_ENTITY_TOO_LARGE        = 413
HTTP_REQUEST_URI_TOO_LONG            = 414
HTTP_UNSUPPORTED_MEDIA_TYPE          = 415
HTTP_REQUESTED_RANGE_NOT_SATISFIABLE = 416
HTTP_EXPECTATION_FAILED              = 417
HTTP_PRECONDITION_REQUIRED           = 428
HTTP_TOO_MANY_REQUESTS               = 429
HTTP_REQUEST_HEADER_FIELDS_TOO_LARGE = 431
HTTP_INTERNAL_SERVER_ERROR           = 500
HTTP_NOT_IMPLEMENTED                 = 501
HTTP_BAD_GATEWAY                     = 502
HTTP_SERVICE_UNAVAILABLE             = 503
HTTP_GATEWAY_TIMEOUT                 = 504
HTTP_HTTP_VERSION_NOT_SUPPORTED      = 505
HTTP_NETWORK_AUTHENTICATION_REQUIRED = 511


mod_api = Blueprint('api', __name__, url_prefix='/api')
api = flask_restful.Api()
"""Calling init_app can defer for Blueprint object"""
api.init_app(mod_api)
api = swagger.docs(api, apiVersion=API_VERSION, api_spec_url='/spec')

"""Users Related Routes"""
class UserResource(flask_restful.Resource):
    def get(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('request_fields', type=str, action='append')

        args = parser.parse_args()
        user_query = User.query

        if(args['request_fields']):
            request_fields = tuple(args['request_fields'])
            user_schema = UserSchema(exclude='password', only=request_fields)
        else:
            user_schema = UserSchema(exclude='password')

        user = user_query.get(user_id)

        if(not user):
            return {"message" :"User not found"}, HTTP_NOT_FOUND

        try:
            user_json = user_schema.dump(user).data
            return user_json
        except AttributeError as err:
            return {"message" : {"request_fields" : format(err)} }, HTTP_BAD_REQUEST

api.add_resource(UserResource, '/users/<int:user_id>')

class UsersResource(flask_restful.Resource):
    def get(self):
        users = User.query.all()
        user_schema = UserSchema()
        return user_schema.dump(users, many=True).data

    def post(self):
        """Sign Up"""
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('email', type=str, required=True)
        args = parser.parse_args()

        username = args['username']
        password = args['password']
        email = args['email']

        existing_user= User.query.filter(or_(User.email==email, User.username==username)).first()
        if(existing_user):
            return {"message" :"Username or email already used"}, HTTP_BAD_REQUEST

        try:
            new_user= User(username=username, password=password, email=email)

            new_user.add(new_user)
            user_schema = UserSchema(exclude=('password',))
            user_json = user_schema.dump(new_user).data
        except exc.IntegrityError as err:
            return{"message" : "Failed to add use during database execution. The error message returned is: {0}".format(err)}, HTTP_BAD_REQUEST

        return user_json

api.add_resource(UsersResource, '/users')

"""Pins Related Routes"""
class PinResource(flask_restful.Resource):
    def get(self, pin_id):
        parser = reqparse.RequestParser()
        parser.add_argument('request_fields', action='append')

        args = parser.parse_args()
        pin_query = Pin.query

        sw_longitude = args['sw_longitude']
        sw_latitude = args['sw_latitude']
        ne_longitude = args['sw_longitude']
        ne_latitude = args['sw_latitude']

        if(args['request_fields']):
            request_fields = tuple(args['request_fields'])
            pin_schema = PinSchema(only=request_fields)
        else:
            pin_schema = PinSchema()

        pin = pin_query.get(pin_id)

        if(not pin):
            return {"message" :"Pin not found"}, HTTP_NOT_FOUND

        try:
            pin_json = pin_schema.dump(pin).data
            return pin_json
        except AttributeError as err:
            return {"message" : {"request_fields" : format(err)} }, HTTP_BAD_REQUEST

api.add_resource(PinResource, '/pins/<int:pin_id>')

class PinsResource(flask_restful.Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('request_fields', action='append')
        #xmin
        parser.add_argument('sw_longitude', type=float)
        #ymin
        parser.add_argument('sw_latitude', type=float)
        #xmax
        parser.add_argument('ne_longitude', type=float)
        #ymax
        parser.add_argument('ne_latitude', type=float)

        args = parser.parse_args()
        pin_query = Pin.query

        sw_longitude = args['sw_longitude']
        sw_latitude = args['sw_latitude']
        ne_longitude = args['ne_longitude']
        ne_latitude = args['ne_latitude']

        pin_query = pin_query.filter(func.ST_Contains(func.ST_MakeEnvelope(sw_longitude, sw_latitude, ne_longitude, ne_latitude, 4326), Pin.geo))

        if(args['request_fields']):
            request_fields = tuple(args['request_fields'])
            pin_schema = PinSchema(only=request_fields)
        else:
            pin_schema = PinSchema()

        pins = pin_query.all()
        print pin_query

        if(not pins):
            return {"message" :"Pin not found"}, HTTP_NOT_FOUND

        try:
            pin_json = pin_schema.dump(pins, many=True).data
            return pin_json
        except AttributeError as err:
            return {"message" : {"request_fields" : format(err)} }, HTTP_BAD_REQUEST

api.add_resource(PinsResource, '/pins')
