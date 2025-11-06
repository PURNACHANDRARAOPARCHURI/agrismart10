import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.conf import settings
from django.core.cache import cache

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

    # Read API key at call-time so a server restarted or freshly-set env var
    # becomes available without relying on module-level constants.
    owm_key = getattr(settings, 'OPENWEATHERMAP_API_KEY', '')
    if not owm_key:
        return (None, None)

    try:
        session = _requests_session_with_retries()
        # Use HTTPS for geocoding requests to avoid redirects or blocked HTTP access
        url = 'https://api.openweathermap.org/geo/1.0/direct'
        params = {'q': location, 'limit': 1, 'appid': owm_key}
        r = session.get(url, params=params, timeout=5)
        # If the service returns a non-200 status, log a small debug hint (no secrets)
        if not r.ok:
            try:
                print(f'geocode_location: OpenWeather geocode returned status {r.status_code} for q={location}')
            except Exception:
                pass
            return (None, None)
        data = r.json()
        if not data:
            # No geocoding results found for the query
            print(f'geocode_location: no results for q={location}')
            return (None, None)
        latlon = (data[0]['lat'], data[0]['lon'])
        cache.set(cache_key, latlon, timeout=60 * 60 * 24)  # cache 24h
        return latlon
    except Exception as exc:
        # Log the exception briefly for debugging (no API key printed)
        try:
            print(f'geocode_location: exception when geocoding "{location}": {type(exc).__name__} {str(exc)[:200]}')
        except Exception:
            pass
        return (None, None)


def fetch_short_forecast(lat, lon):
    """Fetch simple forecast (temp, humidity, rainfall) using OWM One Call API.
    Uses cache and retrying session. Returns dict with temperature, humidity, rainfall.
    Falls back to mocked values on failure or when no API key set.
    """
    # Read key at call-time to reflect any environment changes without module reload
    owm_key = getattr(settings, 'OPENWEATHERMAP_API_KEY', '')
    if lat is None or lon is None or not owm_key:
        # Return clearly-marked mocked values so frontend can surface that these
        # are sample/fallback values when the OpenWeatherMap API key is not set
        return {'temperature': 25.0, 'humidity': 70.0, 'rainfall': 50.0, 'mocked': True}

    cache_key = f'owm:{round(lat,4)}:{round(lon,4)}'
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        session = _requests_session_with_retries()
        url = 'https://api.openweathermap.org/data/2.5/onecall'
        params = {'lat': lat, 'lon': lon, 'exclude': 'minutely,hourly,alerts', 'units': 'metric', 'appid': owm_key}
        r = session.get(url, params=params, timeout=6)
        # If the provider returns a non-200, try a smaller 'current weather' endpoint
        if not r.ok:
            try:
                print(f'fetch_short_forecast: OpenWeather onecall returned status {r.status_code} for lat={lat},lon={lon} — attempting fallback to /data/2.5/weather')
            except Exception:
                pass
            # Attempt fallback to current weather endpoint which is available on most API plans
            try:
                weather_url = 'https://api.openweathermap.org/data/2.5/weather'
                weather_params = {'lat': lat, 'lon': lon, 'units': 'metric', 'appid': owm_key}
                wr = session.get(weather_url, params=weather_params, timeout=6)
                if wr.ok:
                    wdata = wr.json()
                    main = wdata.get('main', {})
                    temp = main.get('temp')
                    humidity = main.get('humidity')
                    rain = 0.0
                    # rain can be {'1h': x} or {'3h': x}
                    if isinstance(wdata.get('rain'), dict):
                        rain = wdata.get('rain').get('1h') or wdata.get('rain').get('3h') or 0.0
                    result = {'temperature': temp or 25.0, 'humidity': humidity or 70.0, 'rainfall': rain or 0.0, 'mocked': False, 'fallback': 'weather'}
                    cache.set(cache_key, result, timeout=60 * 30)
                    return result
                else:
                    try:
                        print(f'fetch_short_forecast: fallback /data/2.5/weather returned status {wr.status_code} for lat={lat},lon={lon}')
                    except Exception:
                        pass
                    return {'temperature': 25.0, 'humidity': 70.0, 'rainfall': 50.0, 'mocked': True}
            except Exception as exc:
                try:
                    print(f'fetch_short_forecast: fallback exception {type(exc).__name__} {str(exc)[:200]}')
                except Exception:
                    pass
                return {'temperature': 25.0, 'humidity': 70.0, 'rainfall': 50.0, 'mocked': True}
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
        result = {'temperature': temp or 25.0, 'humidity': humidity or 70.0, 'rainfall': rain or 0.0, 'mocked': False}
        cache.set(cache_key, result, timeout=60 * 30)  # cache 30 minutes
        return result
    except Exception as exc:
        try:
            print(f'fetch_short_forecast: exception {type(exc).__name__} {str(exc)[:200]}')
        except Exception:
            pass
        return {'temperature': 25.0, 'humidity': 70.0, 'rainfall': 50.0, 'mocked': True}
