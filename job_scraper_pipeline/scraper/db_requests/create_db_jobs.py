import requests
from .utils.set_db_configs import API_BASE_URL


#pull locations
def create_new_jobs_batch(new_jobs):
    count_jobs_created = 0
    for job in new_jobs:
        print('job: ', job)
        for i, location in enumerate(job['job_locations']):
            if location is None:
                job['job_locations'].pop(i)

        response = requests.post(f"{API_BASE_URL}/jobs", json=job)
        if response.status_code == 201:
            count_jobs_created += 1
        else:
            print(f"Error creating job: {response.text}")
    return count_jobs_created