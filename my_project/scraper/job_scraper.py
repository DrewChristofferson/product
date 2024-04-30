import time
import json
from datetime import datetime, timedelta
import os
from ..old_files.company_mapping import linkedInCompanyCodes as l
from .utils import write_to_txt, detemine_job_listing_validity, check_if_element_exists, determine_authwall, create_job_unique_code, write_to_csv, write_to_json, get_companies, set_airtable_config
from .job_details_scraper import scrape_job_details
from ..utils.dedup import dedup_logic
from ..utils.logger import log
from ..utils.csv_to_airtable import update_company as update_airtable
from pyairtable.formulas import match

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException




import csv

RUN_TYPE = 'new_production'
csv_file_path = ''
csv_all_jobs = ''
overview_data_path = ''
json_folder = ''
custom_referer = "https://google.com"
all_company_jobs_json = {}
all_product_jobs = []
all_jobs = []
all_company_job_ids = []
existing_company_jobs = []
new_company_job_ids = []
company_job_count = []
count_jobs_in_search_results = 0
count_product_jobs = 0
count_other_jobs = 0
start_time = ''
run_log_file_path = ''

class AuthwallBlocker(Exception):
    pass

# def get_existing_job_ids(path, company_name):
#     global existing_company_jobs
#     # print(f'{path}/data/{company_name}.json')
#     with open(f'{path}/data/{company_name}.json', 'r') as file:
#         data = json.load(file)
#     for key, value in data.items():
#         if "is_active" in value and value["is_active"] == True:
#             all_company_job_ids.append(key)
#             existing_company_jobs.append(key)

def open_selenium_driver(driver, url, company_name, max_retries=4, delay=1):
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
                print(f"Authwall. Retries left: {max_retries - retries}")
                retries += 1
                time.sleep(4)
        except Exception as e:
            log(run_log_file_path, f'{e}\n')
        finally:
            if not has_authwall or max_retries_reached:
                return

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

# def create_data_dir(company_name):
#     #create new file directory for run data
#     global folder_directory 
#     global json_folder

#     current_datetime = datetime.now()
#     # Truncate the microseconds component
#     current_datetime_without_microseconds = current_datetime.replace(microsecond=0)
#     current_datetime_without_microseconds = '2024-03-06 21:49:12'
#     if RUN_TYPE == "production" or RUN_TYPE == "new_production":
#         folder_directory = f'data/{RUN_TYPE}'
#     else:
#         folder_directory = f'data/{RUN_TYPE}/{current_datetime_without_microseconds}'
#     if os.path.exists(f'{folder_directory}/data/{company_name}.json'):
#         pass
#         # get_existing_job_ids(folder_directory, company_name)
#     else:
#         with open(f'{folder_directory}/data/{company_name}.json', "w") as json_file:
#             json.dump({}, json_file, indent=4)

#     json_folder = f'{folder_directory}/data/{company_name}.json'

def identify_inactive_jobs(directory, existing_jobs, postings_to_add):
    new_jobs = []
    jobs_to_inactivate = []

    #identify new jobs
    for key, value in postings_to_add.items():
        job_found_in_existing = False
        posting_to_add_id = key
        posting_to_add_fields = value
        for existing_job in existing_jobs:
            # if posting_to_add_fields['job_title'] == existing_job['job_title']:
            #     print(posting_to_add_fields['company_name'], existing_job['company_name'])
            if posting_to_add_fields['job_title'] == existing_job['job_title'] and posting_to_add_fields['location'] in existing_job['locations'] and posting_to_add_fields['company_name'] == existing_job['company_name'][0]:
                job_found_in_existing = True
        if job_found_in_existing == False:
            new_jobs.append(postings_to_add[posting_to_add_id])
            
    #identify inactive jobs
    for existing_job in existing_jobs:
        job_found_in_new_postings = False
        for key, value in postings_to_add.items():
            posting_to_add_id = key
            posting_to_add_fields = value
            if posting_to_add_fields['job_title'] == existing_job['job_title'] and posting_to_add_fields['location'] in existing_job['locations'] and posting_to_add_fields['company_name'] == existing_job['company_name'][0]:
                #temp function to add linkedin_url
                if existing_job['job_post_linkedin_url'] == None and job_found_in_new_postings == False:
                    print('adding url', existing_job['job_post_linkedin_url'])
                    add_linkedin_url(existing_job['id'], posting_to_add_fields['job_url'], existing_job['job_post_url'])
                job_found_in_new_postings = True
        if job_found_in_new_postings == False:
            jobs_to_inactivate.append(existing_job)

    return(new_jobs, jobs_to_inactivate)

def add_linkedin_url(id, l_url, main_url):
    airtable = set_airtable_config('jobs')
    update = {}
    if 'www.linkedin.com' in main_url:
        update = {
            'job_post_linkedin_url': l_url,
        }
    else:
        update = {
            'job_post_linkedin_url': l_url,
            'job_post_company_url': main_url
        }
    airtable.update(
        id,
        update
    )

def get_jobs_for_company(company_name):
    global existing_company_jobs
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

def parse_job_listing(job_listing, company_airtable_id):
    job_title = job_listing.find_element(By.CLASS_NAME, "base-search-card__title").text
    company_name = job_listing.find_element(By.CLASS_NAME, "base-search-card__subtitle").text
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


def search_linkedin_for_jobs(company, browser):
    global all_company_jobs_json
    global existing_company_jobs
    global json_folder

    new_jobs = []
    jobs_to_inactivate = []
    company_jobs = []
    postings_to_add = {}
    company_name = company['name']
    company_code = company['linkedin_id']
    company_airtable_id = company['airtable_id']

    url_job_list = f'https://www.linkedin.com/jobs/product-manager-jobs?keywords="Product%20Manager"&location=United%20States&locationId=&geoId=103644278&f_TPR=&f_C={company_code}&position=1&pageNum=0'
    open_selenium_driver(browser, url_job_list, company_name)
    time.sleep(2)
    
    
    jobs_exist = check_if_element_exists("class", browser, "base-card")
    if jobs_exist:
        scroll_to_all_job_listings(browser)
        time.sleep(2)
        job_listings = browser.find_elements(By.CLASS_NAME, "base-card")

        for job_listing in job_listings:
            job_listing_is_valid = detemine_job_listing_validity(job_listing)
            if job_listing_is_valid:
                job, job_formatted = parse_job_listing(job_listing, company_airtable_id)
                if job[0] not in existing_company_jobs and "Product Manager" in job[1] and job[5]:
                    postings_to_add[job_formatted["job_id"]] = job_formatted["values"]

        new_jobs, jobs_to_inactivate = identify_inactive_jobs(json_folder, existing_company_jobs, postings_to_add)
        write_to_json(json_folder, postings_to_add, company_name)
    # else:
    #     print("No jobs at this company")
    return(new_jobs, jobs_to_inactivate)

def calc_start_time():
    global start_time
    global run_log_file_path
    start_datetime = datetime.now()
    start_time = start_datetime.strftime("%Y-%m-%d %H:%M:%S")
    start_time = start_datetime.replace(microsecond=0)
    run_log_file_path = f'data/{RUN_TYPE}/run-logs/{start_time}.txt'
    log(run_log_file_path, f'Started scraping jobs at {start_time}\n')
    return start_datetime

def set_up_selenium_browser():
    # Set up Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--referer=" + custom_referer)
    chrome_options.add_argument("--headless=new")
    # Instantiate the Chrome driver with the custom options
    browser = webdriver.Chrome(options=chrome_options)
    return browser

def log_company_scrape(airtable_company_id):
    airtable_table = set_airtable_config('companies')
    response = airtable_table.update(
        airtable_company_id, 
        {
            "Last Scrape Date": datetime.today().isoformat()
        }, 
        typecast=True
    )

def calc_run_duration(start, end):
    difference = end - start

    # Calculate total number of seconds in the difference
    total_seconds = difference.total_seconds()

    # Calculate hours, minutes, and seconds
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    # Format the difference as a string in the format "hours:minutes:seconds"
    formatted_difference = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    return(f"Total run duration (HH:MM:SS): {formatted_difference}")



def reset_counting_vars():
    global all_company_jobs_json
    global all_company_job_ids
    global existing_company_jobs

    existing_company_jobs = []
    all_company_job_ids = []
    all_company_jobs_json = {}

def configure_companies_to_run():
    airtable_companies = get_companies()
    midpoint = len(airtable_companies) // 2
    # Split the list into two halves
    first_half = airtable_companies[0]
    second_half = airtable_companies[midpoint:]
    single_company_test = airtable_companies[600:601]

    return single_company_test

    # print(airtable_companies[0], len(airtable_companies))

def scrape_jobs():
    global count_jobs_in_search_results
    global run_log_file_path
    all_airtable_jobs_count = 0
    all_airtable_deactivated_jobs_count = 0

    run_start_datetime = calc_start_time()
    companies = configure_companies_to_run()
    browser = set_up_selenium_browser()

    for a_company in companies:
        company_name = a_company['name']
        date_last_scraped = a_company['Last Scrape Date']
        company_airtable_id = a_company['airtable_id']
        company_airtable_jobs_count = 0
        company_airtable_deactivated_jobs_count = 0

        two_days_ago = run_start_datetime - timedelta(days=2)
        two_days_ago = two_days_ago.strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")

        if today != date_last_scraped:
            print(f'Now scraping for product jobs at {company_name}\n')
            reset_counting_vars()
            #break out function to get existing jobs
            # create_data_dir(company_name)
            existing_jobs = get_jobs_for_company(company_name)
            new_jobs, jobs_to_inactivate = search_linkedin_for_jobs(a_company, browser) 
            company_airtable_deactivated_jobs_count, new_jobs_full_details =  scrape_job_details(company_name, run_log_file_path, company_airtable_deactivated_jobs_count, new_jobs, jobs_to_inactivate)
            new_jobs_dedupped = dedup_logic(company_name, new_jobs_full_details, existing_jobs)
            company_airtable_jobs_count = update_airtable(company_name, new_jobs_dedupped)
            
            all_airtable_jobs_count += company_airtable_jobs_count
            all_airtable_deactivated_jobs_count += company_airtable_deactivated_jobs_count

            log(run_log_file_path, f"{company_name}: {company_airtable_jobs_count} added | {company_airtable_deactivated_jobs_count} deactivated \n")
            log_company_scrape(company_airtable_id)
        else:
            print(f"already scraped {company_name} recently")

    log(run_log_file_path,f"Count jobs added to airtable: {all_airtable_jobs_count} | Count jobs decativated on airtable: {all_airtable_deactivated_jobs_count} \n")
    log(run_log_file_path, f'Finished scraping jobs at {datetime.now().replace(microsecond=0)}\n')
    log(run_log_file_path, calc_run_duration(run_start_datetime, datetime.now()))
    browser.quit()