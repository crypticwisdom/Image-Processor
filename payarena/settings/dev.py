from .base import *
from decouple import config

print("------------------ You are on Pay Arena's Development Environment --------------------")

SECRET_KEY = env('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = ["*", "payarenamall.tm-dev.xyz"]

DATABASES = {
    'default': {
        'ENGINE': env('DATABASE_ENGINE'),
        'NAME': env('DATABASE_NAME'),
        'USER': env('DATABASE_USER'),
        'PASSWORD': env('DATABASE_PASSWORD'),
        'HOST': env('DATABASE_HOST'),
        'PORT': env('DATABASE_PORT'),
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated']
}


CORS_ALLOWED_ORIGINS = [
    "https://payarenamall.tm-dev.xyz",
    "http://localhost:8080",
    "http://localhost:80",
    "http://localhost:3000",
    "http://localhost",
]

# CORS_ALLOW_ALL_ORIGINS = True
# CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=60),
    'UPDATE_LAST_LOGIN': True,
    'AUTH_HEADER_TYPES': ('Bearer', 'Token',),
}

# SITE CONFIG
SIMILAR_PRODUCT_LIMIT = env('SIMILAR_PRODUCT_LIMIT')
# Email
EMAIL_URL = env('EMAIL_URL')
# Shipping
SHIPPING_BASE_URL = env('SHIPPING_BASE_URL')
SHIPPING_EMAIL = env('SHIPPING_EMAIL')
SHIPPING_PASSWORD = env('SHIPPING_PASSWORD')


AWS_ACCESS_KEY_ID = 'b95ded76045bd40bb2c2600ae55f6364c4b96c63'
AWS_SECRET_ACCESS_KEY = 'TjvAExwWyT9NhpM/S9oM0J6Cg/8YabaqtfGNF/kd2+k='
AWS_STORAGE_BUCKET_NAME = 'PayArena_Mall'
AWS_LOCATION = 'payarena'
# AWS_S3_ENDPOINT_URL = 'https://yep-us-app-tm30.fra1.digitaloceanspaces.com'
AWS_S3_ENDPOINT_URL = 'https://objectstorage.uk-london-1.oraclecloud.com'
AWS_S3_CUSTOM_DOMAIN = ''
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE = False

# STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

