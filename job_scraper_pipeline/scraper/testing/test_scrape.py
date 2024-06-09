from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def test_scrape():
    job_listings_xpath = "//div[contains(@id, 'jobWrap')]//div//div//a"
    job_title_xpath = ".//span"
    job_url_xpath = None
    next = "//a[contains(@class, 'next')]"

    driver = webdriver.Chrome() 
    driver.get('https://www.databricks.com/company/careers/open-positions?department=Product&location=all')
    current_job_listings_on_page = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, job_listings_xpath))
    )
    # time.sleep(2)
    # print("going")
    current_job_listings_on_page = driver.find_elements(By.XPATH,job_listings_xpath)
    print((len(current_job_listings_on_page)))

    for job_listing in current_job_listings_on_page:
        # link_element = job_listing.find_element(By.XPATH, job_url_xpath)
        job_url = job_listing.get_attribute("href")
        job_title = job_listing.find_element(By.XPATH, job_title_xpath).text
        print(job_url, job_title)
    # next_button = driver.find_element(By.XPATH, next)
    # next_button.click()
    time.sleep(10)

def test_scrape_capitalone():
    job_listings_xpath = "//section[contains(@id, 'search-results-list')]//ul//li"
    job_title_xpath = ".//a//h2"
    job_url_xpath = ".//a"
    next = "//a[contains(@class, 'next')]"

    driver = webdriver.Chrome() 
    driver.get('https://www.capitalonecareers.com/search-jobs/product%20manager/Fairlee%2C%20VA/234/1/4/6252001-6254928-4758041-4046694/38x87372/-77x27137/50/2')
    current_job_listings_on_page = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, job_listings_xpath))
    )
    # time.sleep(2)
    # print("going")
    current_job_listings_on_page = driver.find_elements(By.XPATH,job_listings_xpath)
    print((len(current_job_listings_on_page)))

    for job_listing in current_job_listings_on_page:
        link_element = job_listing.find_element(By.XPATH, job_url_xpath)
        job_url = link_element.get_attribute("href")
        job_title = job_listing.find_element(By.XPATH, job_title_xpath).text
        print(job_url, job_title)
    next_button = driver.find_element(By.XPATH, next)
    next_button.click()
    time.sleep(10)

def test_scrape_apple():
    job_listings_xpath = "//div[contains(@class, 'results__table')]//table//tbody"
    job_title_xpath = ".//tr//td[contains(@class, 'table-col-1')]//a"
    job_url_xpath = ".//tr//td[contains(@class, 'table-col-1')]//a"
    next = "//li[contains(@class, 'pagination__next')]"

    driver = webdriver.Chrome() 
    driver.get('https://jobs.apple.com/en-us/search?location=united-states-USA&sort=relevance&search=%22product%20manager%22')
    current_job_listings_on_page = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, job_listings_xpath))
    )
    # time.sleep(2)
    # print("going")
    current_job_listings_on_page = driver.find_elements(By.XPATH,job_listings_xpath)
    print((len(current_job_listings_on_page)))

    for job_listing in current_job_listings_on_page:
        link_element = job_listing.find_element(By.XPATH, job_url_xpath)
        job_url = link_element.get_attribute("href")
        job_title = job_listing.find_element(By.XPATH, job_title_xpath).text
        print(job_url, job_title)
    next_button = driver.find_element(By.XPATH, next)
    next_button.click()
    time.sleep(10)

def test_scrape_workday():
    job_listings_xpath = "//li[contains(@class, 'css-1q2dra3')]"
    job_title_xpath = ".//div//div//div//h3//a"
    job_url_xpath = ".//div//div//div//h3//a"
    next = "//button[@aria-label='next']"

    driver = webdriver.Chrome() 
    driver.get('https://transunion.wd5.myworkdayjobs.com/en-US/TransUnion?q=%27Product+Manager%27&locationCountry=bc33aa3152ec42d4995f4791a106ed09')
    current_job_listings_on_page = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, job_listings_xpath))
    )
    # time.sleep(2)
    # print("going")
    current_job_listings_on_page = driver.find_elements(By.XPATH,job_listings_xpath)
    print((len(current_job_listings_on_page)))

    for job_listing in current_job_listings_on_page:
        link_element = job_listing.find_element(By.XPATH, job_url_xpath)
        job_url = link_element.get_attribute("href")
        job_title = job_listing.find_element(By.XPATH, job_title_xpath).text
        print(job_url, job_title)
    next_button = driver.find_element(By.XPATH, next)
    next_button.click()
    time.sleep(10)


# tiktok
    # def test_scrape():
    # driver = webdriver.Chrome() 
    # driver.get('https://careers.tiktok.com/position?keywords=product%20manager&category=6704215864629004552&location=&project=&type=&job_hot_flag=&current=1&limit=100&functionCategory=&tag=')
    # current_job_listings_on_page = WebDriverWait(driver, 10).until(
    #     EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'borderContainer__3S4gr')]//div//a"))
    # )
    # # time.sleep(2)
    # # print("going")
    # current_job_listings_on_page = driver.find_elements(By.XPATH, "//div[contains(@class, 'borderContainer__3S4gr')]//div//a")
    # print((len(current_job_listings_on_page)))

    # for job_listing in current_job_listings_on_page:
    #     # link_element = job_listing.find_element(By.TAG_NAME, "a")
    #     job_url = job_listing.get_attribute("href")
    #     job_title = job_listing.find_element(By.XPATH, ".//div[contains(@class, 'title__37NOe')]").text
    #     print(job_url, job_title)
    # next_button = driver.find_element(By.XPATH, "//li[@title='Next Page']")
    # next_button.click()
    # time.sleep(10)