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
    "http://localhost",
]

CORS_ALLOW_ALL_ORIGINS = True
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

