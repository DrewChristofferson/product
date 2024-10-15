from .utils.set_db_configs import API_BASE_URL
import requests

def pull_all_levels():
    response = requests.get(f"{API_BASE_URL}/levels?per_page=100")
    levels = response.json()

    return(levels)


