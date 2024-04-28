from ..utils.company_mapping_2 import airtable_codes as airtable_ids
from ..scraper.utils import set_airtable_config
import json

def add_loc_to_existing_job(new_location, existing_job):
    airtable_table = set_airtable_config('jobs')
    existing_job['locations'].append(new_location)
    response = airtable_table.update(
        existing_job['id'],
        {
            'locations': existing_job['locations']
        },
        typecast=True
    )
    

def dedup_logic(company_name, new_jobs, existing_jobs):
    for job in new_jobs:
        print(job['locations'])
    # Determine whether any new jobs are duplicates with old jobs
    i = 0
    while i < len(new_jobs):
        new_job = new_jobs[i]
        for existing_job in existing_jobs:
            if (new_job['job_title'] == existing_job['job_title'] and
                new_job['experience_desc'] == existing_job['experience_desc'] and
                new_job['locations'][0] not in existing_job['locations']):
                
                add_loc_to_existing_job(new_job['locations'][0], existing_job)
                new_jobs.pop(i)
                print("dup for ", new_job['locations'][0])
                for job in new_jobs:
                    print(job['locations'])
                print(i)
                i -= 1  # Decrementing to stay at the same index after popping an element
                break  # Exit the inner loop once a match is found
        i += 1  # Move to the next index in the outer loop
    
    # Determine whether any new jobs are duplicates with each other
    for i, new_job1 in enumerate(new_jobs):
        for j, new_job2 in enumerate(new_jobs):
            if i != j and 'locations' in new_job1 and 'locations' in new_job2:
                if new_job1['job_title'] == new_job2['job_title'] and new_job1['experience_desc'] == new_job2['experience_desc']:
                    # Append location on to the current job if there's a match
                    new_job1['locations'].append(new_job2['locations'][0])
                    #delete the job, for which we just appended its location
                    new_jobs.pop(j)
    return(new_jobs)



def handle_duplicates():
    for key, value in airtable_ids.items():
        company_name = key
        skip_companies = ["assembly", "Assembly", "Aptos", "Apple", "X (formerly Twitter)", "Zip", "BFMeta"]
        # print(company_name)
        if company_name not in skip_companies:
            dedup_logic(company_name)