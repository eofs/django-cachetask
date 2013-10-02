DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

INSTALLED_APPS = (
    'cachetask',
    'cachetask.tests.testapp',
)


SECRET_KEY = 'abcde12345'

# Celery broker
BROKER_URL = 'memory://'
