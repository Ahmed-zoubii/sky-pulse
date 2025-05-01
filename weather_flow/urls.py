from django.urls import path

from .views import WeatherView, ForecastView, home

urlpatterns = [
    path(route='', view=home),
    path(route='weather/', view=WeatherView.as_view()),
    path(route='weather/forecast/', view=ForecastView.as_view()),
]