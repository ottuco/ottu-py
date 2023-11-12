SECRET_KEY = "django-insecure"
DEBUG = True
ALLOWED_HOSTS = []
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "django.contrib.auth",
    "tests.test_ottu.test_contrib.test_django.polls",
    "ottu.contrib.django",
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

DJ_OTTU_MERCHANT_ID = "test.ottu.dev"
DJ_OTTU_AUTH_USERNAME = "dj_username"
DJ_OTTU_AUTH_PASSWORD = "dj_password"
DJ_OTTU_WEBHOOK_URL = "https://test.client.dev/webhook-receiver/"
DJ_OTTU_WEBHOOK_KEY = "pu9MpX3yPR"
