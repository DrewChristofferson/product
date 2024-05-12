from ...utils.utils_selenium import open_selenium_driver, check_if_element_exists
from ...utils.utils_general import create_job_unique_code
from .identify_inactive_jobs import identify_inactive_jobs
import time
from selenium.webdriver.common.by import By


def parse_job_listing(job_listing, company_airtable_id, company_name):
    job_title = job_listing.find_element(By.CLASS_NAME, "table--advanced-search__title").text
    posted_date = job_listing.find_element(By.CLASS_NAME, "table--advanced-search__date").text
    company_airtable_id = company_airtable_id
    location = job_listing.find_element(By.CLASS_NAME, "table-col-2").text
    job_url = job_listing.find_element(By.CLASS_NAME, "table--advanced-search__title").get_attribute('href')
    job_id = create_job_unique_code([job_title, company_name, location])
    job = [job_id, job_title, company_name, company_airtable_id, location, job_url]
    job_formatted = {
        "job_id": job_id,
        "values": {
            "job_title": job_title,
            "company_name": company_name,
            "company_airtable_id": company_airtable_id,
            "location": location,
            "job_url": job_url,
            "is_active": True,
            "posted_date": posted_date
        }
    }
    return(job, job_formatted)

def get_company_page_jobs(company, browser, run_log_file_path, existing_company_jobs):
    postings_to_add = {}
    company_name = company['name']
    url = company['careers_page_url']
    company_airtable_id = company['airtable_id']
    open_selenium_driver(browser, url, company_name, run_log_file_path)
    time.sleep(2)

    jobs_exist = check_if_element_exists("class", browser, "results")
    if jobs_exist:
        time.sleep(2)
        job_listings = browser.find_elements(By.CSS_SELECTOR, "div.results tbody")
        for job_listing in job_listings:
            job, job_formatted = parse_job_listing(job_listing, company_airtable_id, company_name)
            if job[0] not in existing_company_jobs and "Product Manager" in job[1] and job[5]:
                postings_to_add[job_formatted["job_id"]] = job_formatted["values"]
        new_jobs, jobs_to_inactivate, company_airtable_reactivated_jobs_count = identify_inactive_jobs(existing_company_jobs, postings_to_add)
    # else:
    #     print("No jobs at this company")
    return(new_jobs, jobs_to_inactivate, company_airtable_reactivated_jobs_count)