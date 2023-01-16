from .base import *
print("============================= Development Environment =====================================")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'wRDf2wWTN8zNoNPBvI5ADxwub24fEzOwHh8woTZkwufibfI-0QTSaA'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tm_ip_db',
        'USER': 'tm_ip',
        'HOST': 'localhost',
        'PASSWORD': 'iamherenow',
        'PORT': 5432
    }
}


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
