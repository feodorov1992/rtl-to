from rest_framework.authentication import TokenAuthentication

from rtl_to.settings import *

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'app_auth',
    'django_genericfilters',
    'orders',
    'print_forms',
    'pricing',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'drf_spectacular',
    'tech_api'
]

ROOT_URLCONF = 'rtl_to.tech_api_urls'

WSGI_APPLICATION = 'rtl_to.tech_api_wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rtl_to.tech_api_auth.BearerAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'SERVE_INCLUDE_SCHEMA': False
}

DEBUG = False
