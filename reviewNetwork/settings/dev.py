from reviewNetwork.settings.base import *

DEBUG = True

DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
PAYSAFE_ID = os.environ.get('PAYSAFE_ID')
PAYSAFE_BASE_64_APIKEY = os.environ.get('PAYSAFE_BASE_64_APIKEY')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'DB_NAME',
        'USER': 'DB_USER',
        'PASSWORD': 'DB_PASSWORD',
        'HOST': 'DB_HOST',
        'PORT': 'DB_PORT',
    }
}


import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://f3360401076040a8addd9fc7cdd5f20b@o200667.ingest.sentry.io/5377352",
    integrations=[DjangoIntegration()],

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)
