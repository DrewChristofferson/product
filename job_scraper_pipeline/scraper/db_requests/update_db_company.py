from .utils.set_db_configs import API_BASE_URL
import requests
from datetime import datetime

def log_company_scrape(company_id):
    print(datetime.today().strftime("%Y-%m-%d"))
    response = requests.put(f"{API_BASE_URL}/companies/{company_id}", json={"last_scrape_date": datetime.today().strftime("%Y-%m-%d")})
    if response.status_code == 200:
        return response.json()['id']
    else:
        print(f"Error updating company: {response.text}")
        return None