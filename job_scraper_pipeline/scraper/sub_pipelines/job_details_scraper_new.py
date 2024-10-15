from fake_useragent import UserAgent
from ..db_requests.update_db_job import deactivate_record
from ...utils.utils_selenium import open_selenium_driver
from ...utils.utils_parsing import assign_field_values, get_url_content, check_active_job, clean_salary, get_date, get_level_id, get_experience_number, get_sub_dept_id, get_date, is_internship, is_new_grad
from .job_details_to_s3 import job_descriptions_to_s3
from ..openai.test_openai import test_openai, sythesize_job_posting_wrapper
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from ...utils.get_location_id import get_location_id


PARENT_DIRECTORY_PATH = "data/new_production"
airtable_api_key = ''
airtable_table = ''
details_errors = []

def join_qualifications(min_quals, pref_quals):
    joined_quals = []
    idx = 1
    for qual in min_quals:
        joined_quals.append({
            "text": qual,
            "is_preferred": False,
            "position_in_list": idx
        })
        idx += 1
    for qual in pref_quals:
        joined_quals.append({
            "text": qual,
            "is_preferred": True,
            "position_in_list": idx
        })
        idx += 1
    return joined_quals if joined_quals else None

def format_responsibilities(responsibilities):
    formatted_responsibilities = []
    idx = 1
    for resp in responsibilities:
        formatted_responsibilities.append({
            "text": resp,
            "position_in_list": idx
        })
        idx += 1

    return formatted_responsibilities if formatted_responsibilities else None

def fetch_job_details_with_retry(job_in, headers,run_log_file_path, browser, details_xpath, max_retries=2):

    retries = 0
    custom_referer = "https://google.com"
    custom_referer2 = "https://linkedin.com/jobs"
    posted_time_ago = None
    content = None 

    if details_xpath: #company page
        open_selenium_driver(browser, job_in['job_url'])
        content = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, details_xpath))
        )
    else: #linkedin
        job_details_page_content = get_url_content(job_in['job_url'], headers)
        content = job_details_page_content.find("div", class_="description__text")
        posted_time_ago = job_details_page_content.find("span", class_="posted-time-ago__text").text.strip()
    if content:
        try:
            job_details = sythesize_job_posting_wrapper(content.text, job_in['company_name'], job_in['title'])
            print('response', job_details)
            job = {}

            job['min_salary_range'] = job_details['min_base_salary'] if job_details['min_base_salary'] != 'null' else None
            job['max_salary_range'] = job_details['max_base_salary'] if job_details['max_base_salary'] != 'null' else None
            job['years_experience_required'] = job_details['years_experience_req'] if job_details['years_experience_req'] != 'null' else None
            if posted_time_ago: #linkedin
                job['posted_date'] = get_date(posted_time_ago) if posted_time_ago else None
            else:
                job['posted_date'] = job_details['posted_date'] if job_details['posted_date'] != 'null' else None
            if 'location' in job_in: #linkedin
                job['job_locations'] = [job_in['location']] 
            else: #company page
                location_ids = []
                for location in job_details['locations']:
                    location_ids.append(get_location_id(location))
                job['job_locations'] = location_ids
            job['is_remote_eligible'] = True if job_details['is_remote'] == 'YES' else False
            job['is_manager'] = True if job_details['is_people_manager'] == 'YES' else False
            # job['product_name'] = job_details['product_name'] if job_details['product_name'] != 'null' else None
            job['description'] = job_details['product_summary'] if job_details['product_summary'] != 'null' else None
            full_qualifications = join_qualifications(job_details['minimum_qualifications'],job_details['preferred_qualifications'])
            job['qualifications'] = full_qualifications
            # job['preferred_qualifications'] = job_details['preferred_qualifications'] if job_details['preferred_qualifications'] != 'null' else None
            # job['product_type'] = job_details['product_type'] if job_details['product_type'] != 'null' else None
            # job['is_equity_offered'] = job_details['is_equity_offered'] if job_details['is_equity_offered'] != 'null' else None
            job['responsibilities'] = format_responsibilities(job_details['job_responsibilities']) 
            # job['minimum_education_degree_level'] = job_details['minimum_education_degree_level'] if job_details['minimum_education_degree_level'] != 'null' else None
            # job['preferred_education_degree_level'] = job_details['preferred_education_degree_level'] if job_details['preferred_education_degree_level'] != 'null' else None
            # job['preferred_undergrad_field_of_study'] = job_details['preferred_undergrad_field_of_study'] if job_details['preferred_undergrad_field_of_study'] != 'null' else None
            # job['product_management_skills'] = job_details['product_management_skills'] if job_details['product_management_skills'] != 'null' else None
            # job['benefits'] = job_details['benefits'] if job_details['benefits'] != 'null' else None
            job['job_post_url'] = job_in['job_url']
            job['title'] = job_in['title']
            job['company_id'] = job_in['company_id']
            job['level_id'] = get_level_id(job_in['title'])
            job['department_id'] = 1 #hardcode to product for now
            job['sub_department_id'] = get_sub_dept_id(job_in['title'])
            job['is_internship'] = is_internship(job_in['title'])
            job['is_new_grad'] = is_new_grad(job_in['title'])
            job['is_active'] = True

            print(f"Successfully updated details for job id: {job_in['title']}!")
            return(job)
        except Exception as e:
            print(f"An unexpected error occurred updating job with job details field: {e}")
    else:
        print(f"No content")


    # job_details_page_content = get_url_content(url, headers)
    # if job_details_page_content:
    #     content = job_details_page_content.find("div", class_="description__text")
    #     if content:
    #         # TODO: refactor to send to s3 before creation
    #         # job_descriptions_to_s3(company_name, content)
    #         return(assign_field_values(job_details_page_content, headers, company_name))
    #     else:
    #         details_errors.append([job_title, url])
    #         return(None, None, None, None, None, None, False)
    # else:
    #     print("Failed to get job_details page content")
    #     details_errors.append([job_title, url])
    #     # right now we just loop through until all errors are solved
    #     # log(run_log_file_path, f"Failed to get job details for Job ID: {job_id} from Company: {company_name}\n")
    #     return(None, None, None, None, None, None, False)

    




def scrape_job_details(company_name, run_log_file_path, jobs_deactivated_count, new_jobs, jobs_to_inactivate, browser=None, details_xpath=None):
    global details_errors
    # Define headers with the custom referrer
    complete_new_jobs = []
    ua=UserAgent()
    hdr = {'User-Agent': ua.random,
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
      'Accept-Encoding': 'none',
      'Accept-Language': 'en-US,en;q=0.8',
      'Connection': 'keep-alive'}
    details_errors = []
    for job_to_inactivate in jobs_to_inactivate:
        is_job_active = check_active_job(job_to_inactivate['job_post_url'], hdr)
        if not is_job_active:
            jobs_deactivated_count = deactivate_record(job_to_inactivate['id'], jobs_deactivated_count)
    print('new jobs', new_jobs)
    for new_job in new_jobs:
        job_with_all_fields = fetch_job_details_with_retry(new_job, hdr, run_log_file_path, browser, details_xpath)
        if job_with_all_fields is not None:
            complete_new_jobs.append(job_with_all_fields)
        else:
            print('failed to get job details')
    # remove incomplete jobs
    print('complete new jobs', complete_new_jobs)
    for complete_new_job in complete_new_jobs[:]:
        if 'job_post_url' not in complete_new_job or 'posted_date' not in complete_new_job:
            complete_new_jobs.remove(complete_new_job)
            print('invalid job post url or posted date')
    return(jobs_deactivated_count, complete_new_jobs)


