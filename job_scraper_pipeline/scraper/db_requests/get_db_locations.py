from .utils.set_db_configs import API_BASE_URL
import requests

def pull_all_locations():
    response = requests.get(f"{API_BASE_URL}/locations")
    locations = response.json()

    return(locations)

def location_find_first(city, state):
    response = requests.get(f"{API_BASE_URL}/locations?city={city}&state_abbr={state}&state_full={state}")
    location = response.json()[0] if response.status_code == 200 and response.json() else None

    return(location)
