from .base import *

print("============================= Production Environment =====================================")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'xBOzPwqV3HKQXncxdie6EJdSoQM9aQcvPEacYlprOZHEMcS5YODfIX1QC3vJPirx1Oaq_AMVHH0rcggp'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'tm_ip',
#         'USER': 'tm_ip_db',
#         'HOST': 'localhost',
#         'PASSWORD': 'iamherenow',
#         'PORT': 5432
#     }
# }


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=3),
    'UPDATE_LAST_LOGIN': True,
    'AUTH_HEADER_TYPES': ('Bearer', 'Token',),
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
}
CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://localhost:8000",
    "http://localhost:80",
    "http://localhost:3000",
    "http://localhost",
    "http://127.0.0.1"
]

CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS
