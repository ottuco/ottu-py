SECRET_KEY = "django-insecure"
DEBUG = True
ALLOWED_HOSTS = []
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "django.contrib.auth",
    "django.contrib.admin",
    "ottu.contrib.django",
    "tests.test_ottu.test_contrib.test_django.polls",
]

MIDDLEWARE = []

ROOT_URLCONF = "tests.test_ottu.test_contrib.test_django.polls.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

USE_TZ = True

# Ottu settings
OTTU_MERCHANT_ID = "test.ottu.dev"
OTTU_AUTH = {
    "class": "ottu.auth.BasicAuth",
    "username": "dj_username",
    "password": "dj_password",
}
OTTU_WEBHOOK_URL = "https://test.client.dev/webhook-receiver/"
OTTU_WEBHOOK_KEY = "pu9MpX3yPR"
