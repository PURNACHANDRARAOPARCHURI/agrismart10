from .settings import *

# Use a fast in-memory SQLite database for tests to avoid external DB dependencies
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Use simple cache for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Tests will inherit logging from base settings; keep defaults to avoid errors here.
