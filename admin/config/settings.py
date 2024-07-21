from pathlib import Path
import os
from dotenv import load_dotenv
from split_settings.tools import include
import sentry_sdk


load_dotenv()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", False) == "True"


include(
    "components/database.py",
    "components/installed_apps.py",
    "components/middlewares.py",
    "components/templates.py",
    "components/pass_validators.py",
)

ALLOWED_HOSTS = (
    os.environ.get("ALLOWED_HOSTS")
    .replace("[", "")
    .replace("]", "")
    .replace("'", "")
    .split(",")
)


ROOT_URLCONF = "config.urls"


WSGI_APPLICATION = "config.wsgi.application"

AUTHENTICATION_BACKENDS = [
    "users.auth.CustomBackend",
    # 'django.contrib.auth.backends.ModelBackend',
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "ru-RU"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

AUTH_API_LOGIN_URL = os.environ.get("AUTH_API_LOGIN_URL")


sentry_sdk.init(
    dsn="https://cf3dc30539417cdefc65204e4ca2fe4b@o4507457845592064.ingest.de.sentry.io/4507640034820176",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)
