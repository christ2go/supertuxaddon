import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

GITHUB_CLIENT_ID = "19d7baaa7df1cb2296c7"
GITHUB_CLIENT_SECRET = "b982d78d8cb37ce40488a3a0f4cc102472841294"

SECRET_KEY = "test"

UPLOAD_FOLDER = "/Users/christian/PycharmProjects/supertuxaddon/tmp"