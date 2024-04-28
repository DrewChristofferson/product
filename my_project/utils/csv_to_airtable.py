import os
from dotenv import load_dotenv
import json
from pyairtable import Api
from pyairtable.formulas import match
from ..utils.company_mapping_2 import airtable_codes as a
from ..scraper.utils import write_to_json


def update_airtable():
    upload_all_jobs()

def get_table():
    load_dotenv("../.env")
    api_key = os.getenv("AIRTABLE_API_KEY")
    api = Api(api_key)
    table = api.table('appT4TIFvWbwAQ35G', 'tbliHYwp5pTrRxqJk')
    return table

def get_all_jobs(table):
    for key, value in l.items():
        company_name = key
        print(company_name)
        formula = match({"company_name": company_name})
        records = table.all(formula=formula)
        for record in records:
            # print("airtable", record["fields"]["job_title"], record["fields"]["location"])
            json_file_path = f"../data/production/data/{company_name}.json"
            if os.path.exists(json_file_path):
                with open(f"../data/production/data/{company_name}.json") as json_file:
                    data = json.load(json_file)
                for key, value in data.items():
                    if value["Job Title"] == record["fields"]["job_title"] and value["Location"] == record["fields"]["location"]:
                        value["airtable_id"] = record["id"]
                        print(f"found match!!", value["Job Title"])

                write_to_json(json_file_path, data, company_name)

            else:
                print("no file path exists!!")
        # print(records)
    

def upload_all_jobs():
    for key, value in a.items():
        company_name = key
        skip_companies = ["assembly", "Assembly", "Aptos", "Apple", "X (formerly Twitter)", "Zip", "BFMeta"]
        print(company_name)
        if company_name not in skip_companies:
            update_company(company_name)

def update_company(company_name, new_jobs):
    table = get_table()
    # for new_job in new_jobs:
    #     # if 'company_name' in new_job:
    #     #     del new_job['company_name']
    #     if 'company_airtable_id' in new_job:
    #         print("airtable id", new_job)
            # new_job['company_linked'] = new_job.pop('company_airtable_id')
    response = table.batch_create(
        new_jobs,
        # typecast = true
        True
    )
    count_new_jobs = len(response)
    return(count_new_jobs)
    
        
    # for records in table.iterate(page_size=100, max_records=1000):
    #     for job in records:
    #         airtable_codes[job['fields']['Name']] = job['id']
    #     print(airtable_codes)


    # for key, value in l.items():
    #     with open(f"../data/production/data/{key}.json") as json_file:
    #         data = json.load(json_file)
    #     for key, value in data.items():
    #         table.create({
    #             "Job Title": value["Job Title"],
    #             "Company": value["Company"],
    #             "Location": value["Location"],
    #             "Companies linked": ['recyGWIotMciXHLKN']
    #             })


    #create new airtable job in job_scraper
    #save airtableid as field in local db
    #anytime we update local db, we also need to make a call to airtable, referencing the airtable id