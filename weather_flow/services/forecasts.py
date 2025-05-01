from datetime import datetime

from django.conf import settings
import requests
from rest_framework.exceptions import NotFound, APIException

from .current_city import get_current_city

API_KEY = settings.WEATHER_API_KEY


def get_forecast_data(city=None):
    city = city if city else get_current_city()
    base_url = f'https://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city}&days=6'

    try:
        response = requests.get(base_url, timeout=5)
        forecasts_data = response.json()

        if 'error' in forecasts_data:
            message = forecasts_data['error'].get('message')
            raise NotFound(f"Location error: {message}")

        region = forecasts_data['location']['name']
        country = forecasts_data['location']['country']

        sunrise = forecasts_data['forecast']['forecastday'][0]['astro']['sunrise']
        sunset = forecasts_data['forecast']['forecastday'][0]['astro']['sunset']

        coming_days_forecast = dict()
        for index, data in enumerate(forecasts_data['forecast']['forecastday']):
            if index > 0:
                date = datetime.strptime(data['date'], '%Y-%m-%d').strftime('%A, %d %B')
                coming_days_forecast[index] = (f"date: {date}", f"temp_c: {round(data['day']['avgtemp_c'])}°C",
                                               f"condition: {data['day']['condition']['text']}",
                                               f"icon: {data['day']['condition']['icon']}")

        return {
            'region': f"{region}, {country}",
            'sunrise': sunrise,
            'sunset': sunset,
            'coming_days_forecast': coming_days_forecast,
        }
    except requests.RequestException:
        raise APIException("Forecast service unreachable")


# Mapping dictionary
WIND_DIRECTION_MAP = {
    "N": "↑",
    "NNE": "↗",
    "NE": "↗",
    "ENE": "↗",
    "E": "→",
    "ESE": "↘",
    "SE": "↘",
    "SSE": "↘",
    "S": "↓",
    "SSW": "↙",
    "SW": "↙",
    "WSW": "↙",
    "W": "←",
    "WNW": "↖",
    "NW": "↖",
    "NNW": "↖"
}


def process_wind_direction(wind_dir):
    """Translate wind direction text to an arrow icon."""
    return WIND_DIRECTION_MAP.get(wind_dir, wind_dir)  # back to text if not found


def get_hourly_forecast(city=None):
    city = city if city else get_current_city()
    coming_hours = dict()
    base_url = f'https://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city}&days=2'

    try:
        response = requests.get(base_url, timeout=5)
        forecast_data = response.json()

        if 'error' in forecast_data:
            message = forecast_data['error'].get('message')
            raise NotFound(f"Location error: {message}")

        # Extract  Current Hour
        current_hour = int(datetime.strptime(forecast_data['location']['localtime'], '%Y-%m-%d %H:%M').strftime("%H"))

        def extract_coming_hours(day):
            for index, hour in enumerate(forecast_data['forecast']['forecastday'][day]['hour']):
                if (index > current_hour and day == 0) or day == 1:
                    coming_hour = datetime.strptime(hour['time'], '%Y-%m-%d %H:%M').strftime('%H:%M')

                    coming_hours[f"hour: {coming_hour}"] = (f"temp_c: {round(hour['temp_c'])}°C",
                                                            f"condition: {hour['condition']['text']}",
                                                            f"icon: {hour['condition']['icon']}",
                                                            f"wind_speed: {round(hour['wind_kph'])}km/h",
                                                            f"wind_direction: {process_wind_direction(hour['wind_dir'])}")

        for i in range(2):
            extract_coming_hours(i)

        coming_hours = dict(tuple(coming_hours.items())[2:15:3])
        return {'coming_hours_forecast': coming_hours}

    except requests.RequestException:
        raise APIException("Forecast service unreachable")
