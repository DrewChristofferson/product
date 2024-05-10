import time
from datetime import datetime, timedelta
from ..utils.logger import log
from .utils import detemine_job_listing_validity, check_if_element_exists, determine_authwall, create_job_unique_code, set_airtable_config
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

class AuthwallBlocker(Exception):
    pass

def reopen_job(job_id):
    airtable_table = set_airtable_config('jobs')
    response = airtable_table.update(
        job_id, 
        {
            "is_active": True, 
            "closed_date": None
        }, 
        typecast=True
    )

def identify_inactive_jobs(existing_jobs, postings_to_add):
    new_jobs = []
    jobs_to_inactivate = []
    reactivated_jobs_count = 0

    #identify new jobs
    for key, value in postings_to_add.items():
        job_found_in_existing = False
        posting_to_add_id = key
        posting_to_add_fields = value
        for existing_job in existing_jobs:
            # if posting_to_add_fields['job_title'] == existing_job['job_title']:
            #     print(posting_to_add_fields['company_name'], existing_job['company_name'])
            if posting_to_add_fields['job_title'] == existing_job['job_title'] and posting_to_add_fields['location'] in existing_job['locations'] and posting_to_add_fields['company_name'] == existing_job['company_name'][0]:
                if existing_job["is_active"] == False:
                    reopen_job(existing_job["id"])
                    reactivated_jobs_count += 1
                job_found_in_existing = True
        if job_found_in_existing == False:
            new_jobs.append(postings_to_add[posting_to_add_id])
            
    #identify inactive jobs
    for existing_job in existing_jobs:
        if existing_job["is_active"] == False:
            pass
        else:
            job_found_in_new_postings = False
            for key, value in postings_to_add.items():
                posting_to_add_id = key
                posting_to_add_fields = value
                if posting_to_add_fields['job_title'] == existing_job['job_title'] and posting_to_add_fields['location'] in existing_job['locations'] and posting_to_add_fields['company_name'] == existing_job['company_name'][0]:
                    job_found_in_new_postings = True
            if job_found_in_new_postings == False:
                jobs_to_inactivate.append(existing_job)

    # print(jobs_to_inactivate)
    return(new_jobs, jobs_to_inactivate, reactivated_jobs_count)

def parse_job_listing(job_listing, company_airtable_id, company_name):
    job_title = job_listing.find_element(By.CLASS_NAME, "base-search-card__title").text
    company_airtable_id = company_airtable_id
    location = job_listing.find_element(By.CLASS_NAME, "job-search-card__location").text
    job_url = job_listing.find_element(By.CLASS_NAME, "base-card__full-link").get_attribute('href')
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
        }
    }
    return(job, job_formatted)

def scroll_to_all_job_listings(browser):
    while True:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        browser.execute_script("window.scrollBy(0, -200);")
        try:
            element = WebDriverWait(browser, 2).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'inline-notification__text'))
            )
            break  # Exit the loop once the element is found
        except TimeoutException:
            pass

        try:
            element2 = WebDriverWait(browser, 1).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'infinite-scroller__show-more-button'))
            )
            element2.click()
            # print("Show more found!")
            # break  # Exit the loop once the element is found
        except TimeoutException:
            pass
        # print("Element not found, scrolling down...")

def open_selenium_driver(driver, url, company_name, run_log_file_path, max_retries=4, delay=1):
    retries = 0
    max_retries_reached = False
    while retries <= max_retries:
        try:
            # print(f'try: ', retries + 1)
            driver.get(url)
            time.sleep(1)
            has_authwall = determine_authwall(driver)
            if has_authwall and (max_retries - retries == 0):
                print("Max retries")
                max_retries_reached = True
                raise AuthwallBlocker(f"Reached max retries ({max_retries}) for fetching job listings for {company_name}")
            elif has_authwall and not max_retries_reached:
                # print(f"Authwall. Retries left: {max_retries - retries}")
                retries += 1
                time.sleep(4)
        except Exception as e:
            log(run_log_file_path, f'{e}\n')
        finally:
            if not has_authwall or max_retries_reached:
                return


def get_linkedin_jobs(company, browser, run_log_file_path, existing_company_jobs):
    global all_company_jobs_json
    global json_folder

    new_jobs = []
    jobs_to_inactivate = []
    company_jobs = []
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
        # write_to_json(json_folder, postings_to_add, company_name)
    # else:
    #     print("No jobs at this company")
    return(new_jobs, jobs_to_inactivate, company_airtable_reactivated_jobs_count)