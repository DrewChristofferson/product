from ...utils.utils_selenium import open_selenium_driver, check_if_element_exists
from ...utils.utils_general import create_job_unique_code
from ..openai.test_openai import test_openai_jobs
from .identify_inactive_jobs import identify_inactive_jobs
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



# def parse_job_listing(job_listing, company_airtable_id, company_name):
#     job_title = job_listing.find_element(By.CLASS_NAME, "table--advanced-search__title").text
#     location = job_listing.find_element(By.CLASS_NAME, "table-col-2").text
#     job_url = job_listing.find_element(By.CLASS_NAME, "table--advanced-search__title").get_attribute('href')
#     # posted_date = job_listing.find_element(By.CLASS_NAME, "table--advanced-search__date").text
#     company_airtable_id = company_airtable_id

#     job_id = create_job_unique_code([job_title, company_name, location])
#     job = [job_id, job_title, company_name, company_airtable_id, location, job_url]
#     job_formatted = {
#         "job_id": job_id,
#         "values": {
#             "job_title": job_title,
#             "company_name": company_name,
#             "company_airtable_id": company_airtable_id,
#             "location": location,
#             "job_url": job_url,
#             "is_active": True
#         }
#     }
#     return(job, job_formatted)

def parse_job_listings(job_listings, company_airtable_id, company_name, existing_company_jobs, browser, title_html, url_html):
    job_listings_text = []
    output_list_of_job_postings = {}
    job_url = ""
    # todo: refactor this
    output_list_of_jobs = []
    company_airtable_id = company_airtable_id
    print(job_listings[0].get_attribute("innerHTML"))
    for job_listing in job_listings:
        # wait = WebDriverWait(browser, 10)
        # link_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "a")))
        try:
            if url_html:
                job_url_raw = job_listing.find_element(By.XPATH, url_html)
                job_url = job_url_raw.get_attribute("href")
                print(job_url)
            else:
                job_url = job_listing.get_attribute("href")

            if title_html:
                job_title_raw = job_listing.find_element(By.XPATH, title_html)
                job_title = job_title_raw.text
                print(job_title)
            else:
                job_title = job_listing.text

            
            # print(job_url)
            # Get the text content of the element and replace newline characters with a placeholder
        #     text_with_placeholder = job_listing.text.replace('\n', '|||')
        #     # Restore newline characters in the text
        #     text_with_newlines = text_with_placeholder.replace('|||', '\n')
        #     text_with_newlines += f'\n{job_url}'
        #     job_listings_text.append(text_with_newlines)
        # list_as_string = '; '.join(job_listings_text)
        # print(len(list_as_string))
        # if len(list_as_string) > 0:
        #     openai_response = test_openai_jobs(list_as_string)
        #     print(len(openai_response))
 
            # for job_listing in openai_response:
            # job_title = job_listing['job_title']
            # location = job_listing['location']
            # job_url = job_listing['job_url']
            temp_job_id = create_job_unique_code([job_title, company_name, job_url])
            # job = [job_id, job_title, company_name, company_airtable_id, location, job_url]
            job_formatted = {
                "job_id": temp_job_id,
                "values": {
                    "job_title": job_title,
                    "company_name": company_name,
                    "company_airtable_id": company_airtable_id,
                    "job_url": job_url,
                    "is_active": True
                }
            }
            # print(job_formatted)
            if "Product Manager" in job_title:
                # output_list_of_job_postings[job_formatted["job_id"]] = job_formatted["values"]
                output_list_of_jobs.append(job_formatted)
        except:
            pass
    return(output_list_of_jobs)

def get_more_jobs(browser, next_btn_class_name, container_html_class):
    try: #get next jobs, if exist
        next_button = browser.find_element(By.XPATH, next_btn_class_name)
        next_button.click()
        # time.sleep(2)
        WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, container_html_class))
        )
        time.sleep(4)
        return True
    except:
        return False


def get_company_page_jobs(company, browser, run_log_file_path, existing_company_jobs):
    IS_COMPANY_PAGE_SCRAPING = True
    num_pages = 1
    postings_to_add = {}
    list_of_job_postings = []
    company_name = company['name']
    url = company['careers_page_url']
    company_airtable_id = company['airtable_id']
    job_listings_xpath = company['job_listings_xpath']
    job_url_xpath = company['job_url_xpath']
    next_btn_xpath = company['next_btn_xpath']
    job_title_xpath = company['job_title_xpath']
    open_selenium_driver(browser, url, company_name, run_log_file_path)\

    # jobs_exist = check_if_element_exists("class", browser, container_html_class)
    WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.XPATH, job_listings_xpath))
    )
    time.sleep(4)
    # container = browser.find_element(By.CLASS_NAME, container_html_class)
        
    first_page = True
    next_button = None
    current_job_listings_on_page = None

    current_job_listings_on_page = browser.find_elements(By.XPATH, job_listings_xpath)
    current_job_listings_on_page_parsed = parse_job_listings(current_job_listings_on_page, company_airtable_id, company_name, existing_company_jobs, browser, job_title_xpath, job_url_xpath)
    list_of_job_postings.extend(current_job_listings_on_page_parsed)
    print("page 1: postings on page: ", len(current_job_listings_on_page), " product postings: ", len(current_job_listings_on_page_parsed), " total product postings: ", len(list_of_job_postings))
    if next_btn_xpath:
        more_jobs_exist = get_more_jobs(browser, next_btn_xpath, job_listings_xpath)
        while more_jobs_exist: #if there's more pages of jobs, keep iterating
            new_job_listings_on_page = browser.find_elements(By.XPATH, job_listings_xpath)
            new_job_listings_on_page_parsed = parse_job_listings(new_job_listings_on_page, company_airtable_id, company_name, existing_company_jobs, browser, job_title_xpath, job_url_xpath)
            # print("total", list_of_job_postings)
            
            if current_job_listings_on_page == new_job_listings_on_page:
                print("already been here")
                break
            else:  
                num_pages += 1
                print("page, ", num_pages, " 1: postings on page: ", len(new_job_listings_on_page), " product postings: ", len(new_job_listings_on_page_parsed), " total product postings: ", len(list_of_job_postings))
                list_of_job_postings.extend(new_job_listings_on_page_parsed)
                current_job_listings_on_page_parsed = []
                current_job_listings_on_page = new_job_listings_on_page
                new_job_listings_on_page = []
                new_job_listings_on_page_parsed = []
                more_jobs_exist = get_more_jobs(browser, next_btn_xpath, job_listings_xpath) #returns false if there's not a valid next button

    for job in list_of_job_postings:
        postings_to_add[job["job_id"]] = job["values"]
    new_jobs, jobs_to_inactivate, company_airtable_reactivated_jobs_count = identify_inactive_jobs(existing_company_jobs, postings_to_add, IS_COMPANY_PAGE_SCRAPING)
    # else:
    #     print("No jobs at this company")
    return(new_jobs, jobs_to_inactivate, company_airtable_reactivated_jobs_count)