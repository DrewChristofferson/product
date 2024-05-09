import os
import json
import random
from fake_useragent import UserAgent
from datetime import datetime, timedelta
import requests
from pyairtable import Api
from dotenv import load_dotenv
from selenium import webdriver
from urllib.parse import unquote
import re
import time
from bs4 import BeautifulSoup
from .utils import has_integer_and_word_experience, write_to_json, check_if_element_exists, get_levels, get_experience_number, get_companies, set_airtable_config
from ..old_files.company_mapping import linkedInCompanyCodes as l
from ..utils.logger import log

PARENT_DIRECTORY_PATH = "data/new_production"
airtable_api_key = ''
airtable_table = ''
details_errors = []
jobs_deactivated_count = 0
# Linkedin 'apply now' url are typically infused with a bunch of junk so we first try to make a request and get the url in the response
#However, some companies that already have clean urls have trouble getting the final url, so we have a hardcoded whitelist
companies_on_url_whitelist = [
    "Atlassian"
]
# Companies that have linkedin external links in the parameter of the url on link click
companies_url_in_parameters = [
    "Citi"
]
companies_split_apply = [
    "Confluent",
    "Nordstrom",
    "ServiceTitan",
    "Hinge Health",
    "Front",
    "Anthropic",
    "Stubhub",
    "Plaid"

]

# def set_airtable_vars():
#     global airtable_api_key
#     global airtable_table
#     # Load environment variables from .env file
#     load_dotenv("".env")

#     api_key = os.getenv("AIRTABLE_API_KEY")
#     # print(api_key)

#     airtable_api_key = Api(api_key)
#     airtable_table = airtable_api_key.table('appT4TIFvWbwAQ35G', 'tbliHYwp5pTrRxqJk')

def get_url_content(url, headers, max_retries=4):
    retries = 0
    while retries <= max_retries:
        try:
            retries += 1
            job_detail_page = requests.get(url)
            # time.sleep(random.uniform(1,3))
            # Check if the request was successful (status code 200)
            if job_detail_page.status_code == 200:
                # Process the response data
                soup = BeautifulSoup(job_detail_page.content, "html.parser")
                return(soup)
            else:
                if max_retries == retries:
                    print("reached max retries")
                    return(None)
            
                
        except requests.RequestException as e:
            # Handle any exceptions that occur during the request
            print("Error: An error occurred during the job detail page:", e)



def strip_external_url(external_url_code):
    external_url_code_stripped = external_url_code.contents[0].strip('<!-->').strip()
    start_index = external_url_code_stripped.find('?url=') + len('?url=')
    url_part = external_url_code_stripped[start_index:]
    end_index = url_part.find('&urlHash')
    cleaned_url = url_part[:end_index]
    modified_url = cleaned_url.replace('%2F', '/').replace('%3A', ':').replace('%2E', '.').replace('%3D', '=').replace('%3F', '?').replace('%26', '&')
    # modified_url = clean_meta_url(modified_url)
    return(modified_url)

def get_parameter_url(url):
    match = re.search(r'https://[^?]+\?', url)
    if match:
        filler_url = match.group(0)
        actual_url = url.split(filler_url, 1)[1]
        return(actual_url)

def remove_before_apply(url):
    url_parts = url.split('apply', 1)
    return(url_parts[0])

def replace_with_dashes(url):
    url_with_dashes = url.replace("%5Cu002d", '-')
    return(url_with_dashes)

def replace_login_redirect(url):
    pattern = r'login\?redirect=/[^/]+/'
    return(re.sub(pattern, '', url))

def get_external_url(request_url, headers, company_name, max_retries=2):
    retries = 0
    while retries <= max_retries:
        try:
            retries += 1
            if company_name in companies_url_in_parameters:
                request_url = get_parameter_url(request_url)
            request_url_clean = unquote(request_url)
            response = requests.get(request_url_clean, headers=headers)
            if response.status_code == 200:
                final_external_url = response.url
                # Workday urls insert '%5Cu002d' for a dash character. This code replaces it. 
                # final_external_url_dashes = final_external_url.replace("%5Cu002d", '-')
                final_external_url = replace_with_dashes(final_external_url)
                final_external_url_cleaned = unquote(final_external_url) 
                final_external_url_cleaned = replace_login_redirect(final_external_url_cleaned) 
                final_external_url_cleaned = replace_with_dashes(final_external_url_cleaned)   
                if company_name in companies_split_apply:
                    final_external_url_cleaned = remove_before_apply(final_external_url_cleaned)    
                return(final_external_url_cleaned)
            else:
                print("Error: Unexpected status code for external url:", response.status_code)
                if company_name in companies_on_url_whitelist:
                    return(unquote(request_url))
            
        except requests.RequestException as e:
            # Handle any exceptions that occur during the request
            print("Error: An error occurred during the request for the external url:", e)

def assign_field_values(content, headers, company_name):
    description = get_element_text(content, "div", "description__text")
    posted_time_ago = get_element_text(content, "span", "posted-time-ago__text")
    top_container = content.find(class_="top-card-layout__entity-info-container").find("icon")
    if top_container is not None:
        external_url_code = content.find(id="applyUrl")
        if external_url_code:
            external_url = strip_external_url(external_url_code)
            final_external_url = get_external_url(external_url, headers, company_name)                        
        else:
            final_external_url = None
    else:
        final_external_url = None
    # Find job summary and criteria details
    criteria_details = content.find_all("li", class_="description__job-criteria-item")
    job_metadata = []
    for section in criteria_details:
        section_details = [phrase.strip() for phrase in section.text.split('\n\n')]
        job_metadata.append(section_details[1:])
    # print(len(job_metadata), job_metadata)
    experience_requirements = content.find("div", "description__text").find_all(string=lambda text: text and "experience" in text)
    cleaned_experience_requirements = []
    for requirement in experience_requirements:
        if has_integer_and_word_experience(requirement):
            # print("meets criteria", requirement)
            cleaned_experience_requirements.append(requirement)
    if content.find("div", class_="salary"):
        salary = content.find("div", class_="salary").text.strip()
    else:
        salary = None
    return(salary, description, posted_time_ago, cleaned_experience_requirements, job_metadata, final_external_url, True)

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

    

def get_element_text(html, tag, class_name):
    if html.find(tag, class_=class_name):
        return html.find(tag, class_=class_name).text.strip()
    else:
        return None


# 

def clean_salary(salary_range):
    if 'yr' in salary_range:
        salary_values = salary_range.split('/yr - $')
        pay_schedule = 'Salary'
    elif 'hr' in salary_range:
        salary_values = salary_range.split('/hr - $')
        pay_schedule = 'Hourly'
    else:
        return(None, None)
    min_salary = (salary_values[0])[1:]
    min_salary = int(float(min_salary.replace(',', '')))
    max_salary = (salary_values[1])[:-3]
    max_salary = int(float(max_salary.replace(',', '')))
    return(min_salary, max_salary, pay_schedule)

def get_date(posted_time_ago):
    match = re.search(r'\d+', posted_time_ago)
    number_in_str = None
    if match:
        number_in_str = int(match.group())
            # day = 1, week = 2, month = 3
        if 'hour' in posted_time_ago or 'min' in posted_time_ago or 'sec' in posted_time_ago:
            days_since = 1
        elif 'day' in posted_time_ago:
            days_since = number_in_str + 1
        elif 'week' in posted_time_ago:
            days_since = (number_in_str * 7) + 1
        elif 'month' in posted_time_ago:
            days_since = (number_in_str * 30) + 1
        else:
            return(None)

        calculated_date = datetime.today() - timedelta(days=days_since)
        formatted_date = calculated_date.strftime("%m-%d-%Y")
        return(formatted_date)
    else:
        return(None)
    


def check_active_job(url, headers):
    job_details_page_content = get_url_content(url, headers)
    if job_details_page_content:
        apply_button = job_details_page_content.find("button", class_="top-card-layout__cta")
        return(apply_button)
    else:
        return None

def deactivate_airtable_record(airtable_record_id):
    global jobs_deactivated_count 
    airtable_table = set_airtable_config('jobs')
    response = airtable_table.update(
        airtable_record_id, 
        {
            "is_active": False, 
            "closed_date": datetime.today().strftime("%m-%d-%Y")
        }, 
        typecast=True
    )
    # is_airtable_record_is_active = True if "is_active" not in response["fields"] else False
    jobs_deactivated_count += 1


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
    # json_file_path, details_errors_path = fetch_most_recent_data()
    json_file_path = f"data/new_production/data/{company_name}.json"
    details_errors_path = "data/new_production/data/errors.json"
    # with open(json_file_path, 'r') as file:
    #     data = json.load(file)
    # initial_run = True
    # while details_errors or initial_run:
    #     #set initial_company_execution to false for remaining re-runs needed
    #     initial_run = False
    details_errors = []
    for job_to_inactivate in jobs_to_inactivate:
        is_job_active = check_active_job(job_to_inactivate['job_post_linkedin_url'], hdr)
        # print(is_job_active)
        # print(is_closed_job_posting, value["is_active"], value["job_closed_date"])
        if not is_job_active:
            # value["is_active"] = False
            # value["job_closed_date"] = datetime.today().strftime("%m-%d-%Y")
            deactivate_airtable_record(job_to_inactivate['id'])
    for new_job in new_jobs:
        salary_range, description, posted_time_ago, experience_requirements, job_metadata, external_url, is_scrape_successful = fetch_job_details_with_retry(new_job['job_url'], new_job['job_title'], hdr, new_job['company_name'], run_log_file_path)
        if is_scrape_successful:
            if salary_range:
                min_salary, max_salary, pay_schedule = clean_salary(salary_range)
            else:
                min_salary = None
                max_salary = None
                pay_schedule = None
            if posted_time_ago:
                posted_date = get_date(posted_time_ago)
            else: 
                posted_date = None
            # check to see whether the job posting is actually still open. If so, make active and nullify the closed date.

            # new_job["is_scrape_done"] = is_scrape_successful
            new_job["job_post_url"] = external_url if external_url else new_job['job_url']
            #change the name of this upstream
            new_job["job_post_linkedin_url"] = new_job['job_url']
            new_job["job_post_company_url"] = external_url
            new_job["company_linked"] = new_job.pop('company_airtable_id')
            #need to dedup instead of this hack
            new_job["locations"] = [new_job["location"]]
            new_job["is_active"] = True
            new_job["min_salary"] = min_salary
            new_job["max_salary"] = max_salary
            # new_job["pay_schedule"] = pay_schedule
            # new_job["description"] = description
            new_job["posted_date"] = posted_date
            new_job["experience_desc"] = experience_requirements[0] if experience_requirements else None
            new_job["years_experience_req"] = get_experience_number(experience_requirements)
            new_job["level"] = get_levels(new_job["job_title"])
            del new_job["company_name"]
            del new_job["job_url"]
            del new_job["location"]
            # new_job["waiting_for_job_details_run"] = False
            # if job_metadata:
            #     for metadata_section in job_metadata:
            #         new_job[metadata_section[0]] = metadata_section[1]
        else:
            print("Failed to add details to existing job, error scraping data")  
    # remove incomplete jobs
    for new_job in new_jobs[:]:
        if not "company_linked" in new_job or not 'job_post_linkedin_url' in new_job:
            new_jobs.remove(new_job)

        # for key, value in data.items():
        #     job_id = key
        #     job_url = value["job_url"]
        #     yesterday = datetime.now() - timedelta(days=1)
        #     formatted_yesterday = yesterday.strftime('%m-%d-%Y')
        #     formatted_today = datetime.now().strftime('%m-%d-%Y')
        #     # if 'job_closed_date' in value and (value["job_closed_date"] == formatted_yesterday or value["job_closed_date"] == formatted_today):
        #     # if 'airtable_id' in value and jobs_not_found and job_id in jobs_not_found:
        #     #             is_job_active = check_active_job(job_url, hdr)
        #     #             # print(is_job_active)
        #     #             # print(is_closed_job_posting, value["is_active"], value["job_closed_date"])
        #     #             if not is_job_active:
        #     #                 value["is_active"] = False
        #     #                 value["job_closed_date"] = datetime.today().strftime("%m-%d-%Y")
        #     #                 deactivate_airtable_record(value['airtable_id'])
        #     #                 print(f"Set job listing {id} as inactive.")

        #     if 'is_scrape_done' not in data[job_id] or data[job_id].get('is_scrape_done') is False:
        #     # if 'is_scrape_done' in data[job_id]:
        #         pass
        #     # print(data)
        #     else:
        #         print("already done")
    # write_to_json(json_file_path, data, company_name)
    return(jobs_deactivated_count, new_jobs)


def scrape_details():
    airtable_companies = get_companies()
    for a_company in airtable_companies:
        company_name = a_company['name']
        company_code = a_company['linkedin_id']
        company_airtable_id = a_company['airtable_id']
        scrape_job_details(company_name)

