from datetime import datetime, timedelta
from .utils.set_db_configs import API_BASE_URL  
import requests

def deactivate_record(job_id, jobs_deactivated_count):
    response = requests.put(
        f"{API_BASE_URL}/jobs/{job_id}", json={
            "is_active": False, 
            "closed_date": datetime.today().strftime("%m-%d-%Y")
        }
    )
    if response.status_code == 200:
        print(f"deactivated job {job_id}")
        jobs_deactivated_count += 1
        return(jobs_deactivated_count)
    else:
        print(f"Error deactivating job {job_id}: {response.text}")
        return None


def reopen_job(job_id, new_url):
    response = requests.put(f"{API_BASE_URL}/jobs/{job_id}", json={
        "is_active": True, 
        "closed_date": None,
        "job_post_url": new_url
    })
    if response.status_code == 200:
        print(f"reopened job {job_id}")
        return
    else:
        print(f"Error reopening job {job_id}: {response.text}")
        return

def add_loc_to_existing_job(new_location, existing_job):
    existing_job['job_locations'].append(new_location)
    response = requests.put(f"{API_BASE_URL}/jobs/{existing_job['id']}", json={
        'job_locations': existing_job['job_locations']
    },)
    if response.status_code == 200:
        print(f"added location for job {existing_job['id']}")
        return
    else:
        print(f"added location for job {existing_job['id']}: {response}")
        return

