import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.conf import settings
from django.core.cache import cache

OWM_KEY = getattr(settings, 'OPENWEATHERMAP_API_KEY', '')

# Configure a requests Session with retries/backoff
def _requests_session_with_retries(total_retries=2, backoff_factor=0.3):
    session = requests.Session()
    retries = Retry(total=total_retries, backoff_factor=backoff_factor,
                    status_forcelist=[429, 500, 502, 503, 504], allowed_methods=frozenset(['GET', 'POST']))
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    return session


def geocode_location(location):
    """Geocode a location string to (lat, lon) using cache + OWM geocoding when available."""
    if not location:
        return (None, None)
    cache_key = f'geocode:{location.lower()}'
    cached = cache.get(cache_key)
    if cached:
        return cached

    if not OWM_KEY:
        return (None, None)

    try:
        session = _requests_session_with_retries()
        url = 'http://api.openweathermap.org/geo/1.0/direct'
        params = {'q': location, 'limit': 1, 'appid': OWM_KEY}
        r = session.get(url, params=params, timeout=5)
        r.raise_for_status()
        data = r.json()
        if not data:
            return (None, None)
        latlon = (data[0]['lat'], data[0]['lon'])
        cache.set(cache_key, latlon, timeout=60 * 60 * 24)  # cache 24h
        return latlon
    except Exception:
        return (None, None)


def fetch_short_forecast(lat, lon):
    """Fetch simple forecast (temp, humidity, rainfall) using OWM One Call API.
    Uses cache and retrying session. Returns dict with temperature, humidity, rainfall.
    Falls back to mocked values on failure or when no API key set.
    """
    if lat is None or lon is None or not OWM_KEY:
        return {'temperature': 25.0, 'humidity': 70.0, 'rainfall': 50.0}

    cache_key = f'owm:{round(lat,4)}:{round(lon,4)}'
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        session = _requests_session_with_retries()
        url = 'https://api.openweathermap.org/data/2.5/onecall'
        params = {'lat': lat, 'lon': lon, 'exclude': 'minutely,hourly,alerts', 'units': 'metric', 'appid': OWM_KEY}
        r = session.get(url, params=params, timeout=6)
        r.raise_for_status()
        data = r.json()
        current = data.get('current', {})
        daily = data.get('daily', [])
        temp = current.get('temp')
        humidity = current.get('humidity')
        rain = 0.0
        if 'rain' in current:
            rain = current.get('rain', 0.0)
        elif daily and isinstance(daily, list) and 'rain' in daily[0]:
            rain = daily[0].get('rain', 0.0)
        result = {'temperature': temp or 25.0, 'humidity': humidity or 70.0, 'rainfall': rain or 0.0}
        cache.set(cache_key, result, timeout=60 * 30)  # cache 30 minutes
        return result
    except Exception:
        return {'temperature': 25.0, 'humidity': 70.0, 'rainfall': 50.0}
