from fake_useragent import UserAgent
import re
from ..db_requests.update_job import deactivate_airtable_record
from ...utils.utils_parsing import get_url_content, check_active_job, get_date, get_levels, get_experience_number, get_element_text, has_integer_and_word_experience

PARENT_DIRECTORY_PATH = "data/new_production"
airtable_api_key = ''
airtable_table = ''
details_errors = []
jobs_deactivated_count = 0


def clean_salary(content):
    dollar_amounts = []
    matches = re.findall(r'\$[\d,.]+', content.text)
    for match in matches:
        # Remove commas and convert to float
        amount = int(float(match.replace(',', '').replace('$', '')))
        dollar_amounts.append(amount)

    # Print the first and second dollar amounts
    if len(dollar_amounts) >= 2:
        min_salary = dollar_amounts[0]
        max_salary = dollar_amounts[1]
    else:
        min_salary = None
        max_salary = None
    return(min_salary, max_salary)

def assign_field_values(content, headers, company_name):
    experience_requirements = content.find("div", id="jd-key-qualifications").find_all(string=lambda text: text and "experience" in text)
    cleaned_experience_requirements = []
    for requirement in experience_requirements:
        if has_integer_and_word_experience(requirement):
            # print("meets criteria", requirement)
            cleaned_experience_requirements.append(requirement)
    salary_content = content.find("div", id="accordion_pay&benefits")
    if salary_content:
        min_salary, max_salary = clean_salary(salary_content)
    else:
        min_salary = None
        max_salary = None
    return(min_salary, max_salary, cleaned_experience_requirements, True)

def fetch_job_details_with_retry(url, job_title, headers, company_name, run_log_file_path, max_retries=2):
    job = {

    }
    retries = 0
    custom_referer = "https://google.com"
    custom_referer2 = "https://linkedin.com/jobs"

    job_details_page_content = get_url_content(url, headers)
    if job_details_page_content:
        content = job_details_page_content.find("div", class_="job-details")
        if content:
            return(assign_field_values(job_details_page_content, headers, company_name))
        else:
            details_errors.append([job_title, url])
            return(None, None, None, False)
    else:
        print("Failed to get job_details page content")
        details_errors.append([job_title, url])
        # right now we just loop through until all errors are solved
        # log(run_log_file_path, f"Failed to get job details for Job ID: {job_id} from Company: {company_name}\n")
        return(None, None, None, False)

    




def scrape_job_details_apple(company_name, run_log_file_path, jobs_deactivated_count_in, new_jobs, jobs_to_inactivate):
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
        jobs_deactivated_count = deactivate_airtable_record(job_to_inactivate['id'], jobs_deactivated_count)
    for new_job in new_jobs:
        min_salary, max_salary, experience_requirements, is_scrape_successful = fetch_job_details_with_retry(new_job['job_url'], new_job['job_title'], hdr, new_job['company_name'], run_log_file_path)
        if is_scrape_successful:
            new_job["job_post_url"] = new_job['job_url']
            new_job["job_post_linkedin_url"] = None
            new_job["job_post_company_url"] = new_job['job_url']
            new_job["company_linked"] = new_job.pop('company_airtable_id')
            new_job["locations"] = [new_job["location"]]
            new_job["is_active"] = True
            new_job["min_salary"] = min_salary
            new_job["max_salary"] = max_salary
            new_job["posted_date"] = new_job['posted_date']
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
        if not "company_linked" in new_job:
            new_jobs.remove(new_job)
    return(jobs_deactivated_count, new_jobs)


