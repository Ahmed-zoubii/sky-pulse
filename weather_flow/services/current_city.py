from django.conf import settings

import requests


def get_current_city():
    return requests.get(
        url=f"https://ipinfo.io/json?token={settings.IPINFO_API_TOKEN}",
        timeout=4
    ).json().get('city')

