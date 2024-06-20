from .utils.set_airtable_configs import set_airtable_config
from pyairtable.formulas import match

def get_formatted_fields(job):
    fields =  {
        'id': job['id'], 
        'job_title': job["fields"]["job_title"], 
        'locations': job["fields"]["locations"], 
        'is_active': job["fields"]["is_active"] if 'is_active' in job["fields"] else False,
        'company_name': job["fields"]['company_name'], 
        'job_post_url': job["fields"]['job_post_url'], 
        'job_post_linkedin_url': job["fields"]['job_post_linkedin_url'] if 'job_post_linkedin_url' in job["fields"] else None,
        'job_post_company_url': job["fields"]['job_post_company_url'] if 'job_post_company_url' in job["fields"] else None,
        'experience_desc': job["fields"]['experience_desc'] if 'experience_desc' in job["fields"] else None,
        'years_experience_req': job["fields"]['years_experience_req'] if 'years_experience_req' in job["fields"] else None,
        'raw_jd_uploaded': job["fields"]['raw_jd_uploaded'] if 'raw_jd_uploaded' in job["fields"] else None,
        'job_details_added': job["fields"]['job_details_added'] if 'job_details_added' in job["fields"] else None,
        'job_details_xpath': job["fields"]['job_details_xpath'] if 'job_details_xpath' in job["fields"] else None,
        'preferred_qualifications': job["fields"]['preferred_qualifications'] if 'preferred_qualifications' in job["fields"] else None,
        'minimum_qualifications': job["fields"]['minimum_qualifications'] if 'minimum_qualifications' in job["fields"] else None,
        'job_responsibilities': job["fields"]['job_responsibilities'] if 'job_responsibilities' in job["fields"] else None
    }
    return(fields)

def get_airtable_jobs(company_name):
    formula = match({"company_name": company_name})
    airtable = set_airtable_config("jobs")
    response = airtable.all(formula=formula)
    return(response)

def pull_existing_jobs_for_company(company_name):
    all_existing_company_jobs = []
    response = get_airtable_jobs(company_name)
    for job in response:
        if 'is_active' in job["fields"]:
            all_existing_company_jobs.append(get_formatted_fields(job))

    return(all_existing_company_jobs)



def pull_jobs_without_details(company_name):
    all_existing_company_jobs = []
    response = get_airtable_jobs(company_name)
    for job in response:
        if 'is_active' in job["fields"] and 'job_details_added' not in job['fields']:
            all_existing_company_jobs.append(get_formatted_fields(job))
    return(all_existing_company_jobs)


# For main pipeline ----------------

def pull_all_jobs_for_company(company_name):
    all_existing_company_jobs = []
    response = get_airtable_jobs(company_name)
    for job in response:
        all_existing_company_jobs.append(get_formatted_fields(job))

    return(all_existing_company_jobs)