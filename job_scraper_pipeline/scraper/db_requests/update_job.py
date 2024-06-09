from datetime import datetime, timedelta
from .utils.set_airtable_configs import set_airtable_config

def deactivate_airtable_record(airtable_record_id, jobs_deactivated_count):
    airtable_table = set_airtable_config('jobs')
    response = airtable_table.update(
        airtable_record_id, 
        {
            "is_active": False, 
            "closed_date": datetime.today().strftime("%m-%d-%Y")
        }, 
        typecast=True
    )
    # is_airtable_record_is_active = True if "is_active" not in response["fields"] else False
    jobs_deactivated_count += 1
    return(jobs_deactivated_count)

def reopen_job(job_id, new_url):
    airtable_table = set_airtable_config('jobs')
    if 'linkedin' in new_url:
        response = airtable_table.update(
            job_id, 
            {
                "is_active": True, 
                "closed_date": None,
                "job_post_url": new_url,
                "job_post_linkedin_url": new_url
            }, 
            typecast=True
        )
    else:
        response = airtable_table.update(
            job_id, 
            {
                "is_active": True, 
                "closed_date": None,
                "job_post_url": new_url,
                "job_post_company_url": new_url

            }, 
            typecast=True
        )

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