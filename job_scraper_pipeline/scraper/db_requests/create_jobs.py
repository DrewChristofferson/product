from .utils.set_airtable_configs import set_airtable_config


def create_new_jobs_batch(new_jobs):
    print(new_jobs)
    table = set_airtable_config("jobs")
    response = table.batch_create(
        new_jobs,
        typecast = True
    )
    count_new_jobs = len(response)
    return(count_new_jobs)
    
