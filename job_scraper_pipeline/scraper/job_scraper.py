from datetime import datetime, timedelta
import time
from ..utils.utils_general import calc_start_time, log
from ..utils.utils_selenium import set_up_selenium_browser
from .sub_pipelines.job_details_scraper import scrape_job_details
from .sub_pipelines.job_details_scraper_company import scrape_job_details_company
from .sub_pipelines.get_company_page_jobs import get_company_page_jobs
from .db_requests.get_jobs import pull_all_jobs_for_company
from .sub_pipelines.get_linkedin_jobs import get_linkedin_jobs
from .db_requests.get_companies import pull_companies
from .sub_pipelines.dedup_jobs import dedup_jobs
from .db_requests.update_company import log_company_scrape
from .db_requests.create_jobs import create_new_jobs_batch as add_new_jobs
from .sub_pipelines.job_details_to_s3 import job_descriptions_to_s3
from .sub_pipelines.check_inactive_jobs import deactivate_old_jobs


def scrape_jobs(rerun_setting, company_name=None):
    all_airtable_jobs_count = 0
    all_airtable_deactivated_jobs_count = 0
    all_airtable_reactivated_jobs_count = 0
    run_log_file_path = None #Placeholder for if we want to send logs to a file

    run_start_datetime = calc_start_time(run_log_file_path)
    companies = pull_companies(company_name)
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

        if today != date_last_scraped or rerun_setting:
            #break out function to get existing jobs
            # create_data_dir(company_name)
            existing_jobs = pull_all_jobs_for_company(company_name)
            if not a_company['careers_page_url']:
                company_airtable_deactivated_jobs_count = deactivate_old_jobs(browser, existing_jobs, company_airtable_deactivated_jobs_count)
                new_jobs, jobs_to_inactivate, company_airtable_reactivated_jobs_count = get_linkedin_jobs(a_company, browser, run_log_file_path, existing_jobs) 
                company_airtable_deactivated_jobs_count, new_jobs_full_details =  scrape_job_details(company_name, run_log_file_path, company_airtable_deactivated_jobs_count, new_jobs, jobs_to_inactivate)

            elif a_company['careers_page_url']:
                new_jobs, jobs_to_inactivate, company_airtable_reactivated_jobs_count = get_company_page_jobs(a_company, browser, run_log_file_path, existing_jobs) 
                company_airtable_deactivated_jobs_count, new_jobs_full_details =  scrape_job_details_company(a_company, company_name, run_log_file_path, company_airtable_deactivated_jobs_count, new_jobs, jobs_to_inactivate, browser)


            new_jobs_dedupped = dedup_jobs(company_name, new_jobs_full_details, existing_jobs)
            company_airtable_jobs_count = add_new_jobs(new_jobs_dedupped)
            
            all_airtable_jobs_count += company_airtable_jobs_count
            all_airtable_deactivated_jobs_count += company_airtable_deactivated_jobs_count
            all_airtable_reactivated_jobs_count += company_airtable_reactivated_jobs_count


            log(run_log_file_path, f"{company_name}: {company_airtable_jobs_count} added | {company_airtable_deactivated_jobs_count} deactivated | {company_airtable_reactivated_jobs_count} reactivated \n")
            log_company_scrape(company_airtable_id)
        
    print("now updating job details")
    #send jds to s3 to extract details and update airtable records. TODO: refactor to get details earlier in the pipeline. Currectly depedent on airtable creating an ID. 
    job_descriptions_to_s3(companies, browser)

    log(run_log_file_path,f"Count jobs added to airtable: {all_airtable_jobs_count} | Count jobs decativated on airtable: {all_airtable_deactivated_jobs_count} | Count jobs recativated on airtable: {all_airtable_reactivated_jobs_count}\n")
    browser.quit()