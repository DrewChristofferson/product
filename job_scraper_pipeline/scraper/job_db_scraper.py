from datetime import datetime, timedelta
import time
from ..utils.utils_general import calc_start_time, log
from ..utils.utils_selenium import set_up_selenium_browser
from .sub_pipelines.job_details_scraper_new import scrape_job_details
from .sub_pipelines.job_details_scraper_company_new import scrape_job_details_company
from .sub_pipelines.get_company_page_jobs_new import get_company_page_jobs
from .sub_pipelines.get_linkedin_jobs_new import get_linkedin_jobs
from .sub_pipelines.dedup_jobs_new import dedup_jobs
from .sub_pipelines.job_details_to_s3 import job_descriptions_to_s3
from .sub_pipelines.check_inactive_jobs_new import deactivate_old_jobs
from .db_requests.get_db_jobs import pull_all_jobs_for_company
from .db_requests.get_db_companies import pull_companies
from .db_requests.update_db_company import log_company_scrape
from .db_requests.create_db_jobs import create_new_jobs_batch as add_new_jobs


def scrape_db_jobs(rerun_setting, company_id=None):
    all_jobs_count = 0
    all_deactivated_jobs_count = 0
    all_reactivated_jobs_count = 0
    run_log_file_path = None #Placeholder for if we want to send logs to a file

    run_start_datetime = calc_start_time(run_log_file_path)
    companies = pull_companies(company_id)
    browser = set_up_selenium_browser()

    for c in companies:
        company_name = c['name']
        print(f"Scraping jobs for {company_name}")
        date_last_scraped = c['company_scraping_data']['last_scrape_date']
        # Parse the string into a datetime object
        if date_last_scraped:
            date_last_scraped_object = datetime.strptime(date_last_scraped, "%Y-%m-%d").date()
        else:
            date_last_scraped_object = None

        company_id = c['id']
        company_jobs_count = 0
        company_deactivated_jobs_count = 0
        company_reactivated_jobs_count = 0

        two_days_ago = run_start_datetime - timedelta(days=2)
        two_days_ago = two_days_ago.strftime("%Y-%m-%d")
        today = datetime.now().date()

        if today != date_last_scraped_object or rerun_setting:
            #break out function to get existing jobs
            # create_data_dir(company_name)
            existing_jobs = pull_all_jobs_for_company(company_id)
            if not c['company_scraping_data']['scrape_url']: #LinkedIn
                company_deactivated_jobs_count = deactivate_old_jobs(browser, existing_jobs, company_deactivated_jobs_count)
                new_jobs, jobs_to_inactivate, company_reactivated_jobs_count = get_linkedin_jobs(c, browser, run_log_file_path, existing_jobs) 
                company_deactivated_jobs_count, new_jobs_full_details =  scrape_job_details(company_name, run_log_file_path, company_deactivated_jobs_count, new_jobs, jobs_to_inactivate)

            elif c['company_scraping_data']['scrape_url']: #Company Pages
                new_jobs, jobs_to_inactivate, company_reactivated_jobs_count = get_company_page_jobs(c, browser, run_log_file_path, existing_jobs)
                company_deactivated_jobs_count, new_jobs_full_details =  scrape_job_details(company_name, run_log_file_path, company_deactivated_jobs_count, new_jobs, jobs_to_inactivate, browser, c['company_scraping_data']['job_details_xpath'])

            #try with company pages
            new_jobs_dedupped = dedup_jobs(company_name, new_jobs_full_details, existing_jobs)
            print(new_jobs_dedupped)
            company_jobs_count = add_new_jobs(new_jobs_dedupped)
            
            all_jobs_count += company_jobs_count
            all_deactivated_jobs_count += company_deactivated_jobs_count
            all_reactivated_jobs_count += company_reactivated_jobs_count


            log(run_log_file_path, f"{company_name}: {company_jobs_count} added | {company_deactivated_jobs_count} deactivated | {company_reactivated_jobs_count} reactivated \n")
            log_company_scrape(company_id)
        
    print("now updating job details")
    #send jds to s3 to extract details and update  records. TODO: refactor to get details earlier in the pipeline. Currectly depedent on airtable creating an ID. 
    # job_descriptions_to_s3(companies, browser)

    log(run_log_file_path,f"Count jobs added: {all_jobs_count} | Count jobs decativated: {all_deactivated_jobs_count} | Count jobs recativated: {all_reactivated_jobs_count}\n")
    browser.quit()