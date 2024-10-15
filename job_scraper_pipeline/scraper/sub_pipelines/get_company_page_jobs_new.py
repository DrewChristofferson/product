from ...utils.utils_selenium import open_selenium_driver, check_if_element_exists
from ...utils.utils_general import create_job_unique_code
from .identify_inactive_jobs_new import identify_inactive_jobs
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException




def parse_job_listings(job_listings, company_id, company_name, existing_company_jobs, browser, title_html, url_html):
    # todo: refactor this
    output_list_of_jobs = []
    company_id = company_id
    for job_listing in job_listings:
        job_url = ""
        job_title = ""
        try:
            if url_html:
                job_url_raw = job_listing.find_element(By.XPATH, url_html)
                job_url = job_url_raw.get_attribute("href")
            else:
                job_url = job_listing.get_attribute("href")
        except Exception as e:
            print("Failed to get url in listings", e)

        try:
            if title_html:
                job_title_raw = job_listing.find_element(By.XPATH, title_html)
                job_title = job_title_raw.text
                # print(job_title)
            else:
                job_title = job_listing.text
        except Exception as e:
            print("Failed to get job_title in listings", e)

        job_formatted = {
            "title": job_title,
            "company_name": company_name,
            "company_id": company_id,
            "job_url": job_url,
            "is_active": True
        }
        if "Product Manager" in job_title:
            output_list_of_jobs.append(job_formatted)
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
    postings_to_add = []
    list_of_job_postings = []
    new_jobs = []
    jobs_to_inactivate = []
    company_reactivated_jobs_count = 0
    company_name = company['name']
    url = company['company_scraping_data']['scrape_url']
    company_id = company['id']
    job_listings_xpath = company['company_scraping_data']['job_listings_xpath']
    job_url_xpath = company['company_scraping_data']['job_url_xpath']
    next_btn_xpath = company['company_scraping_data']['next_btn_xpath']
    job_title_xpath = company['company_scraping_data']['job_title_xpath']
    open_selenium_driver(browser, url, company_name, run_log_file_path)

    is_job_listings = None
    try:
        is_job_listings = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, job_listings_xpath))
        )
    except TimeoutException as e:
        pass
    time.sleep(4)
        

    if is_job_listings:
        current_job_listings_on_page = browser.find_elements(By.XPATH, job_listings_xpath)
        current_job_listings_on_page_parsed = parse_job_listings(current_job_listings_on_page, company_id, company_name, existing_company_jobs, browser, job_title_xpath, job_url_xpath)
        list_of_job_postings.extend(current_job_listings_on_page_parsed)
        if next_btn_xpath:
            more_jobs_exist = get_more_jobs(browser, next_btn_xpath, job_listings_xpath)
            while more_jobs_exist: #if there's more pages of jobs, keep iterating
                new_job_listings_on_page = browser.find_elements(By.XPATH, job_listings_xpath)
                new_job_listings_on_page_parsed = parse_job_listings(new_job_listings_on_page, company_id, company_name, existing_company_jobs, browser, job_title_xpath, job_url_xpath)
                
                if current_job_listings_on_page == new_job_listings_on_page:
                    break
                else:  
                    num_pages += 1
                    list_of_job_postings.extend(new_job_listings_on_page_parsed)
                    current_job_listings_on_page_parsed = []
                    current_job_listings_on_page = new_job_listings_on_page
                    new_job_listings_on_page = []
                    new_job_listings_on_page_parsed = []
                    more_jobs_exist = get_more_jobs(browser, next_btn_xpath, job_listings_xpath) #returns false if there's not a valid next button

        for job in list_of_job_postings:
            postings_to_add.append(job)
    new_jobs, jobs_to_inactivate, company_reactivated_jobs_count = identify_inactive_jobs(existing_company_jobs, postings_to_add, IS_COMPANY_PAGE_SCRAPING)

    return(new_jobs, jobs_to_inactivate, company_reactivated_jobs_count)