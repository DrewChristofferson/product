from ..db_requests.update_db_job import reopen_job

#TODO: Check this logic
def identify_inactive_jobs(existing_jobs, postings_to_add, is_company_page=False):
    new_jobs = []
    jobs_to_inactivate = []
    reactivated_jobs_count = 0
    if is_company_page: #logic for company pages only - target state
        print('existing jobs', len(existing_jobs))
        print('postings to add', len(postings_to_add))
        #identify new jobs in the new scraped postings
        for posting_to_add in postings_to_add:
            job_found_in_existing = False
            for existing_job in existing_jobs:
                if existing_job["is_active"] == True and posting_to_add['title'] == existing_job['title'] and posting_to_add['company_name'] == existing_job['company']['name']:
                    job_found_in_existing = True
            if job_found_in_existing == False:
                new_jobs.append(posting_to_add)
        
        #identify inactive jobs in the existing jobs
        for existing_job in existing_jobs:
            if existing_job["is_active"] == False:
                pass
                #TODO: check for jobs to reopen
            else:
                job_found_in_new_postings = False
                for posting_to_add in postings_to_add:
                    if posting_to_add['title'] == existing_job['title'] and posting_to_add['company_name'] == existing_job['company']['name']:
                        job_found_in_new_postings = True
                if job_found_in_new_postings == False:
                    jobs_to_inactivate.append(existing_job)
    else:
        #identify new jobs
        jobs_to_reopen = []
        for posting_to_add in postings_to_add:
            job_found_in_existing = False
            for existing_job in existing_jobs:
                if posting_to_add['title'] == existing_job['title'] and posting_to_add['company_name'] == existing_job['company']['name']:
                    #If the posting matches an existing job, mark as true so that we don't add
                    #this posting to the list of new jobs
                    job_found_in_existing = True
                    if existing_job["is_active"] == False and posting_to_add['job_url'].split('?')[0] == existing_job['job_post_url'].split('?')[0]:
                        jobs_to_reopen.append(existing_job)
                        reopen_job(existing_job["id"], posting_to_add['job_url'])
                        reactivated_jobs_count +=1
            if job_found_in_existing == False:
                new_jobs.append(posting_to_add)

    print('counts:', len(new_jobs), len(jobs_to_inactivate), reactivated_jobs_count)
    return(new_jobs, jobs_to_inactivate, reactivated_jobs_count)


