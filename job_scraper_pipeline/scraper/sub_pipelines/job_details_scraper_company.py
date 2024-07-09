from fake_useragent import UserAgent
from ..openai.test_openai import test_openai
import re
import time
from selenium.webdriver.common.by import By
from ...utils.utils_selenium import open_selenium_driver, check_if_element_exists
from ..db_requests.update_job import deactivate_airtable_record
from ...utils.utils_parsing import get_url_content, check_active_job, get_date, get_levels, get_experience_number, get_element_text, has_integer_and_word_experience
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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


def temp_fetch_job_details(url, xpath, browser):
    open_selenium_driver(browser, url)
    content_raw = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )
    content_text = content_raw.text
    return(content_text)

def fetch_job_details_with_retry(url, job_title, headers, company_name, container_html_class, run_log_file_path, browser, max_retries=2):
    job = {

    }
    retries = 0
    custom_referer = "https://google.com"
    custom_referer2 = "https://linkedin.com/jobs"

    open_selenium_driver(browser, url, company_name, run_log_file_path)
    content_raw = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, container_html_class))
    )

    # job_details_page_content = check_if_element_exists("class", browser, container_html_class)
    # job_details_page_content = get_url_content(url, headers)
    # print(job_details_page_content)
    
    # content_raw = browser.find_element(By.XPATH, container_html_class)

    job_details = test_openai(content_raw.text)
    min_salary = job_details['min_salary'] if job_details['min_salary'] != 'null' else None
    max_salary = job_details['max_salary'] if job_details['max_salary'] != 'null' else None
    years_experience_req = job_details['years_experience_req'] if job_details['years_experience_req'] != 'null' else None
    posted_date = job_details['posted_date'] if job_details['posted_date'] != 'null' else None
    locations = job_details['locations'] if job_details['locations'] != 'null' else None

    return(min_salary, max_salary, years_experience_req, posted_date, locations, True)

    
    # else:
    #     details_errors.append([job_title, url])
    #     return(None, None, None, None, None, False)

    




def scrape_job_details_company(company, company_name, run_log_file_path, jobs_deactivated_count_in, new_jobs, jobs_to_inactivate, browser):
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
        min_salary, max_salary, years_experience_req, posted_date, locations, is_scrape_successful = fetch_job_details_with_retry(new_job['job_url'], new_job['job_title'], hdr, new_job['company_name'], company['job_details_xpath'], run_log_file_path, browser)
        if is_scrape_successful:
            new_job["job_post_url"] = new_job['job_url']
            new_job["job_post_linkedin_url"] = None
            new_job["job_post_company_url"] = new_job['job_url']
            new_job["company_linked"] = new_job.pop('company_airtable_id')
            new_job["locations"] = locations
            new_job["is_active"] = True
            # new_job["min_salary"] = min_salary
            # new_job["max_salary"] = max_salary
            new_job["posted_date"] = posted_date
            # new_job["summary"] = summary
            # new_job["experience_desc"] = experience_requirements[0] if experience_requirements else None
            new_job["years_experience_req"] = years_experience_req
            new_job["level"] = get_levels(new_job["job_title"])
            del new_job["company_name"]
            del new_job["job_url"]
        else:
            print("Failed to add details to existing job, error scraping data")  
    # remove incomplete jobs
    for new_job in new_jobs[:]:
        if not "company_linked" in new_job:
            new_jobs.remove(new_job)
    return(jobs_deactivated_count, new_jobs)


