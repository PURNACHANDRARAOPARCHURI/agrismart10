#!/usr/bin/env python3
"""Small helper to validate DATABASE_URL connectivity from the project environment.

Run from the backend folder:
  python scripts/check_db.py

This will attempt to connect using psycopg2 and print a short result. It will not
print the database password but will show host/port/database and the error message
if the connection fails.
"""
import os
import sys
from urllib.parse import urlparse

try:
    import psycopg2
except Exception as e:
    print('ERROR: psycopg2 not available. Install requirements with:')
    print('  python -m pip install -r requirements.txt')
    raise


def mask_url(url):
    try:
        p = urlparse(url)
        user = p.username or ''
        host = p.hostname or ''
        port = p.port or 5432
        db = p.path[1:] if p.path and p.path.startswith('/') else p.path
        return f'{user}@{host}:{port}/{db}'
    except Exception:
        return url


def main():
    url = os.environ.get('DATABASE_URL') or os.environ.get('DATABASE_URL'.upper())
    if not url:
        print('DATABASE_URL environment variable is not set.')
        print('Set it in PowerShell like:')
        print("$env:DATABASE_URL = 'postgresql://user:pass@host/db?sslmode=require'")
        sys.exit(2)

    print('Checking DB connectivity for:', mask_url(url))

    # Quick hint about common problematic params
    if 'channel_binding' in url:
        print('Note: connection string contains channel_binding parameter — if your client/libpq is old this may fail.')

    try:
        conn = psycopg2.connect(dsn=url, connect_timeout=6)
        cur = conn.cursor()
        cur.execute('SELECT version()')
        ver = cur.fetchone()
        print('Connected OK — Postgres version:', ver[0] if ver else 'unknown')
        cur.close()
        conn.close()
        sys.exit(0)
    except Exception as e:
        print('Connection failed:')
        print(type(e).__name__ + ':', str(e))
        # Common diagnostic hints
        print('\nDiagnostics hints:')
        print('- Ensure network connectivity to the host (Test-NetConnection on PowerShell).')
        print("  Example: Test-NetConnection -ComputerName <host> -Port 5432")
        print("- If you see SSL or channel binding errors, try removing channel_binding param for a quick test (but check Neon docs before removing permanently).")
        print("- Ensure your local libpq/psycopg2 is up-to-date; on Windows reinstalling psycopg2-binary or Postgres client can help.")
        sys.exit(3)


if __name__ == '__main__':
    main()
