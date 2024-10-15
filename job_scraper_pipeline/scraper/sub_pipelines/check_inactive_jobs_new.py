from ...utils.utils_parsing import get_content_final_url, get_url_content, check_active_job
from ...utils.utils_selenium import open_selenium_driver
from ..db_requests.update_db_job import deactivate_record
from fake_useragent import UserAgent
 

def deactivate_old_jobs(browser, company_jobs, deactivated_count):
    for job in company_jobs:
        if job['is_active']:
            ua=UserAgent()
            hdr = {'User-Agent': ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
            _id = job['id']
            url = job['job_post_url']
            is_active = check_active_job(url, hdr)
            if not is_active:
                deactivated_count = deactivate_record(_id, deactivated_count)
    return(deactivated_count)

