from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from .services import weather, forecasts, normalize_location

def home(request):
    return render(request, 'weather_flow/home.html')


class WeatherView(APIView):
    """
    API endpoint to get the current weather data.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='location',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Country or City Name',
                required=False,
            )
        ],
    )
    def get(self, request):
        # Retrieve the 'location' query parameter.
        location = request.GET.get('location', None)

        # Catch numeric input
        if location is not None and location.isdigit():
            raise ValidationError(
                "Invalid location: Numeric values are not allowed."
                "Please provide a city or country name."
            )
        if location:
            location = normalize_location.normalize_location(location)


        # Call the service function to get weather data.
        weather_data = weather.get_weather_data(location)
        return Response(data=weather_data, status=status.HTTP_200_OK)


class ForecastView(APIView):
    """
    API endpoint to get forecast and hourly forecast data.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='location',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Country or City Name',
                required=False,
            )
        ],
    )
    def get(self, request):
        # Retrieve the 'location' query parameter.
        location = request.GET.get('location', None)

        # Catch numeric input
        if location is not None and location.isdigit():
            raise ValidationError(
                "Invalid location: Numeric values are not allowed."
                "Please provide a city or country name."
            )
        if location:
            location = normalize_location.normalize_location(location)

        # Call the service functions for forecast and hourly forecast data.
        forecast_data = forecasts.get_forecast_data(location)
        hourly_forecast = forecasts.get_hourly_forecast(location)
        response_data = (
            forecast_data,
            hourly_forecast,
        )

        return Response(data=response_data, status=status.HTTP_200_OK)
