from fake_useragent import UserAgent
from ..db_requests.update_job import deactivate_airtable_record
from ..utils_parsing import assign_field_values, get_url_content, check_active_job, clean_salary, get_date, get_levels, get_experience_number

PARENT_DIRECTORY_PATH = "data/new_production"
airtable_api_key = ''
airtable_table = ''
details_errors = []
jobs_deactivated_count = 0


def fetch_job_details_with_retry(url, job_title, headers, company_name, run_log_file_path, max_retries=2):
    job = {

    }
    retries = 0
    custom_referer = "https://google.com"
    custom_referer2 = "https://linkedin.com/jobs"

    job_details_page_content = get_url_content(url, headers)
    if job_details_page_content:
        content = job_details_page_content.find("div", class_="description__text")
        if content:
            return(assign_field_values(job_details_page_content, headers, company_name))
        else:
            details_errors.append([job_title, url])
            return(None, None, None, None, None, None, False)
    else:
        print("Failed to get job_details page content")
        details_errors.append([job_title, url])
        # right now we just loop through until all errors are solved
        # log(run_log_file_path, f"Failed to get job details for Job ID: {job_id} from Company: {company_name}\n")
        return(None, None, None, None, None, None, False)

    




def scrape_job_details(company_name, run_log_file_path, jobs_deactivated_count_in, new_jobs, jobs_to_inactivate):
    global details_errors
    global jobs_deactivated_count
    jobs_deactivated_count = 0
    # Define headers with the custom referrer
    ua=UserAgent()
    hdr = {'User-Agent': ua.random,
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
      'Accept-Encoding': 'none',
      'Accept-Language': 'en-US,en;q=0.8',
      'Connection': 'keep-alive'}
    details_errors = []
    for job_to_inactivate in jobs_to_inactivate:
        is_job_active = check_active_job(job_to_inactivate['job_post_linkedin_url'], hdr)
        if not is_job_active:
            jobs_deactivated_count = deactivate_airtable_record(job_to_inactivate['id'], jobs_deactivated_count)
    for new_job in new_jobs:
        salary_range, description, posted_time_ago, experience_requirements, job_metadata, external_url, is_scrape_successful = fetch_job_details_with_retry(new_job['job_url'], new_job['job_title'], hdr, new_job['company_name'], run_log_file_path)
        if is_scrape_successful:
            if salary_range:
                min_salary, max_salary, pay_schedule = clean_salary(salary_range)
            else:
                min_salary = None
                max_salary = None
            if posted_time_ago:
                posted_date = get_date(posted_time_ago)
            else: 
                posted_date = None

            new_job["job_post_url"] = external_url if external_url else new_job['job_url']
            new_job["job_post_linkedin_url"] = new_job['job_url']
            new_job["job_post_company_url"] = external_url
            new_job["company_linked"] = new_job.pop('company_airtable_id')
            new_job["locations"] = [new_job["location"]]
            new_job["is_active"] = True
            new_job["min_salary"] = min_salary
            new_job["max_salary"] = max_salary
            new_job["posted_date"] = posted_date
            new_job["experience_desc"] = experience_requirements[0] if experience_requirements else None
            new_job["years_experience_req"] = get_experience_number(experience_requirements)
            new_job["level"] = get_levels(new_job["job_title"])
            del new_job["company_name"]
            del new_job["job_url"]
            del new_job["location"]
        else:
            print("Failed to add details to existing job, error scraping data")  
    # remove incomplete jobs
    for new_job in new_jobs[:]:
        if not "company_linked" in new_job or not 'job_post_linkedin_url' in new_job:
            new_jobs.remove(new_job)
    return(jobs_deactivated_count, new_jobs)


