from .utils_general import create_job_unique_code
from datetime import datetime, timedelta
import pytz
import requests
from urllib.parse import unquote
import re
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from .get_location_id import get_location_id
from ..scraper.db_requests.get_db_levels import pull_all_levels



# Linkedin 'apply now' url are typically infused with a bunch of junk so we first try to make a request and get the url in the response
#However, some companies that already have clean urls have trouble getting the final url, so we have a hardcoded whitelist
COMPANIES_ON_URL_WHITELIST = [
    "Atlassian"
]
# Companies that have linkedin external links in the parameter of the url on link click
COMPANIES_URL_IN_PARAMETERS = [
    "Citi"
]
COMPANIES_SPLIT_APPLY = [
    "Confluent",
    "Nordstrom",
    "ServiceTitan",
    "Hinge Health",
    "Front",
    "Anthropic",
    "Stubhub",
    "Plaid"

]

def parse_job_listing_new(job_listing, company_id, company_name):
    job_title = job_listing.find_element(By.CLASS_NAME, "base-search-card__title").text
    company_id = company_id
    location = job_listing.find_element(By.CLASS_NAME, "job-search-card__location").text
    location_id = get_location_id(location)
    job_url = job_listing.find_element(By.CLASS_NAME, "base-card__full-link").get_attribute('href')
    job_id = create_job_unique_code([job_title, company_name, location])
    job_formatted = {
        "title": job_title,
        "company_name": company_name,
        "company_id": company_id,
        "location": location_id,
        "job_url": job_url,
        "is_active": True,
    }
    return(job_formatted)

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

def get_content_final_url(url, headers=None, max_retries=4):
    retries = 0
    if headers is None:
        ua=UserAgent()
        headers = {
            'User-Agent': ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'
        }
    while retries <= max_retries:
        try:
            retries += 1
            job_detail_page = requests.get(url, headers=headers)
            if job_detail_page.status_code == 200:
                return(job_detail_page.url)
            else:
                if max_retries == retries:
                    print("reached max retries")
                    return(None)
                time.sleep(1)
            
                
        except requests.RequestException as e:
            # Handle any exceptions that occur during the request
            print("Error: An error occurred during the job detail page:", e)

def get_url_content(url, headers=None, max_retries=4):
    retries = 0
    if headers is None:
        ua=UserAgent()
        headers = {
            'User-Agent': ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'
        }
    while retries <= max_retries:
        try:
            retries += 1
            job_detail_page = requests.get(url, headers=headers)
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
            if company_name in COMPANIES_URL_IN_PARAMETERS:
                request_url = get_parameter_url(request_url)
            request_url_clean = unquote(request_url)
            response = requests.get(request_url_clean, headers=headers)
            for key, value in response.headers.items():
                print(f"{key}: {value}")
            if response.status_code == 200:
                final_external_url = response.url
                # Workday urls insert '%5Cu002d' for a dash character. This code replaces it. 
                # final_external_url_dashes = final_external_url.replace("%5Cu002d", '-')
                final_external_url = replace_with_dashes(final_external_url)
                final_external_url_cleaned = unquote(final_external_url) 
                final_external_url_cleaned = replace_login_redirect(final_external_url_cleaned) 
                final_external_url_cleaned = replace_with_dashes(final_external_url_cleaned)   
                if company_name in COMPANIES_SPLIT_APPLY:
                    final_external_url_cleaned = remove_before_apply(final_external_url_cleaned)    
                return(final_external_url_cleaned)
            else:
                print("Error: Unexpected status code for external url:", response.status_code, request_url_clean)
                if company_name in COMPANIES_ON_URL_WHITELIST:
                    return(unquote(request_url))
            
        except requests.RequestException as e:
            # Handle any exceptions that occur during the request
            print("Error: An error occurred during the request for the external url:", e)
        
        retries += 1

    print("Max retries exceed to get URL")
    return None

def assign_field_values(content, headers, company_name):
    #TODO: refactor, the external url is dead code
    final_external_url = None
    description = get_element_text(content, "div", "description__text")
    posted_time_ago = get_element_text(content, "span", "posted-time-ago__text")
    # top_container = content.find(class_="top-card-layout__entity-info-container").find("icon")
    # if top_container is not None:
    #     external_url_code = content.find(id="applyUrl")
    #     if external_url_code:
    #         external_url = strip_external_url(external_url_code)
    #         final_external_url = get_external_url(external_url, headers, company_name)                        
    #     else:
    #         final_external_url = None
    # else:
    #     final_external_url = None
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

def get_hours_since_midnight():
    # Define the EST timezone
    est = pytz.timezone('US/Eastern')

    # Get the current time in EST
    current_time_est = datetime.now(est)

    # Get the midnight of the current day in EST
    midnight_est = current_time_est.replace(hour=0, minute=0, second=0, microsecond=0)

    # Calculate the difference between the current time and midnight
    time_difference = current_time_est - midnight_est

    # Get the number of hours since midnight
    hours_since_midnight = time_difference.total_seconds() / 3600

    return hours_since_midnight

def get_element_text(html, tag, class_name):
    if html.find(tag, class_=class_name):
        return html.find(tag, class_=class_name).text.strip()
    else:
        return None


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
    print("posted time ago", posted_time_ago)
    match = re.search(r'\d+', posted_time_ago)
    number_in_str = None
    if match:
        number_in_str = int(match.group())
            # day = 1, week = 2, month = 3
        if 'hour' in posted_time_ago or 'min' in posted_time_ago or 'sec' in posted_time_ago:
            if 'hour' in posted_time_ago:
                if number_in_str <= get_hours_since_midnight():
                    days_since = 0
                else:
                    days_since = 1
            else:
                days_since = 1
        elif 'day' in posted_time_ago:
            days_since = number_in_str
        elif 'week' in posted_time_ago:
            days_since = (number_in_str * 7)
        elif 'month' in posted_time_ago:
            days_since = (number_in_str * 30)
        else:
            return(None)

        calculated_date = datetime.today() - timedelta(days=days_since)
        formatted_date = calculated_date.strftime("%m-%d-%Y")
        print("formatted date", formatted_date)
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

def get_levels(job_title):
    level = ''
    job_title_lower_case = job_title.lower()
    if 'intern ' in job_title_lower_case or 'internship' in job_title_lower_case or 'associate product manager intern' in job_title_lower_case or 'apm intern' in job_title_lower_case:
        level = 'Intern Product Manager'
        level_id = 1
    elif 'senior associate' in job_title_lower_case or 'sr associate' in job_title_lower_case:
        level = 'Senior Associate Product Manager'
        level_id = 3
    elif 'iii' in job_title_lower_case:
        level = 'Product Manager III'
        level_id = 7
    elif 'ii' in job_title_lower_case:
        level = 'Product Manager II'
        level_id = 6
    elif 'associate' in job_title_lower_case:
        level = 'Associate Product Manager'
        level_id = 2
    elif 'senior group' in job_title_lower_case or 'sr group' in job_title_lower_case:
        level = 'Senior Group Product Manager'
        level_id = 12
    elif 'senior staff' in job_title_lower_case or 'sr staff' in job_title_lower_case:
        level = 'Senior Staff Product Manager'
        level_id = 15
    elif 'senior principal' in job_title_lower_case or 'sr princical' in job_title_lower_case:
        level = 'Senior Principal Product Manager'
        level_id = 13
    elif 'senior lead' in job_title_lower_case or 'sr lead' in job_title_lower_case:
        level = 'Senior Lead Product Manager'
        level_id = 14
    elif 'principal' in job_title_lower_case:
        level = 'Principal Product Manager'
        level_id = 11
    elif 'lead' in job_title_lower_case:
        level = 'Lead Product Manager'
        level_id = 9
    elif 'staff' in job_title_lower_case:
        level = 'Staff Product Manager'
        level_id = 19
    elif 'group' in job_title_lower_case:
        level = 'Group Product Manager'
        level_id = 10
    elif 'senior' in job_title_lower_case or 'sr' in job_title_lower_case:
        level = 'Senior Product Manager'
        level_id = 8
    else:
        level = 'Product Manager'
        level_id = 5
    return(level)

def get_level_id(job_title):
    levels = pull_all_levels()
    level = ''
    level_id = None
    job_title_lower_case = job_title.lower()
    if 'intern ' in job_title_lower_case or 'internship' in job_title_lower_case or 'associate product manager intern' in job_title_lower_case or 'apm intern' in job_title_lower_case:
        level = 'Intern Product Manager'
        level_id = 1
    elif 'senior associate' in job_title_lower_case or 'sr associate' in job_title_lower_case:
        level = 'Senior Associate Product Manager'
        level_id = 3
    elif 'iii' in job_title_lower_case:
        level = 'Product Manager III'
        level_id = 7
    elif 'ii' in job_title_lower_case:
        level = 'Product Manager II'
        level_id = 6
    elif 'associate' in job_title_lower_case:
        level = 'Associate Product Manager'
        level_id = 2
    elif 'vp' in job_title_lower_case or 'vice president' in job_title_lower_case:
        level = 'VP of Product'
        level_id = 17
    elif 'cpo' in job_title_lower_case or 'chief product' in job_title_lower_case:
        level = 'Chief Product Officer'
        level_id = 18
    elif 'director' in job_title_lower_case:
        level = 'Director of Product Management'
        level_id = 16
    elif 'senior group' in job_title_lower_case or 'sr group' in job_title_lower_case:
        level = 'Senior Group Product Manager'
        level_id = 12
    elif 'senior staff' in job_title_lower_case or 'sr staff' in job_title_lower_case:
        level = 'Senior Staff Product Manager'
        level_id = 15
    elif 'senior principal' in job_title_lower_case or 'sr princical' in job_title_lower_case:
        level = 'Senior Principal Product Manager'
        level_id = 13
    elif 'senior lead' in job_title_lower_case or 'sr lead' in job_title_lower_case:
        level = 'Senior Lead Product Manager'
        level_id = 14
    elif 'principal' in job_title_lower_case:
        level = 'Principal Product Manager'
        level_id = 11
    elif 'lead' in job_title_lower_case:
        level = 'Lead Product Manager'
        level_id = 9
    elif 'staff' in job_title_lower_case:
        level = 'Staff Product Manager'
        level_id = 19
    elif 'group' in job_title_lower_case:
        level = 'Group Product Manager'
        level_id = 10
    elif 'senior' in job_title_lower_case or 'sr' in job_title_lower_case:
        level = 'Senior Product Manager'
        level_id = 8
    else:
        level = 'Product Manager'
        level_id = 5
    return(level_id)

def get_sub_dept_id(job_title):
    job_title_lower_case = job_title.lower()
    sub_department_id = None
    if 'growth' in job_title_lower_case:
        sub_department_id = 1
    elif 'artificial intelligence' in job_title_lower_case or 'ai' in job_title_lower_case or 'machine learning' in job_title_lower_case or 'ml' in job_title_lower_case:
        sub_department_id = 4
    elif 'technical' in job_title_lower_case:
        sub_department_id = 2
    elif 'data' in job_title_lower_case:
        sub_department_id = 3
    return(sub_department_id)


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
                # now using string so I commented out the posting below
                # years = int(years)
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

def has_integer_and_word_experience(string):
    pattern1 = r'\b\d+\b.*\bexperience\b'
    pattern2 = r'\b\d+\b.*\byears?\b'

    # Use re.search to find matches for both patterns
    match1 = re.search(pattern1, string)
    match2 = re.search(pattern2, string)

    # Return True if both are found, otherwise False
    return bool(match1) and bool(match2)

def is_internship(title):
    title_lowercase = title.lower()
    if 'intern' in title_lowercase or 'internship' in title_lowercase:
        if 'international' not in title_lowercase:
            return True
        else:
            return False
    else:
        return False

def is_new_grad(title):
    title_lowercase = title.lower()
    if 'new grad' in title_lowercase or 'university grad' in title_lowercase or '2025' in title_lowercase or '2026' in title_lowercase:
        if 'intern' not in title_lowercase:
            return True
        else:
            return False
    else:
        return False