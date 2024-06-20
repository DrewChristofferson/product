from ...utils.utils_parsing import get_content_final_url
from ..db_requests.update_job import deactivate_airtable_record


def deactivate_old_jobs(company_jobs, deactivated_count):
    for job in company_jobs:
        if job['is_active']:
            _id = job['id']
            url = job['job_post_linkedin_url']
            url_after_final_redirect = get_content_final_url(url)
            if url_after_final_redirect and 'expired_jd_redirect' in url_after_final_redirect:
                deactivated_count = deactivate_airtable_record(_id, deactivated_count)
            else: # url is None or url is not expired:
                pass
                # print("not expired")
    return(deactivated_count)

