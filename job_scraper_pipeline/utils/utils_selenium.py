from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import time
from .utils_general import log  


class AuthwallBlocker(Exception):
    pass

def set_up_selenium_browser():
    CUSTOM_REFERER = "https://google.com"

    # Set up Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--referer=" + CUSTOM_REFERER)
    chrome_options.add_argument("--headless=new")
    # Instantiate the Chrome driver with the custom options
    browser = webdriver.Chrome(options=chrome_options)
    return browser


def open_selenium_driver(driver, url, company_name=None, run_log_file_path=None, max_retries=4, delay=1):
    retries = 0
    max_retries_reached = False
    while retries <= max_retries:
        try:
            # print(f'try: ', retries + 1)
            driver.get(url)
            time.sleep(1)
            has_authwall = determine_authwall(driver)
            if has_authwall and (max_retries - retries == 0):
                print("Max retries")
                max_retries_reached = True
                raise AuthwallBlocker(f"Reached max retries ({max_retries}) for fetching job listings for {company_name}")
            elif has_authwall and not max_retries_reached:
                # print(f"Authwall. Retries left: {max_retries - retries}")
                retries += 1
                time.sleep(4)
        except Exception as e:
            log(run_log_file_path, f'{e}\n')
        finally:
            if not has_authwall or max_retries_reached:
                return


def scroll_to_all_job_listings(browser):
    while True:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        browser.execute_script("window.scrollBy(0, -200);")
        try:
            element = WebDriverWait(browser, 2).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'inline-notification__text'))
            )
            break  # Exit the loop once the element is found
        except TimeoutException:
            pass

        try:
            element2 = WebDriverWait(browser, 1).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'infinite-scroller__show-more-button'))
            )
            element2.click()
            # print("Show more found!")
            # break  # Exit the loop once the element is found
        except TimeoutException:
            pass
        # print("Element not found, scrolling down...")


def check_if_element_exists(type, html, criteria=None):
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