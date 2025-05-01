from datetime import datetime

from django.conf import settings
import requests
from rest_framework.exceptions import NotFound, APIException

from .current_city import get_current_city
from .forecasts import process_wind_direction

API_KEY = settings.WEATHER_API_KEY


def get_weather_data(city=None):
    city = city if city else get_current_city()

    try:
        response = requests.get(f'https://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}', timeout=5)
        weather_data = response.json()

        if 'error' in weather_data:
            message = weather_data['error'].get('message')
            raise NotFound(f"Location error: {message}")

        region = weather_data['location']['name']
        country = weather_data['location']['country']
        # extract current weather data
        current = weather_data['current']
        temp_c = current['temp_c']
        condition = current['condition']['text']
        icon = current['condition']['icon']
        feels_like_c = current['feelslike_c']
        humidity = current['humidity']
        wind_speed = current['wind_kph']
        wind_direction = current['wind_dir']
        pressure = current['pressure_mb']
        uv = weather_data['current']['uv']

        # Extract date and time part
        current_time = weather_data['location']['localtime']
        date_time = datetime.strptime(current_time, "%Y-%m-%d %H:%M")
        time_part = date_time.strftime("%H:%M")
        date_part = date_time.strftime("%A, %d %B")

        return {
            'region': f"{region}, {country}",
            'date': date_part,
            'time': time_part,
            'temp_c': f"{round(temp_c)}°C",
            'feelslike_c': f"{round(feels_like_c)}°C",
            'humidity': f"{humidity}%",
            'wind_speed': f"{round(wind_speed)}km/h",
            'wind_dir': process_wind_direction(wind_direction),
            'pressure': f"{round(pressure)}hPa",
            'uv': round(uv),
            'condition': condition,
            'icon': icon
        }

    except requests.RequestException:
        raise APIException("Weather service unreachable")
