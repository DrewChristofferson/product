import time
from .identify_inactive_jobs_new import identify_inactive_jobs
from ...utils.utils_selenium import open_selenium_driver, scroll_to_all_job_listings, detemine_job_listing_validity, check_if_element_exists, close_popup_if_present
from ...utils.utils_parsing import parse_job_listing_new
from selenium.webdriver.common.by import By
from ...scraper.db_requests.get_db_locations import pull_all_locations


def get_linkedin_jobs(company, browser, run_log_file_path, existing_company_jobs):
    new_jobs = []
    jobs_to_inactivate = []
    company_reactivated_jobs_count = 0
    postings_to_add = []
    company_name = company['name']
    company_code = company['company_external_links']['linkedin_company_id']
    company_id = company['id']

    url_job_list = f'https://www.linkedin.com/jobs/product-manager-jobs?keywords="Product%20Manager"&location=United%20States&locationId=&geoId=103644278&f_TPR=&f_C={company_code}&position=1&pageNum=0'
    open_selenium_driver(browser, url_job_list, company_name, run_log_file_path)
    time.sleep(2)
    
    
    jobs_exist = check_if_element_exists("class", browser, "base-card")
    if jobs_exist:
        scroll_to_all_job_listings(browser)
        all_locations = pull_all_locations()
        time.sleep(2)
        job_listings = browser.find_elements(By.CLASS_NAME, "base-card")

        for job_listing in job_listings:
            job_listing_is_valid = detemine_job_listing_validity(job_listing)
            if job_listing_is_valid:
                job_formatted = parse_job_listing_new(job_listing, company_id, company_name) #new function
                if "Product Manager" in job_formatted["title"] and job_formatted["job_url"]:
                    postings_to_add.append(job_formatted)
    else:
        print("No jobs at this company")
    new_jobs, jobs_to_inactivate, company_reactivated_jobs_count = identify_inactive_jobs(existing_company_jobs, postings_to_add)
    return(new_jobs, jobs_to_inactivate, company_reactivated_jobs_count)

