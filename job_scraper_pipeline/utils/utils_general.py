import hashlib
from datetime import datetime
import json

def calc_start_time(run_log_file_path):
    start_datetime = datetime.now()
    start_time = start_datetime.replace(microsecond=0)
    log(run_log_file_path, f'Started scraping jobs at {start_time}\n')
    return(start_datetime)

def create_job_unique_code(job_details):
    list_str = ''.join(job_details)
    hash_code = hashlib.sha256(list_str.encode()).hexdigest()
    return hash_code

def log(file_path, data):
    # for the moment we are just printing the data, but in the future we can output logs to a file
    # write_to_txt(file_path, data)
    print(data)

def write_to_txt(file_path_in, data):
    with open(file_path_in, "a") as file:
        # Write some text to the file
        file.write(data)

def is_valid_json(content):
    try:
        json.loads(content)
    except ValueError as e:
        return False
    return True





