import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-notification-mgmt-key-development')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*'] if DEBUG else os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,.render.com,testserver').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'corsheaders',
    'rest_framework',
    
    # Local apps
    'notifications',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'notification_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.parent / 'frontend'],
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

WSGI_APPLICATION = 'notification_system.wsgi.application'

# Database Configuration
# Production (Render): DATABASE_URL
# Local Development: MySQL (configurable via .env, with resilient fallback to SQLite)
DATABASE_URL = os.getenv('DATABASE_URL')
DB_ENGINE = os.getenv('DB_ENGINE', 'mysql').lower()

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
    }
elif DB_ENGINE == 'mysql':
    db_name = os.getenv('DB_NAME', 'notification_db')
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    db_host = os.getenv('DB_HOST', '127.0.0.1')
    db_port = int(os.getenv('DB_PORT', '3306'))

    # Verify actual MySQL connection with credentials; if unavailable, use local sqlite3
    mysql_is_running = False
    try:
        conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            port=db_port,
            connect_timeout=1
        )
        conn.close()
        mysql_is_running = True
    except Exception:
        mysql_is_running = False

    if mysql_is_running:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': db_name,
                'USER': db_user,
                'PASSWORD': db_password,
                'HOST': db_host,
                'PORT': str(db_port),
                'OPTIONS': {
                    'charset': 'utf8mb4',
                }
            }
        }
    else:
        # Fallback to local SQLite when local MySQL service is not yet started or accessible
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 6}},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR.parent / 'frontend',
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'notification_system.authentication.CsrfExemptSessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}

# CORS & CSRF Configuration
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    'https://*.vercel.app',
    'https://*.onrender.com',
]

SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = True

# Channel Provider Configuration
WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN', 'EAAfj2qvSNMcBSZAFChZC6aZCDl8S50ZCXTV4mOyRmPZAtgJcG2jfocnQz7ZCDrA0plyenhDlSCE9YaxEXOzikD8lzR7YUigxYB9Fjw1zrXZCjmdOPnIBZAXX8q79RcrpZBoZCYDMuMFooWyltADtl8DZBZA1P3kWcjg2iXsjG15iARxVcZAD1yjSJrFg2SBEyEbHGSKOgMyIiBPR4XZBfGp6ZCDekkwjh6ZBrVE7YfC4O5wcYGDgBO3cajI9p01fgZBplL3DVCbAgml0zPwBCn0ZBtQEeM8KDrohA1')
PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID', '1364788486708829')
WHATSAPP_TEST_RECIPIENT = os.getenv('WHATSAPP_TEST_RECIPIENT', '919971086529')

EMAIL_PROVIDER = os.getenv('EMAIL_PROVIDER', 'postmark' if os.getenv('POSTMARKAPP_TOKEN') else 'resend').lower()
EMAIL_API_KEY = os.getenv('EMAIL_API_KEY', '')
POSTMARKAPP_TOKEN = os.getenv('POSTMARKAPP_TOKEN', '')
POSTMARK_FROM_EMAIL = os.getenv('POSTMARK_FROM_EMAIL', '')
DEFAULT_FROM_EMAIL = os.getenv('POSTMARK_FROM_EMAIL', os.getenv('DEFAULT_FROM_EMAIL', 'onboarding@resend.dev'))
EMAIL_TEST_RECIPIENT = os.getenv('EMAIL_TEST_RECIPIENT', 'asha3451@hotmail.com')

ONESIGNAL_APP_ID = os.getenv('ONESIGNAL_APP_ID', '')
ONESIGNAL_REST_API_KEY = os.getenv('ONESIGNAL_REST_API_KEY', '')

VAPID_PUBLIC_KEY = os.getenv('VAPID_PUBLIC_KEY', 'BEwCwy5SLgW13NBVbA8YzA7yNZ9yfDEv42cjJRk5Ly2auIMKAEQL2QsV1Ercg1c7qaZxlSbwJRox3UazxSDa2Wo')
VAPID_PRIVATE_KEY = os.getenv('VAPID_PRIVATE_KEY', 'wzbAEiujSaFJepO-19ycbxYdPvZjab_iJa5zyu4jVDY')
VAPID_ADMIN_EMAIL = os.getenv('VAPID_ADMIN_EMAIL', 'admin@notifications.com')
