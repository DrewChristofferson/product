from ..db_requests.update_job import reopen_job

def identify_inactive_jobs(existing_jobs, postings_to_add, is_company_page=False):
    new_jobs = []
    jobs_to_inactivate = []
    reactivated_jobs_count = 0
    if is_company_page: #logic for company pages only - target state
        #identify new jobs in the new scraped postings
        for key, value in postings_to_add.items():
            job_found_in_existing = False
            posting_to_add_id = key
            posting_to_add_fields = value
            for existing_job in existing_jobs:
                if existing_job["is_active"] == True and posting_to_add_fields['job_title'] == existing_job['job_title'] and posting_to_add_fields['company_name'] == existing_job['company_name'][0]:
                    job_found_in_existing = True
            if job_found_in_existing == False:
                new_jobs.append(postings_to_add[posting_to_add_id])
        
        #identify inactive jobs in the existing jobs
        for existing_job in existing_jobs:
            if existing_job["is_active"] == False:
                pass
            else:
                job_found_in_new_postings = False
                for key, value in postings_to_add.items():
                    posting_to_add_id = key
                    posting_to_add_fields = value
                    if posting_to_add_fields['job_title'] == existing_job['job_title'] and posting_to_add_fields['company_name'] == existing_job['company_name'][0]:
                        job_found_in_new_postings = True
                if job_found_in_new_postings == False:
                    jobs_to_inactivate.append(existing_job)
    else:
        #identify new jobs
        jobs_to_reopen = []
        unique_jobs_reopen = []
        for key, value in postings_to_add.items():
            job_found_in_existing = False
            posting_to_add_id = key
            posting_to_add_fields = value
            # print(posting_to_add_fields['job_title'], posting_to_add_fields['location'])
            for existing_job in existing_jobs:
                # if posting_to_add_fields['job_title'] == existing_job['job_title']:
                # print(existing_job['is_active'], posting_to_add_fields['job_title'], existing_job['job_title'], posting_to_add_fields['location'], existing_job['locations'], posting_to_add_fields['company_name'],existing_job['company_name'][0])
                if posting_to_add_fields['job_title'] == existing_job['job_title'] and posting_to_add_fields['location'] in (existing_job['locations'] if existing_job['locations'] else []) and posting_to_add_fields['company_name'] == existing_job['company_name'][0]:
                    if existing_job["is_active"] == False and 'reopened' not in existing_job:
                        existing_job['job_post_url'] = posting_to_add_fields['job_url']
                        jobs_to_reopen.append(existing_job)
                        # reopen_job(existing_job["id"], posting_to_add_fields['job_url'])
                        
                    job_found_in_existing = True
            if job_found_in_existing == False:
                new_jobs.append(postings_to_add[posting_to_add_id])
        for job in jobs_to_reopen:
            if job['id'] not in unique_jobs_reopen:
                reactivated_jobs_count +=1
                unique_jobs_reopen.append(job['id'])
                reopen_job(job['id'], job['job_post_url'])


                
        #identify inactive jobs. Deprecated and replaced by check_inactive_jobs.py
        # for existing_job in existing_jobs:
        #     if existing_job["is_active"] == False:
        #         pass
        #     else:
        #         job_found_in_new_postings = False
        #         for key, value in postings_to_add.items():
        #             posting_to_add_id = key
        #             posting_to_add_fields = value
        #             if posting_to_add_fields['job_title'] == existing_job['job_title'] and posting_to_add_fields['location'] in existing_job['locations'] and posting_to_add_fields['company_name'] == existing_job['company_name'][0]:
        #                 job_found_in_new_postings = True
        #         if job_found_in_new_postings == False:
        #             jobs_to_inactivate.append(existing_job)

    # print(jobs_to_inactivate)
    return(new_jobs, jobs_to_inactivate, reactivated_jobs_count)


