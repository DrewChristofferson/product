from ..db_requests.get_jobs import pull_existing_jobs_for_company
from ..db_requests.update_job import update_job
from ..s3.test import download_file_from_s3
from ..openai.test_openai import sythesize_job_posting_wrapper


def get_job_posting_data(job, company_name, *fields):
    content = download_file_from_s3(company_name, job['id']) 
    response = sythesize_job_posting_wrapper(content, company_name, job['job_title'], *fields)
    job_responsibilities_text = ""
    for i, responsibility in enumerate(response['job_responsibilities']):
        if i >=5:
            break
        job_responsibilities_text += f"{responsibility}. "
    response['job_responsibilities_text'] = job_responsibilities_text
    del response['job_responsibilities']

    response['job_details_added'] = True
    update_job(job['id'], response)