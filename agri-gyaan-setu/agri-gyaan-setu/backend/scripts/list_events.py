#!/usr/bin/env python
"""List ImportantDate events for quick verification.

Usage: run this from the backend directory with DJANGO_SETTINGS_MODULE and DATABASE_URL set in the environment.
"""
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrigyaan_backend.settings')
    # ensure project path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    try:
        import django
        django.setup()
    except Exception as e:
        print('Failed to setup Django:', e)
        return

    from api.models import ImportantDate
    qs = ImportantDate.objects.all().order_by('-date')
    print('ImportantDate count:', qs.count())
    for ev in qs[:10]:
        print(f'id={ev.id} type={ev.event_type} date={ev.date} end={ev.end_date} recurrence={bool(ev.recurrence)} notes={ev.notes[:80]!r}')

if __name__ == '__main__':
    main()
