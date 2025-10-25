#!/usr/bin/env python
"""
Utility script to run migrations and create a Django superuser in one process.

Usage (PowerShell):
  $env:DJANGO_SETTINGS_MODULE='agrigyaan_backend.settings';
  $env:DATABASE_URL='<your database url>';
  C:/path/to/python.exe backend/scripts/create_superuser.py

Be careful: do NOT commit credentials. This script reads DATABASE_URL from
the environment and uses Django's settings module to configure the DB.
"""
import os
import sys


def ensure_project_path():
    """Add the backend project directory to sys.path so Django settings can be imported.

    This script lives in backend/scripts. We want the backend folder (the parent of
    scripts/) to be on sys.path so 'import agrigyaan_backend' works regardless of
    the current working directory used to invoke the script.
    """
    this_file = os.path.abspath(__file__)
    scripts_dir = os.path.dirname(this_file)
    backend_dir = os.path.dirname(scripts_dir)
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)


if __name__ == '__main__':
    # Minimal environment checks
    settings_module = os.environ.get('DJANGO_SETTINGS_MODULE')
    if not settings_module:
        print('ERROR: DJANGO_SETTINGS_MODULE not set. Example: agrigyaan_backend.settings')
        sys.exit(2)
    if 'DATABASE_URL' not in os.environ:
        print('ERROR: DATABASE_URL environment variable not set.')
        sys.exit(2)

    # Make sure the backend package is importable
    ensure_project_path()

    # Defer Django imports until after env vars and sys.path are configured
    import django
    django.setup()

    from django.core.management import call_command
    from django.contrib.auth import get_user_model

    # Run migrations
    print('Running migrations...')
    call_command('migrate', '--noinput')

    # Create superuser
    User = get_user_model()
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

    if not password:
        print('ERROR: DJANGO_SUPERUSER_PASSWORD environment variable must be set for non-interactive creation.')
        sys.exit(2)

    if User.objects.filter(username=username).exists():
        print('Superuser already exists:', username)
        sys.exit(0)

    User.objects.create_superuser(username=username, email=email, password=password)
    print('Superuser created:', username)
