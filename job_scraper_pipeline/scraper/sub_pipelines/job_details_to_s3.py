from ..db_requests.get_companies import pull_companies
from ..db_requests.get_jobs import pull_existing_jobs_for_company
from ..db_requests.update_job import update_job
from ...utils.utils_parsing import get_url_content
from ...utils.utils_selenium import set_up_selenium_browser
from ..s3.test import upload_txt_to_s3
from ..sub_pipelines.job_details_scraper_company import temp_fetch_job_details
from ..sub_pipelines.job_details_fields_to_airtable import get_job_posting_data
import time


def job_descriptions_to_s3(companies, browser):
    for company in companies:
        print(company['name'])
        jobs = pull_existing_jobs_for_company(company['name']) 
        for job in jobs:
            job_post_url = None
            html_classname = None
            xpath = None
            job_eligible = False
            if job['job_post_linkedin_url'] and job['raw_jd_uploaded'] is None:
                html_classname = "description__text"
                job_post_url = job['job_post_linkedin_url']
                job_eligible = True
            elif job['job_post_company_url'] and job['job_details_xpath'] and job['raw_jd_uploaded'] is None:
                xpath = job['job_details_xpath'][0]
                job_post_url = job['job_post_company_url']
                job_eligible = True
            else:
                print("S3 upload: insufficient url data or jd already uploaded")
            
            if job_eligible:
                try:
                    print("1", job_post_url, html_classname)
                    job_to_s3(job, job_post_url, html_classname, xpath, browser)
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
                else:
                    # Code to execute if no exceptions are raised
                    print("Successfully added jd to s3!")
                    update_job(job['id'], {'raw_jd_uploaded': True})
            
            #Send job details to Airtable
            time.sleep(1)
            if job['raw_jd_uploaded']:
                if not job['job_details_added']:
                    get_job_posting_data(job, company['name'])
                else:
                    print('job details already added')
            else:
                print('Airtable upload: no jd in s3 for this job or no linkedin url')


def job_to_s3(job, url, class_name=None, xpath=None, browser=None):
    print("here")
    if 'linkedin' in url:
        print("1", url, class_name)
        content = get_url_content(url)
        jd_content = content.find("div", class_=class_name)
        jd_text = jd_content.get_text().strip()
    else:
        jd_text = temp_fetch_job_details(url, xpath, browser)
    print(job['company_name'][0], job['id'])
    upload_txt_to_s3(job['company_name'][0], job['id'], jd_text)
    job['raw_jd_uploaded'] = True


