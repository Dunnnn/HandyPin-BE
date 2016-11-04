from flask import Blueprint, request, render_template, redirect, url_for, Flask, jsonify
import werkzeug
import flask_restful
from sqlalchemy import and_, or_, exc, func
from flask_restful import reqparse
from flask_restful_swagger import swagger
from datetime import datetime
from sqlalchemy_searchable import search, parse_search_query
from geoalchemy2 import WKTElement

from ..models.models import *
from ..models.schemas import *
from ..lib.s3_lib import *

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
        parser.add_argument('keyword', type=str)
        parser.add_argument('current_user_id', type=int)

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

        if(args['keyword']):
            keyword = args['keyword']

            combined_search_vector = ( Pin.search_vector | User.search_vector | func.coalesce(Tag.search_vector, u'') )

            pin_query = pin_query.join(User).outerjoin(PinTag).outerjoin(Tag).filter(combined_search_vector.match(parse_search_query(keyword)))

        pins = pin_query.all()
        if(args['current_user_id']):
            for pin in pins:
                if(pin.votes):
                    for vote in pin.votes:
                        if(vote.user_id == args['current_user_id']):
                            pin.vote_by_current_user = vote

        if(not pins):
            return {"message" :"Pin not found"}, HTTP_NOT_FOUND

        try:
            pin_json = pin_schema.dump(pins, many=True).data
            return pin_json
        except AttributeError as err:
            return {"message" : {"request_fields" : format(err)} }, HTTP_BAD_REQUEST

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('longitude', type=float, required=True)
        parser.add_argument('latitude', type=float, required=True)
        parser.add_argument('title', type=str, required=True)
        parser.add_argument('short_title', type=str, required=True)
        parser.add_argument('description', type=str)
        parser.add_argument('owner_id', type=int, required=True)
        parser.add_argument('tag_strings', type=str, action='append')

        args = parser.parse_args()

        longitude = args['longitude']
        latitude = args['latitude']
        title = args['title']
        short_title = args['short_title']
        owner_id = args['owner_id']
        description = args['description']
        tag_strings = None

        if(args['tag_strings']):
            tag_strings = args['tag_strings']

        try:
            new_pin = Pin(title=title, short_title=short_title, owner_id=owner_id, description=description, geo=WKTElement('Point({0} {1})'.format(longitude, latitude), srid=4326))

            new_pin.add(new_pin)

            if(tag_strings):
                for tag_string in tag_strings:
                    tag = Tag.query.filter_by(label=tag_string).first()
                    if(tag):
                        pintag = PinTag(pin=new_pin, tag=tag)
                        pintag.add(pintag)
                    else:
                        new_tag = Tag(label=tag_string.lower())
                        new_tag.add(new_tag)
                        pintag = PinTag(pin=new_pin, tag=new_tag)
                        pintag.add(pintag)
        
            pin_schema = PinSchema()
            pin_json = pin_schema.dump(new_pin).data
        except exc.IntegrityError as err:
            return{"message" : "Failed to add pin during database execution. The error message returned is: {0}".format(err)}, HTTP_BAD_REQUEST

        return pin_json


api.add_resource(PinsResource, '/pins')

class VotePin(flask_restful.Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True)
        parser.add_argument('pin_id', type=int, required=True)
        parser.add_argument('vote', type=int, required=True)

        args = parser.parse_args()
        user_id = args['user_id']
        pin_id = args['pin_id']
        vote = args['vote']

        pin_query = Pin.query

        pin = pin_query.get(pin_id)

        if(not pin):
            return {"message" :"Pin not found"}, HTTP_NOT_FOUND

        user_query = User.query
        user = user_query.get(user_id)

        if(not user):
            return {"message" :"User not found"}, HTTP_NOT_FOUND

        vote_query = Vote.query

        existing_vote= vote_query.filter(and_(Vote.user_id==user_id, Vote.pin_id==pin_id)).first()
        if(existing_vote):
            return {"message" :"User have already voted"}, HTTP_BAD_REQUEST

        try:
            if(vote == 0):
                user_vote = False;
            else:
                user_vote = True;

            new_vote= Vote(user_id=user_id, pin_id=pin_id, vote=user_vote)

            new_vote.add(new_vote)
            vote_schema = VoteSchema()
            vote_json = vote_schema.dump(new_vote).data
        except exc.IntegrityError as err:
            return{"message" : "Failed to add vote during database execution. The error message returned is: {0}".format(err)}, HTTP_BAD_REQUEST

        return vote_json
    

api.add_resource(VotePin, '/votes')

class DeleteVote(flask_restful.Resource):
    def delete(self, vote_id):
        vote = Vote.query.get(vote_id)

        if(vote):
            vote.delete(vote)
            return {"message" : "Vote successfully deleted"}
        else:
            return {"message" : "Vote not found" }, HTTP_NOT_FOUND
        

api.add_resource(DeleteVote, '/votes/<int:vote_id>')
    


class CommentPin(flask_restful.Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('owner_id', type=int, required=True)
        parser.add_argument('pin_id', type=int, required=True)
        parser.add_argument('content', type=str, required=True)

        args = parser.parse_args()
        owner_id = args['owner_id']
        pin_id = args['pin_id']
        content = args['content']

        pin_query = Pin.query

        pin = pin_query.get(pin_id)

        if(not pin):
            return {"message" :"Pin not found"}, HTTP_NOT_FOUND

        user_query = User.query
        user = user_query.get(owner_id)

        if(not user):
            return {"message" :"User not found"}, HTTP_NOT_FOUND

        comment_query = Comment.query

        if (content == ""):
            return {"message" :"content is not valid"}, HTTP_BAD_REQUEST

        try:
            new_comment= Comment(owner_id=owner_id, pin_id=pin_id, content=content)

            new_comment.add(new_comment)
            comment_schema = CommentSchema()
            comment_json = comment_schema.dump(new_comment).data
        except exc.IntegrityError as err:
            return{"message" : "Failed to add comment during database execution. The error message returned is: {0}".format(err)}, HTTP_BAD_REQUEST

        return comment_json

api.add_resource(CommentPin, '/comment')

class UploadUserProfilePhoto(flask_restful.Resource):
    def post(self, user_id):
        user = User.query.get(user_id)

        if(not user):
            return {"message" :"User not found"}, HTTP_NOT_FOUND

        parser = reqparse.RequestParser()
        parser.add_argument('profile_photo', type=werkzeug.datastructures.FileStorage, location='files')

        args = parser.parse_args()
        profile_photo = args['profile_photo']
        profile_photo_basename = profile_photo.filename.rsplit('.', 1)[0]
        profile_photo_ext = profile_photo.filename.rsplit('.', 1)[1]

        #Recompose filename to include current datetime
        profile_photo_filename = 'user{0}_{1}_{2}.{3}'.format(user_id, profile_photo_basename, datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'), profile_photo_ext)
        profile_photo_tmp_path = os.path.join(app.config['UPLOAD_FOLDER'], profile_photo_filename)
        profile_photo.save(profile_photo_tmp_path)

        upload_error = None
        try:
            s3_helper = S3Helper()
            s3_helper.upload_file(profile_photo_tmp_path, profile_photo_filename)
	except:
            upload_error = True
        finally:
            os.remove(profile_photo_tmp_path)

        if(upload_error):
            return {"message" : "Failed to upload profile picture"}, HTTP_INTERNAL_SERVER_ERROR

        profile_photo_s3_url = 'https://s3.amazonaws.com/handypin/{0}'.format(profile_photo_filename)
        profile_photo_file = File(filename = profile_photo_filename, download_url = profile_photo_s3_url)
        user.profile_photo = profile_photo_file
        user.update()
        file_schema = FileSchema()

        return file_schema.dump(profile_photo_file).data


api.add_resource(UploadUserProfilePhoto, '/users/<int:user_id>/profile_photo')

