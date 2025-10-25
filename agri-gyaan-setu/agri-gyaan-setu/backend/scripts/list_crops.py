#!/usr/bin/env python
"""List Crop rows for quick verification.

Run from backend directory with DJANGO_SETTINGS_MODULE and DATABASE_URL set.
"""
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrigyaan_backend.settings')
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    try:
        import django
        django.setup()
    except Exception as e:
        print('Django setup failed:', e)
        return

    from api.models import Crop
    qs = Crop.objects.all()
    print('Crop count:', qs.count())
    for c in qs:
        print(f'id={c.id} name={c.name} N={c.nitrogen} P={c.phosphorus} K={c.potassium}')

if __name__ == '__main__':
    main()
