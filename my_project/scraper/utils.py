import csv
import json
import hashlib
import requests
from lxml.html import fromstring
from itertools import cycle
import re
import os
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from pyairtable import Api
from pyairtable.formulas import match
from dotenv import load_dotenv


def set_airtable_config(table):
    # Load environment variables from .env file
    load_dotenv(".env")

    api_key = os.getenv("AIRTABLE_API_KEY")
    # print(api_key)

    airtable_api_key = Api(api_key)
    if table == 'companies':
        table_id = 'tblGwlPqq03yEQjV1'
    elif table == 'jobs':
        table_id = 'tbliHYwp5pTrRxqJk'
    else:
        table_id = None
    airtable_table = airtable_api_key.table('appT4TIFvWbwAQ35G', table_id)
    return(airtable_table)

def get_companies():
    all_companies = []
    airtable = set_airtable_config('companies')
    formula = match({"Name": "Cloudflare"})
    response = airtable.all(sort=["Name"], fields=["Name", "linkedin_id", "is_inactive", "Last Scrape Date"])
    for company in response:
        if 'linkedin_id' in company['fields'] and 'is_inactive' not in company['fields']:
            all_companies.append({
                "name": company['fields']['Name'],
                "linkedin_id": company['fields']['linkedin_id'],
                "airtable_id": company['id'],
                "Last Scrape Date": company['fields']['Last Scrape Date'] if 'Last Scrape Date' in company['fields'] else None
            })
        else:
            pass
            # print(f"removed {company['fields']['Name']}")
    return(all_companies)



def check_if_element_exists(type, html, criteria):
    try:
        if type == 'xpath':
            print("xpath searching")
        elif type == 'class':
            html.find_element(By.CLASS_NAME, criteria)
    except NoSuchElementException:
        return False
    return True

def determine_authwall(driver) -> bool:
    current_url = driver.current_url
    # print(current_url)
    if "/authwall" in current_url:
        return True
    elif "https://www.linkedin.com/" == current_url:
        return True
    elif check_if_element_exists("class", driver, "neterror"):
        return True
    else:
        return False

def detemine_job_listing_validity(job) -> bool:
    title_exists = check_if_element_exists("class", job, "base-search-card__title")
    company_exists = check_if_element_exists("class", job, "base-search-card__subtitle")
    location_exists = check_if_element_exists("class", job, "job-search-card__location")
    url_exists = check_if_element_exists("class", job, "base-card__full-link")

    if not (title_exists and company_exists and location_exists and url_exists):
        return False
    else:
        return True

def create_job_unique_code(job_details):
    list_str = ''.join(job_details)
    hash_code = hashlib.sha256(list_str.encode()).hexdigest()
    return hash_code

def write_to_csv(file_path_in, data):
    with open(file_path_in, mode='a', newline='') as file:
        # Write the results to the file
        writer = csv.writer(file)
        writer.writerows(data)

def write_to_json(file_path_in, data, company_name):
    with open(file_path_in, 'r') as file:
        json_data = json.load(file)

    for key, value in data.items():
        json_data[key] = value

    with open(file_path_in, "w") as file:
        json.dump(json_data, file, indent=4)

def write_to_txt(file_path_in, data):
    with open(file_path_in, "a") as file:
        # Write some text to the file
        file.write(data)

def has_integer_and_word_experience(string):
    pattern1 = r'\b\d+\b.*\bexperience\b'
    pattern2 = r'\b\d+\b.*\byears?\b'

    # Use re.search to find matches for both patterns
    match1 = re.search(pattern1, string)
    match2 = re.search(pattern2, string)

    # Return True if both are found, otherwise False
    return bool(match1) and bool(match2)

def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    print(response.text.strip())
    parser = fromstring(response.text)
    print(parser)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            #Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            print(proxy)
            proxies.add(proxy)
    return proxies

def get_experience_number(experience_reqs):
    first_job_experience = ''
    years = 0
    if experience_reqs:
        first_job_experience = experience_reqs[0]
        if first_job_experience and len(first_job_experience) < 300:
            cleaned_experience_string = clean_experience_string(first_job_experience)
            match = re.search(r'\d+', cleaned_experience_string)
            if match:
                years = match.group()
                years = int(years)
    else:
        years = None
    return(years)

def clean_experience_string(str):
    # Define a regular expression pattern to match a sequence of digits followed by a dot or a comma
    # Sometimes the experience requirements came from a list (e.g., 1. or 2,)
    pattern = r'\b\d+[.,]\s'
    pattern2 = r'Option\s\d+'
    
    # Use re.sub() to remove the pattern from the text
    str_no_list_numbers = re.sub(pattern, '', str)
    clean_text = re.sub(pattern2, '', str_no_list_numbers)
    
    return clean_text

def get_levels(job_title):
    level = ''
    job_title_lower_case = job_title.lower()
    if 'intern ' in job_title_lower_case or 'internship' in job_title_lower_case:
        level = 'Intern Product Manager'
    elif 'senior associate' in job_title_lower_case or 'sr associate' in job_title_lower_case:
        level = 'Senior Associate Product Manager'
    elif 'iii' in job_title_lower_case:
        level = 'Product Manager III'
    elif 'ii' in job_title_lower_case:
        level = 'Product Manager II'
    elif 'associate' in job_title_lower_case:
        level = 'Associate Product Manager'
    # elif 'technical' in job_title_lower_case:
    #     print("technical pm!", job_title)
    #     value['level'] = 'Technical'
    elif 'senior group' in job_title_lower_case or 'sr group' in job_title_lower_case:
        level = 'Senior Group Product Manager'
    elif 'senior staff' in job_title_lower_case or 'sr staff' in job_title_lower_case:
        level = 'Senior Staff Product Manager'
    elif 'senior principal' in job_title_lower_case or 'sr princical' in job_title_lower_case:
        level = 'Senior Principal Product Manager'
    elif 'senior lead' in job_title_lower_case or 'sr lead' in job_title_lower_case:
        level = 'Senior Lead Product Manager'
    elif 'principal' in job_title_lower_case:
        level = 'Principal Product Manager'
    elif 'lead' in job_title_lower_case:
        level = 'Lead Product Manager'
    elif 'staff' in job_title_lower_case:
        level = 'Staff Product Manager'
    elif 'group' in job_title_lower_case:
        level = 'Group Product Manager'
    elif 'senior' in job_title_lower_case or 'sr' in job_title_lower_case:
        level = 'Senior Product Manager'
    else:
        level = 'Product Manager'
    return(level)