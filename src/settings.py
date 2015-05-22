import os

from flask import Flask
from flask.ext.restful import Api


environment = os.environ.get('DEPLOYMENT')
app = Flask(__name__)
api = Api(app)


# General
if environment == 'development':
    app.config.update(
        DEBUG = True,
        SITE_URL = 'http://teenypies.samdeng.com'
    )
else:
    app.config.update(
        DEBUG = False,
        SITE_URL = 'http://teenypies.com'
    )


# Authentication
app.config.update(
    USERNAME = 'username',
    PASSWORD = 'password'
)


# Database
app.config.update(
    DATABASE = os.path.join(app.root_path, 'database/content.db'),
    SECRET_KEY = 'XXXXXXXXX'
)


# Email
app.config.update(
    DEBUG = False,
    MAIL_SERVER = 'email-smtp.us-east-1.amazonaws.com',
    MAIL_PORT = 465,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'XXXXXXXXXXXXXXXX',
    MAIL_PASSWORD = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
)

# reCaptcha
recaptcha_private_key = 'XXXXXXXXXXXXXXXXXXX'


# Uploads
app.config.update(
    UPLOAD_FOLDER = os.path.join(app.root_path, '../static/images/pies/'),
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
)
