import requests
from .utils.set_db_configs import API_BASE_URL

def pull_companies(companies_filter_id=None):
    all_companies = []
    if companies_filter_id:
        response = requests.get(f"{API_BASE_URL}/companies/{companies_filter_id}?is_active=true")
        all_companies.append(response.json())
    else:
        response = requests.get(f"{API_BASE_URL}/companies?is_active=true")
        all_companies = response.json()
    return all_companies