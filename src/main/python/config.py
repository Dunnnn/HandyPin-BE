import os

SECRET_KEY = os.urandom(24)
SQLALCHEMY_DATABASE_URI = 'postgres://postgres:postgres@handypin.c37rymkezk94.us-east-1.rds.amazonaws.com:5432/handypin'
