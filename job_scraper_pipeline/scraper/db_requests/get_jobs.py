from .utils.set_airtable_configs import set_airtable_config
from pyairtable.formulas import match


def pull_existing_jobs_for_company(company_name):
    all_existing_company_jobs = []
    formula = match({"company_name": company_name})
    airtable = set_airtable_config("jobs")
    response = airtable.all(formula=formula)
    for job in response:
        all_existing_company_jobs.append({
            'id': job['id'], 
            'job_title': job["fields"]["job_title"], 
            'locations': job["fields"]["locations"], 
            'is_active': job["fields"]["is_active"] if 'is_active' in job["fields"] else False, 
            'company_name': job["fields"]['company_name'], 
            'job_post_url': job["fields"]['job_post_url'], 
            'job_post_linkedin_url': job["fields"]['job_post_linkedin_url'] if 'job_post_linkedin_url' in job["fields"] else None,
            'experience_desc': job["fields"]['experience_desc'] if 'experience_desc' in job["fields"] else None
        })

    return(all_existing_company_jobs)
