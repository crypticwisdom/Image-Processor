from .base import *
import dj_database_url
from decouple import config

print("---------------------- You are on Pay Arena's Production Environment --------------------------------")

SECRET_KEY = 'pMTaRpvdoG9BTSdqODKihVvBJGFOSze0yojoNNOZsIjw8VL6veEWKdXAOuthIQt9XS7o48SBNZr2KJo1ZQ'

DEBUG = False

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'payarena-mall',
        'USER': 'payarena',
        'PASSWORD': 'uUT0D6pBJTnWpVqh+sQvZA',
        'HOST': 'localhost',
        'PORT': '',
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # 'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer'
    ]
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=60),
    'UPDATE_LAST_LOGIN': True,
    'AUTH_HEADER_TYPES': ('Bearer', 'Token',),
}


# CORS_ALLOWED_ORIGINS = []
#
# CORS_ALLOW_ALL_ORIGINS = True
# CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

FRONTEND_VERIFICATION_URL = None

NAME_ENQUIRY = env('NAME_ENQUIRY')

