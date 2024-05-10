from datetime import datetime, timedelta
from .utils import create_job_unique_code, set_airtable_config
from .job_details_scraper import scrape_job_details
from .pull_existing_jobs import pull_existing_jobs_for_company
from .get_linkedin_jobs import get_linkedin_jobs
from .pull_companies import pull_companies
from ..utils.dedup import dedup_logic
from ..utils.logger import log
from ..utils.csv_to_airtable import update_company as update_airtable

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException


# we could eventually put these into a config file
RUN_TYPE = 'new_production'
CUSTOM_REFERER = "https://google.com"

class AuthwallBlocker(Exception):
    pass

def calc_start_time():
    start_datetime = datetime.now()
    start_time = start_datetime.replace(microsecond=0)
    run_log_file_path = f'data/{RUN_TYPE}/run-logs/{start_time}.txt'
    log(run_log_file_path, f'Started scraping jobs at {start_time}\n')
    return(start_datetime, run_log_file_path)

def set_up_selenium_browser():
    # Set up Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--referer=" + CUSTOM_REFERER)
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



def scrape_jobs():
    all_airtable_jobs_count = 0
    all_airtable_deactivated_jobs_count = 0
    all_airtable_reactivated_jobs_count = 0

    run_start_datetime, run_log_file_path = calc_start_time()
    companies = pull_companies()
    browser = set_up_selenium_browser()

    for a_company in companies:
        company_name = a_company['name']
        date_last_scraped = a_company['Last Scrape Date']
        company_airtable_id = a_company['airtable_id']
        company_airtable_jobs_count = 0
        company_airtable_deactivated_jobs_count = 0
        company_airtable_reactivated_jobs_count = 0

        two_days_ago = run_start_datetime - timedelta(days=2)
        two_days_ago = two_days_ago.strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")

        if today != date_last_scraped:
            # print(f'Now scraping for product jobs at {company_name}\n')
            #break out function to get existing jobs
            # create_data_dir(company_name)
            existing_jobs, active_existing_company_jobs = pull_existing_jobs_for_company(company_name)
            new_jobs, jobs_to_inactivate, company_airtable_reactivated_jobs_count = get_linkedin_jobs(a_company, browser, run_log_file_path, existing_jobs) 
            company_airtable_deactivated_jobs_count, new_jobs_full_details =  scrape_job_details(company_name, run_log_file_path, company_airtable_deactivated_jobs_count, new_jobs, jobs_to_inactivate)
            new_jobs_dedupped = dedup_logic(company_name, new_jobs_full_details, existing_jobs)
            company_airtable_jobs_count = update_airtable(company_name, new_jobs_dedupped)
            
            all_airtable_jobs_count += company_airtable_jobs_count
            all_airtable_deactivated_jobs_count += company_airtable_deactivated_jobs_count
            all_airtable_reactivated_jobs_count += company_airtable_reactivated_jobs_count


            log(run_log_file_path, f"{company_name}: {company_airtable_jobs_count} added | {company_airtable_deactivated_jobs_count} deactivated | {company_airtable_reactivated_jobs_count} reactivated \n")
            log_company_scrape(company_airtable_id)
        # else: 
        #     print(f"already scraped {company_name} recently")

    log(run_log_file_path,f"Count jobs added to airtable: {all_airtable_jobs_count} | Count jobs decativated on airtable: {all_airtable_deactivated_jobs_count} | Count jobs recativated on airtable: {all_airtable_reactivated_jobs_count}\n")
    browser.quit()