#!/usr/bin/env python
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE','agrigyaan_backend.settings')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import django
django.setup()

from api.models import ImportantDate

if ImportantDate.objects.filter(event_type='sowing').count()==0:
    ev = ImportantDate.objects.create(event_type='sowing', date='2025-10-25', notes='Sample sowing date (global)')
    print('Created sample event:', ev.id)
else:
    print('Sample sowing event already exists')
