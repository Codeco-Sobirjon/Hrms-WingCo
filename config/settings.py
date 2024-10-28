import os
from datetime import timedelta
from pathlib import Path

from django.conf import settings

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-6c)qkb(2*kox(" "qy7x28b4a4_up#crka=mv81f*3@&jykb3f_e)"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    "daphne",
    "channels",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "drf_yasg",
    "import_export",

    "apps.authentification",
    "apps.enrolls",
    "apps.company",
    "apps.resume",
    "apps.chat",
    "apps.notification",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    "apps.authentification.middleware.json_error_response.JsonErrorResponseMiddleware",
    "apps.authentification.middleware.page_not_found.Custom404Middleware"
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "hrms",
        "USER": "postgres",
        "PASSWORD": "0576",
        "HOST": "localhost",
        "PORT": 5432,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation"
                ".UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation" ".MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation" ".CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation" ".NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/



# FORCE_SCRIPT_NAME = "/hrms"

if DEBUG:
    STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
else:
    STATIC_ROOT = os.path.join(BASE_DIR, "static")
# STATIC_URL = f"{FORCE_SCRIPT_NAME}/static/"
STATIC_URL = "static/"

STATIC_ROOT = os.path.join(BASE_DIR, "static_cdn")

# MEDIA_URL = f"{FORCE_SCRIPT_NAME}/media/"
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# GDAL_LIBRARY_PATH = r'C:\Users\admin\Desktop\Projecs Prounity\hrms\back-end\env\Lib\site-packages\osgeo\gdal304.dll'
# GEOS_LIBRARY_PATH = r'C:\Users\admin\Desktop\Projecs Prounity\hrms\back-end\env\Lib\site-packages\osgeo\geos_c.dll'


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "NON_FIELD_ERRORS_KEY": "errors",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=50),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=3),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'ALLOWED_HOSTS': ['*'],
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME_CLAIM': 'exp',
    'SLIDING_TOKEN_REFRESH_LIFETIME_CLAIM': 'refresh_exp',
    'AUTH_COOKIE_SECURE': False,
    'AUTH_COOKIE_SAMESITE': None,
    'AUTH_COOKIE_SECURE': False,
}

CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
]

EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = "sobirbobojonov2000@gmail.com"
EMAIL_HOST_PASSWORD = "rhngiswryyybicyo"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "JWT [Bearer {JWT}]": {
            "name": "Authorization",
            "type": "apiKey",
            "in": "header",
        }
    },
    "TITLE": "HRMS Backend",
    "DESCRIPTION": "HRMS Backend",
    "VERSION": "0.1.0",
    "USE_SESSION_AUTH": False,
}
SPECTACULAR_SETTINGS = {
    "TITLE": "HRMS Backend",
    "DESCRIPTION": "HRMS Backend",
    "VERSION": "0.1.0",
}

AUTH_USER_MODEL = "authentification.CustomUser"
