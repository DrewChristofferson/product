from ..db_requests.get_jobs import pull_existing_jobs_for_company
from ..db_requests.update_job import update_job
from ..s3.test import download_file_from_s3
from ..openai.test_openai import sythesize_job_posting_wrapper


def get_job_posting_data(job, company_name, *fields):
    content = download_file_from_s3(company_name, job['id']) 
    response = sythesize_job_posting_wrapper(content, company_name, job['job_title'], *fields)
    job_responsibilities_text = ""
    min_qualifications_text = ""
    preferred_qualifications_text = ""
    if response['job_responsibilities']:
        for responsibility in response['job_responsibilities']:
            job_responsibilities_text += f"{responsibility}. "
    if response['minimum_qualifications']:
        for min_qual in response['minimum_qualifications']:
            min_qualifications_text += f"{min_qual}. "
    if response['preferred_qualifications']:
        for preferred_qual in response['preferred_qualifications']:
            preferred_qualifications_text += f"{preferred_qual}. "

    response['preferred_qualifications_text'] = preferred_qualifications_text
    response['min_qualifications_text'] = min_qualifications_text
    response['job_responsibilities_text'] = job_responsibilities_text
    if response['years_experience_req'] == "null":
        response['years_experience_req'] = None
    del response['preferred_qualifications']
    del response['minimum_qualifications']
    del response['job_responsibilities']

    response['job_details_added'] = True
    update_job(job['id'], response)


def ad_hoc_run(company_name, *fields):
    jobs = pull_existing_jobs_for_company(company_name) 
    for job in jobs:
        get_job_posting_data(job, company_name, *fields)