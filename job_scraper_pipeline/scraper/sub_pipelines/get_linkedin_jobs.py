import time
from .identify_inactive_jobs import identify_inactive_jobs
from ...utils.utils_selenium import open_selenium_driver, scroll_to_all_job_listings, detemine_job_listing_validity, check_if_element_exists, close_popup_if_present
from ...utils.utils_parsing import parse_job_listing
from selenium.webdriver.common.by import By


def get_linkedin_jobs(company, browser, run_log_file_path, existing_company_jobs):
    new_jobs = []
    jobs_to_inactivate = []
    company_airtable_reactivated_jobs_count = 0
    postings_to_add = {}
    company_name = company['name']
    company_code = company['linkedin_id']
    company_airtable_id = company['airtable_id']

    url_job_list = f'https://www.linkedin.com/jobs/product-manager-jobs?keywords="Product%20Manager"&location=United%20States&locationId=&geoId=103644278&f_TPR=&f_C={company_code}&position=1&pageNum=0'
    open_selenium_driver(browser, url_job_list, company_name, run_log_file_path)
    time.sleep(2)
    
    
    jobs_exist = check_if_element_exists("class", browser, "base-card")
    if jobs_exist:
        scroll_to_all_job_listings(browser)
        time.sleep(2)
        job_listings = browser.find_elements(By.CLASS_NAME, "base-card")

        for job_listing in job_listings:
            job_listing_is_valid = detemine_job_listing_validity(job_listing)
            if job_listing_is_valid:
                job, job_formatted = parse_job_listing(job_listing, company_airtable_id, company_name)
                if job[0] not in existing_company_jobs and "Product Manager" in job[1] and job[5]:
                    postings_to_add[job_formatted["job_id"]] = job_formatted["values"]

    new_jobs, jobs_to_inactivate, company_airtable_reactivated_jobs_count = identify_inactive_jobs(existing_company_jobs, postings_to_add)
    # else:
    #     print("No jobs at this company")
    return(new_jobs, jobs_to_inactivate, company_airtable_reactivated_jobs_count)

