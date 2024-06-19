from ...utils.utils_parsing import get_url_content
from ..db_requests.update_job import deactivate_airtable_record


def deactivate_old_jobs(company_jobs, deactivated_count):
    for job in company_jobs:
        _id = job['id']
        url = job['job_post_linkedin_url']
        content = get_url_content(url)
        body_content = content.find("div", class_="description__text")
        if body_content is None:
            deactivated_count = deactivate_airtable_record(_id, deactivated_count)
            print("deactivate this baby!! level 1")
    return(deactivated_count)
        # else:
        #     text = body_content.get_text()
        #     if text is None or "No longer accepting applications" in text:
        #         # deactivate_airtable_record(_id)
        #         print("deactivate this baby!! level 2")
