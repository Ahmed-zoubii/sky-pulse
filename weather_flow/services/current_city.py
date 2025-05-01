import os

import requests


def get_current_city():
    return requests.get(
        url=f"https://ipinfo.io/json?token={os.environ['IPINFO_API_TOKEN']}",
        timeout=4
    ).json().get('city')

