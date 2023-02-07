from .base import *
from decouple import config

SECRET_KEY = env('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = ["*", "payarenamall.tm-dev.xyz"]

DATABASES = {
    'default': {
        'ENGINE': env('DATABASE_ENGINE', None),
        'NAME': env('DATABASE_NAME', None),
        'USER': env('DATABASE_USER', None),
        'PASSWORD': env('DATABASE_PASSWORD', None),
        'HOST': env('DATABASE_HOST', None),
        'PORT': env('DATABASE_PORT', None),
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
    "https://payarenamall.tm-dev.xyz",
    "http://localhost:8080",
    "http://localhost:80",
    "http://localhost:3000",
    "http://localhost",
    "http://127.0.0.1"
]

CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=60),
    'UPDATE_LAST_LOGIN': True,
    'AUTH_HEADER_TYPES': ('Bearer', 'Token',),
}

# SITE CONFIG
SIMILAR_PRODUCT_LIMIT = env('SIMILAR_PRODUCT_LIMIT', None)
# Email
EMAIL_URL = env('EMAIL_URL', None)
# Shipping
SHIPPING_BASE_URL = env('SHIPPING_BASE_URL', None)
SHIPPING_EMAIL = env('SHIPPING_EMAIL', None)
SHIPPING_PASSWORD = env('SHIPPING_PASSWORD', None)
SHIPPING_TOKEN = env('SHIPPING_TOKEN', None)

AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', None)
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', None)
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', None)
AWS_LOCATION = env('AWS_LOCATION', None)
# AWS_S3_ENDPOINT_URL = 'https://objectstorage.uk-london-1.oraclecloud.com'
AWS_S3_ENDPOINT_URL = env('AWS_S3_ENDPOINT_URL', None)
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

FRONTEND_VERIFICATION_URL = env('FRONTEND_VERIFICATION_URL', None)
FRONTEND_PAYMENT_REDIRECT_URL = env('FRONTEND_PAYMENT_REDIRECT_URL', None)
FRONTEND_URL = env('FRONTEND_URL', None)
NAME_ENQUIRY = env('NAME_ENQUIRY', None)

PAYARENA_ACCOUNT_BASE_URL = env('PAYARENA_ACCOUNT_BASE_URL', None)

# PAYMENT GATEWAY
PAYMENT_GATEWAY_URL = env("PAYMENT_GATEWAY_URL", None)
PAYMENT_GATEWAY_MERCHANT_ID = env("PAYMENT_GATEWAY_MERCHANT_ID", None)
PAYMENT_GATEWAY_SECRET_KEY = env("PAYMENT_GATEWAY_SECRET_KEY", None)
PAYMENT_CREDIT_WALLET_URL = env("PAYMENT_CREDIT_WALLET_URL", None)

# PAYARENA ENCRYPTION
PAYARENA_CYPHER_KEY = env("PAYARENA_CYPHER_KEY", None)
PAYARENA_IV = env("PAYARENA_IV", None)

BANK_URL = env("BANK_URL", None)

# U_MAP CREDENTIALS
U_MAP_BASE_URL = env("U_MAP_BASE_URL", None)
U_MAP_USER_ID = env("U_MAP_USER_ID", None)
U_MAP_PASSWORD = env("U_MAP_PASSWORD", None)

# Billing
BILLING_BASE_URL = env('BILLING_BASE_URL', None)
BILLING_EMAIL = env('BILLING_EMAIL', None)
BILLING_PASSWORD = env('BILLING_PASSWORD', None)
BILLING_TOKEN = env('BILLING_TOKEN', None)
BILLING_USER_ID = env('BILLING_USER_ID', None)

PAYARENA_MERCHANT_ID = env('PAYARENA_MERCHANT_ID', None)

# Elasticsearch
ELASTICSEARCH_URL = env('ELASTICSEARCH_URL', None)

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': ELASTICSEARCH_URL
    },
}

CRONJOBS = [
    ('59 23 */2 * *', 'ecommerce.cron.remove_redundant_cart_cron'),
]

# These are Production Credentials.
IMAGE_PROCESSOR_EMAIL = env('IMAGE_PROCESSOR_EMAIL', None)
IMAGE_PROCESSOR_CLIENT_NAME = env('IMAGE_PROCESSOR_CLIENT_NAME', None)
IMAGE_PROCESSOR_PASSWORD = env('IMAGE_PROCESSOR_PASSWORD', None)
IMAGE_PROCESS_BASE_URL = env('IMAGE_PROCESS_BASE_URL', None)

IMAGE_PROCESSOR_CLIENT_TOKEN = env('IMAGE_PROCESSOR_CLIENT_TOKEN', None)

IMAGE_PROCESSOR_MERCHANT_STORE_BANNER_BLOCK_NAME = env('IMAGE_PROCESSOR_MERCHANT_STORE_BANNER_BLOCK_NAME', None)
IMAGE_PROCESSOR_MERCHANT_STORE_BANNER_TOKEN = env('IMAGE_PROCESSOR_MERCHANT_STORE_BANNER_TOKEN', None)

IMAGE_PROCESSOR_MALL_PRODUCT_BLOCK_NAME = env('IMAGE_PROCESSOR_MALL_PRODUCT_BLOCK_NAME', None)
IMAGE_PROCESSOR_MALL_PRODUCT_TOKEN = env('IMAGE_PROCESSOR_MALL_PRODUCT_TOKEN', None)

IMAGE_PROCESSOR_MALL_HEADER_BANNER_BLOCK_NAME = env('IMAGE_PROCESSOR_MALL_HEADER_BANNER_BLOCK_NAME', None)
IMAGE_PROCESSOR_MALL_HEADER_BANNER_TOKEN = env('IMAGE_PROCESSOR_MALL_HEADER_BANNER_TOKEN', None)

IMAGE_PROCESSOR_MALL_FOOTER_BANNER_BLOCK_NAME = env('IMAGE_PROCESSOR_MALL_FOOTER_BANNER_BLOCK_NAME', None)
IMAGE_PROCESSOR_MALL_FOOTER_BANNER_TOKEN = env('IMAGE_PROCESSOR_MALL_FOOTER_BANNER_TOKEN', None)

IMAGE_PROCESSOR_MALL_BIG_BANNER_BLOCK_NAME = env('IMAGE_PROCESSOR_MALL_BIG_BANNER_BLOCK_NAME', None)
IMAGE_PROCESSOR_MALL_BIG_BANNER_TOKEN = env('IMAGE_PROCESSOR_MALL_BIG_BANNER_TOKEN', None)

IMAGE_PROCESSOR_MALL_MEDIUM_BANNER_BLOCK_NAME=env('IMAGE_PROCESSOR_MALL_MEDIUM_BANNER_BLOCK_NAME', None)
IMAGE_PROCESSOR_MALL_MEDIUM_BANNER_TOKEN=env('IMAGE_PROCESSOR_MALL_MEDIUM_BANNER_TOKEN', None)

IMAGE_PROCESSOR_MALL_SMALL_BANNER_BLOCK_NAME=env('IMAGE_PROCESSOR_MALL_SMALL_BANNER_BLOCK_NAME', None)
IMAGE_PROCESSOR_MALL_SMALL_BANNER_BLOCK_TOKEN=env('IMAGE_PROCESSOR_MALL_SMALL_BANNER_BLOCK_TOKEN', None)

IMAGE_PROCESSOR_MALL_MERCHANT_BANNER_BLOCK_NAME=env('IMAGE_PROCESSOR_MALL_MERCHANT_BANNER_BLOCK_NAME', None)
IMAGE_PROCESSOR_MALL_MERCHANT_BANNER_BLOCK_TOKEN=env('IMAGE_PROCESSOR_MALL_MERCHANT_BANNER_BLOCK_TOKEN', None)

IMAGE_PROCESSOR_MALL_SPA_BRAND_UPLOAD_BLOCK_NAME=env('IMAGE_PROCESSOR_MALL_SPA_BRAND_UPLOAD_BLOCK_NAME', None)
IMAGE_PROCESSOR_MALL_SPA_BRAND_UPLOAD_BLOCK_TOKEN=env('IMAGE_PROCESSOR_MALL_SPA_BRAND_UPLOAD_BLOCK_TOKEN', None)


