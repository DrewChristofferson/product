from ..db_requests.update_job import reopen_job

def identify_inactive_jobs(existing_jobs, postings_to_add, is_company_page=False):
    new_jobs = []
    jobs_to_inactivate = []
    reactivated_jobs_count = 0
    if is_company_page: #logic for company pages only - target state
        print("idenitfy logic!!", len(existing_jobs), len(postings_to_add))
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
        
        #identify inactive jobs in the exiting jobs
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
        for key, value in postings_to_add.items():
            job_found_in_existing = False
            posting_to_add_id = key
            posting_to_add_fields = value
            for existing_job in existing_jobs:
                # if posting_to_add_fields['job_title'] == existing_job['job_title']:
                #     print(posting_to_add_fields['company_name'], existing_job['company_name'])
                if posting_to_add_fields['job_title'] == existing_job['job_title'] and posting_to_add_fields['location'] in existing_job['locations'] and posting_to_add_fields['company_name'] == existing_job['company_name'][0]:
                    if existing_job["is_active"] == False:
                        reopen_job(existing_job["id"], posting_to_add_fields['job_url'])
                        reactivated_jobs_count += 1
                    job_found_in_existing = True
            if job_found_in_existing == False:
                new_jobs.append(postings_to_add[posting_to_add_id])
                
        #identify inactive jobs
        for existing_job in existing_jobs:
            if existing_job["is_active"] == False:
                pass
            else:
                job_found_in_new_postings = False
                for key, value in postings_to_add.items():
                    posting_to_add_id = key
                    posting_to_add_fields = value
                    if posting_to_add_fields['job_title'] == existing_job['job_title'] and posting_to_add_fields['location'] in existing_job['locations'] and posting_to_add_fields['company_name'] == existing_job['company_name'][0]:
                        job_found_in_new_postings = True
                if job_found_in_new_postings == False:
                    jobs_to_inactivate.append(existing_job)

    # print(jobs_to_inactivate)
    return(new_jobs, jobs_to_inactivate, reactivated_jobs_count)


