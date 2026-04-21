"""
Django settings for Glovoke backend.
"""

from pathlib import Path
from datetime import timedelta
import os

# ─────────────────────────────────────────────────────────────
#  Paths
# ─────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent


# ─────────────────────────────────────────────────────────────
#  Security  (override via environment in production)
# ─────────────────────────────────────────────────────────────

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-o@0rynci-3*3mnzdq+9^ksj%%44*f2f395h!y%qdex)1gmt^+h'
)

DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')


# ─────────────────────────────────────────────────────────────
#  Installed Apps
# ─────────────────────────────────────────────────────────────

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',

    # Local
    'core',
]


# ─────────────────────────────────────────────────────────────
#  Middleware
# ─────────────────────────────────────────────────────────────

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',          # ← must be before CommonMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ─────────────────────────────────────────────────────────────
#  URL / WSGI
# ─────────────────────────────────────────────────────────────

ROOT_URLCONF = 'backend.urls'
WSGI_APPLICATION = 'backend.wsgi.application'


# ─────────────────────────────────────────────────────────────
#  Templates
# ─────────────────────────────────────────────────────────────

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ─────────────────────────────────────────────────────────────
#  Database
# ─────────────────────────────────────────────────────────────

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# PostgreSQL — uncomment and set env vars when ready for production:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME':     os.environ.get('DB_NAME',     'glovoke'),
#         'USER':     os.environ.get('DB_USER',     'postgres'),
#         'PASSWORD': os.environ.get('DB_PASSWORD', ''),
#         'HOST':     os.environ.get('DB_HOST',     'localhost'),
#         'PORT':     os.environ.get('DB_PORT',     '5432'),
#     }
# }


# ─────────────────────────────────────────────────────────────
#  Custom User model
# ─────────────────────────────────────────────────────────────

AUTH_USER_MODEL = 'core.User'


# ─────────────────────────────────────────────────────────────
#  Password validation
# ─────────────────────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ─────────────────────────────────────────────────────────────
#  Internationalisation
# ─────────────────────────────────────────────────────────────

LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'Africa/Nairobi'
USE_I18N      = True
USE_TZ        = True


# ─────────────────────────────────────────────────────────────
#  Static & Media files
# ─────────────────────────────────────────────────────────────

STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ─────────────────────────────────────────────────────────────
#  Default primary key
# ─────────────────────────────────────────────────────────────

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ─────────────────────────────────────────────────────────────
#  Django REST Framework
# ─────────────────────────────────────────────────────────────

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    # Show Browsable API in DEBUG mode only
    **(
        {'DEFAULT_RENDERER_CLASSES': [
            'rest_framework.renderers.JSONRenderer',
            'rest_framework.renderers.BrowsableAPIRenderer',
        ]}
        if DEBUG else {}
    ),
}


# ─────────────────────────────────────────────────────────────
#  Simple JWT
# ─────────────────────────────────────────────────────────────

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':  timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS':  True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}


# ─────────────────────────────────────────────────────────────
#  CORS  (django-cors-headers)
# ─────────────────────────────────────────────────────────────

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = os.environ.get(
        'CORS_ALLOWED_ORIGINS',
        'http://localhost:5173,http://localhost:3000'
    ).split(',')

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]


# ─────────────────────────────────────────────────────────────
#  Sessions  (used by guest/anonymous carts)
# ─────────────────────────────────────────────────────────────

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30   # 30 days
SESSION_SAVE_EVERY_REQUEST = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'


# ─────────────────────────────────────────────────────────────
#  File upload limits
# ─────────────────────────────────────────────────────────────

DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10 MB


# ─────────────────────────────────────────────────────────────
#  Email  (console in dev, SMTP in production)
# ─────────────────────────────────────────────────────────────

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND    = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST       = os.environ.get('EMAIL_HOST',       'smtp.gmail.com')
    EMAIL_PORT       = int(os.environ.get('EMAIL_PORT',   '587'))
    EMAIL_USE_TLS    = True
    EMAIL_HOST_USER  = os.environ.get('EMAIL_HOST_USER',  '')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'Glovoke <noreply@glovoke.com>')


# ─────────────────────────────────────────────────────────────
#  Logging
# ─────────────────────────────────────────────────────────────

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG' if DEBUG else 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',   # set to DEBUG to log all SQL queries
            'propagate': False,
        },
    },
}


# ─────────────────────────────────────────────────────────────
#  M-Pesa  (Safaricom Daraja — add your own keys)
# ─────────────────────────────────────────────────────────────

MPESA_CONSUMER_KEY    = os.environ.get('MPESA_CONSUMER_KEY',    '')
MPESA_CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET', '')
MPESA_SHORTCODE       = os.environ.get('MPESA_SHORTCODE',       '')
MPESA_PASSKEY         = os.environ.get('MPESA_PASSKEY',         '')
MPESA_CALLBACK_URL    = os.environ.get('MPESA_CALLBACK_URL',    'https://yourdomain.com/api/mpesa/callback/')
MPESA_ENVIRONMENT     = os.environ.get('MPESA_ENVIRONMENT',     'sandbox')   # 'sandbox' | 'production'