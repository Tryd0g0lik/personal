import os

import dotenv
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
print(f"===BASE_DIR=================== {BASE_DIR} ======================BASE_DIR=====")
dotenv.load_dotenv()
IS_DEBUG = os.getenv("IS_DEBUG", "1")
DEBUG = True if int(IS_DEBUG) == 1 else False
# '''' .ENV ''''

DJANGO_SETTINGS_MODULE = os.getenv("DJANGO_SETTINGS_MODULE", "")
SECRET_KEY = os.getenv("SECRET_KEY", "")

# APP
APP_PROTOCOL = os.getenv("APP_PROTOCOL", "")
APP_HOST = os.getenv("APP_HOST", "")
APP_HOST_REMOTE = os.getenv("APP_HOST_REMOTE", "")
APP_PORT = os.getenv("APP_PORT", "")

APP_TIME_ZONE = os.getenv("APP_TIME_ZONE", "")

# db production
POSTGRES_DB = os.getenv("POSTGRES_DB", "person_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "")

POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_ENGINE = os.getenv("DB_ENGINE", "")

# db development
DATABASE_ENGINE_LOCAL = os.getenv("DATABASE_ENGINE_LOCAL", "")
DATABASE_LOCAL = os.getenv("DATABASE_LOCAL", "")

# jwt
JWT_ACCESS_TOKEN_LIFETIME_MINUTES = os.getenv("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", 5)
JWT_REFRESH_TOKEN_LIFETIME_DAYS = os.getenv("JWT_REFRESH_TOKEN_LIFETIME_DAYS", 1)

# Email Service
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PORT = os.getenv("SMTP_PORT", "465")
SMTP_PASS = os.getenv("SMTP_PASS", "")

# Redis
REDIS_HOST = os.getenv("REDIS_HOST", "")
DB_TO_RADIS_PORT = os.getenv("DB_TO_RADIS_PORT", "")
DB_TO_RADIS_HOST = os.getenv("DB_TO_RADIS_HOST", "")
DB_TO_RADIS_CACHE_USERS = os.getenv("DB_TO_RADIS_CACHE_USERS", "")
# '''Cookie'''
SESSION_COOKIE_HTTPONLY = False  # CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True  # change to the True - CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "Lax"  # CSRF_COOKIE_SAMESITE = 'Lax'  # or 'Strict'
CSRF_USE_SESSIONS = False
SESSION_COOKIE_AGE = 86400

# ''' Quantity of admin & superuser '''
IS_ADMIN = os.getenv("IS_ADMIN", "4")
IS_SUPERUSER = os.getenv("IS_SUPERUSER", "1")
DJANGO_ENV = f'{os.getenv("DJANGO_ENV", "production")}'


