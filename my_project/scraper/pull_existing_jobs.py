from pyairtable.formulas import match
from .utils import set_airtable_config


def pull_existing_jobs_for_company(company_name):
    existing_company_jobs = []
    formula = match({"company_name": company_name, "is_active": True})
    airtable = set_airtable_config("jobs")
    response = airtable.all(formula=formula)
    for job in response:
        existing_company_jobs.append({
            'id': job['id'], 
            'job_title': job["fields"]["job_title"], 
            'locations': job["fields"]["locations"], 
            'company_name': job["fields"]['company_name'], 
            'job_post_url': job["fields"]['job_post_url'], 
            'job_post_linkedin_url': job["fields"]['job_post_linkedin_url'] if 'job_post_linkedin_url' in job["fields"] else None,
            'experience_desc': job["fields"]['experience_desc'] if 'experience_desc' in job["fields"] else None
        })
    return(existing_company_jobs)