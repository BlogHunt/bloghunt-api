"""
Django settings for bloghunt project.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
from datetime import timedelta

import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
# SECURITY WARNING: don't run with debug turned on in production!
try:
    SECRET_KEY = os.environ['SECRET_KEY']
except KeyError:
    SECRET_KEY = 'mock secret'
    DEBUG = True
else:
    DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'pinesearch.com').split(':')
if DEBUG:
    ALLOWED_HOSTS.append('*')


# Application definition

INSTALLED_APPS = [
    # Django contrib apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django.contrib.sites",

    # 3rd party apps
    'oauth2_provider',
    'rest_framework',
    'pinax.stripe',

    # Local apps
    'feeds',
    'users',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bloghunt.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bloghunt.wsgi.application'

DATABASES = {'default': dj_database_url.config(default='sqlite:///db.sqlite3')}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# One-week activation window; you may, of course, use a different value.
ACCOUNT_ACTIVATION_DAYS = 7

# Security
SECURE_HSTS_SECONDS = 518400
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_FRAME_DENY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_HTTPONLY = True

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True

if not DEBUG:
    # See notes at https://docs.djangoproject.com/en/1.10/ref/settings/
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Sending Email

EMAIL_HOST = os.environ.get('EMAIL_HOST', None)
EMAIL_PORT = os.environ.get('EMAIL_PORT', None)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', None)
EMAIL_HOST_PASSWORD  = os.environ.get('EMAIL_HOST_PASSWORD', None)
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', None)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.environ.get('STATIC_ROOT', 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]


# REST API defaults

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'bloghunt.throttling.GlobalScopedDefaultsTrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '60/minute',
        'user': '60/minute',
        'premium': '1000/minute',
    },
    'PAGE_SIZE': 25,
}

# if DEBUG:
#     REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
#         'rest_framework.renderers.JSONRenderer',
# #         'rest_framework.renderers.BrowsableAPIRenderer',
#     )

OAUTH2_PROVIDER = {
    'SCOPES': {
        'read': 'Read scope',
    }
}

AUTHENTICATION_BACKENDS = (
    'oauth2_provider.backends.OAuth2Backend',
    'django.contrib.auth.backends.ModelBackend'
)

# Celery Settings

try:
    BROKER_URL = os.environ['BROKER_URL']
    CELERY_RESULT_BACKEND = os.environ['BACKEND_URL']
except KeyError:
    CELERY_ALWAYS_EAGER = True
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_RESULT_EXPIRES = timedelta(minutes=15)
CELERY_DEFAULT_EXCHANGE = 'default'
CELERY_TIMEZONE = 'UTC'

# Stripe Settings

PINAX_STRIPE_PUBLIC_KEY = os.environ['STRIPE_API_KEY']
PINAX_STRIPE_SECRET_KEY = os.environ['STRIPE_API_SECRET']
PINAX_STRIPE_DEFAULT_PLAN = os.environ['STRIPE_DEFAULT_PLAN']
SITE_ID = 1
