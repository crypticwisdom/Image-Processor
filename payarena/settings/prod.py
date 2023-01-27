from .base import *
import dj_database_url
from decouple import config

SECRET_KEY = env('SECRET_KEY')

DEBUG = False

ALLOWED_HOSTS = ["*", "apimall.payarena.com"]

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
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated']
}

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "https://mall.payarena.com",
    "http://localhost:8080",
    "http://localhost:80",
    "http://localhost:3000",
    "http://localhost",
    "http://127.0.0.1"
]

CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=60),
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
SHIPPING_TOKEN = env('SHIPPING_TOKEN')

AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
AWS_LOCATION = env('AWS_LOCATION')
AWS_S3_ENDPOINT_URL = env('AWS_S3_ENDPOINT_URL')
AWS_S3_CUSTOM_DOMAIN = ''
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE = False

STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

FRONTEND_VERIFICATION_URL = env('FRONTEND_VERIFICATION_URL')
FRONTEND_PAYMENT_REDIRECT_URL = env('FRONTEND_PAYMENT_REDIRECT_URL')
FRONTEND_URL = env('FRONTEND_URL')
NAME_ENQUIRY = env('NAME_ENQUIRY')

PAYARENA_ACCOUNT_BASE_URL = env('PAYARENA_ACCOUNT_BASE_URL')

# PAYMENT GATEWAY
PAYMENT_GATEWAY_URL = env("PAYMENT_GATEWAY_URL")
PAYMENT_GATEWAY_MERCHANT_ID = env("PAYMENT_GATEWAY_MERCHANT_ID")
PAYMENT_GATEWAY_SECRET_KEY = env("PAYMENT_GATEWAY_SECRET_KEY")
PAYMENT_CREDIT_WALLET_URL = env("PAYMENT_CREDIT_WALLET_URL")

# PAYARENA ENCRYPTION
PAYARENA_CYPHER_KEY = env("PAYARENA_CYPHER_KEY")
PAYARENA_IV = env("PAYARENA_IV")

BANK_URL = env("BANK_URL")

# U_MAP CREDENTIALS
U_MAP_BASE_URL = env("U_MAP_BASE_URL")
U_MAP_USER_ID = env("U_MAP_USER_ID")
U_MAP_PASSWORD = env("U_MAP_PASSWORD")

# Billing
BILLING_BASE_URL = env('BILLING_BASE_URL')
BILLING_EMAIL = env('BILLING_EMAIL')
BILLING_PASSWORD = env('BILLING_PASSWORD')
BILLING_TOKEN = env('BILLING_TOKEN')
BILLING_USER_ID = env('BILLING_USER_ID')

PAYARENA_MERCHANT_ID = env('PAYARENA_MERCHANT_ID')

# Elasticsearch
ELASTICSEARCH_URL = env('ELASTICSEARCH_URL')

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': ELASTICSEARCH_URL
    },
}

CRONJOBS = [
    ('59 23 */2 * *', 'ecommerce.cron.remove_redundant_cart_cron'),
]

# Production credentials for Image Processor will should be added.