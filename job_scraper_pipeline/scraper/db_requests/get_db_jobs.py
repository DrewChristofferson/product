from .utils.set_db_configs import API_BASE_URL
import requests

def pull_all_jobs_for_company(company_id):
    response = requests.get(f"{API_BASE_URL}/jobs", params={
        'company_id': company_id,
        'per_page': 1000
    })
    jobs = response.json()['jobs']['jobs']
    return(jobs)

