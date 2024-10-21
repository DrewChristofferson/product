from ..db_requests.update_job import add_loc_to_existing_job


def dedup_jobs(company_name, new_jobs, existing_jobs):
    # Determine whether any new jobs are duplicates with old jobs
    i = 0
    while i < len(new_jobs):
        new_job = new_jobs[i]
        for existing_job in existing_jobs:
            if existing_job["is_active"] == False:
                pass
            else:
                if (new_job['job_title'] == existing_job['job_title'] and
                    new_job['years_experience_req'] == existing_job['years_experience_req'] and
                    new_job['locations'][0] not in (existing_job['locations'] if existing_job['locations'] else [])):
                    
                    add_loc_to_existing_job(new_job['locations'][0], existing_job)
                    new_jobs.pop(i)
                    i -= 1  # Decrementing to stay at the same index after popping an element
                    break  # Exit the inner loop once a match is found
        i += 1  # Move to the next index in the outer loop
    
    # Determine whether any new jobs are duplicates with each other
    indexes_to_delete = []
    new_jobs_copy = new_jobs.copy()
    for i, new_job1 in enumerate(new_jobs_copy):  # Iterate over a copy of the list
        for j, new_job2 in enumerate(new_jobs_copy):  # Iterate over a copy of the list
            if i != j and i not in indexes_to_delete and 'locations' in new_job1 and 'locations' in new_job2:
                if new_job1['job_title'] == new_job2['job_title'] and new_job1['years_experience_req'] == new_job2['years_experience_req']:
                    new_jobs[i]['locations'].extend(new_jobs[j]['locations'])
                    indexes_to_delete.append(j)
    new_jobs = [new_job for i, new_job in enumerate(new_jobs) if i not in indexes_to_delete]
    return(new_jobs)


