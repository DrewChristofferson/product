
from .utils import set_airtable_config, write_to_json, get_experience_number, get_levels
from ..utils.company_mapping_2 import airtable_codes as airtable_ids
import json
from datetime import datetime
import re



def bulk_update():
    for key, value in airtable_ids.items():
        company_name = key
        company_updates = []
        json_file_path = f"../data/new_production/data/{company_name}.json"
        # print(company_name)
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        for key, value in data.items():
            if not "waiting_for_job_details_run" in value:
                value["waiting_for_job_details_run"] = True
        #     if "airtable_id" in value:
        #         del value["airtable_id"]
        #     else:
        #         print("no id")
        #     if "airtable_id_test1" in value:
        #         del value["airtable_id_test1"]
        #     else:
        #         print("no id1")
        #     if "airtable_id_test2" in value:
        #         del value["airtable_id_test2"]
        #     else:
        #         print("no id2")
        with open(json_file_path, "w") as file:
            json.dump(data, file, indent=4)
       
       
        # # print(company_name, dups)
        #     airtable = set_airtable_config('tbl9y2HmtQMDwTjHX')
        #     airtable 
        #     if "airtable_id" in value:
        #         company_updates.append({
        #             "id": value["airtable_id"],
        #             "fields": {
        #                 'company_linked': airtable_ids[company_name]
        #             }
        #         })
        #     else:
        #         print("no id")
        # print(company_updates)
        # airtable.batch_update(company_updates)
            
            # airtable.create({
            #         "job_title": value["Job Title"],
            #         "company_linked": 'recyGWIotMciXHLKN',  
            #         "location": [value["Location"], "San Diego, CA"],
            #         "level": value["level"],
            #         "years_experience_req": 3,
            #         "job_post_url": value["External Job Url"],
            #         "is_active": value["is_active"],
            #         "min_salary": value["Min Salary"],
            #         "max_salary": value["Max Salary"],
            #         "posted_date": value["Posted Date"],
            #         "closed_date": value["job_closed_date"],
            #         "experience_desc": value["Experience Requirements"][0],
            #     }, typecast = True
            #     )


            # if "years_experience_required" in value:
            #     og_years = value["years_experience_required"]
            #     # print(og_years)
            #     if isinstance(og_years, str):
            #         print("found string", company_name)
            #         value["years_experience_required"] = int(og_years)
            # else:
            #     value["years_experience_required"] = None
            # write_to_json(json_file_path, data, company_name)

        #     print(value["Job Title"])
        #     value["level"] = get_levels(value["Job Title"])
        #     value["years_experience_required"] = get_experience_number(value["Experience Requirements"])
        # write_to_json(json_file_path, data, company_name)


            





# - product manager - 3/5, 3, 5 - (Deel, Discord, dropbox)
# - staff - 8, 7, 7,5 - (cockroach labs, confluent, databricks, etsy)
# - senior or sr - 4, 5, 3/5, 4/6, 8, 4/6, 6/10, 5, 4/5 - (confluent, databricks, datadog, Discord, Docusign, duolingo, ebay, EA, Epic)
# - senior staff - 8 - (databricks)
# - group - 7 - (datadog)
# - senior group - 8 - (dropbox)
# - intern - 0 - (chegg)
# - lead - 7, 8/10 - (circle, ebay)
# - II (or 2) - 5, 1/3 - (coinbase, datadog)
# - III - 3 - (expedia)
# - principal - 5,7, 7 - (Contentful, crowdstrike, dropbox)
# - senior principal - 10 - (dropbox)
# - associate
# - director TODO
# - head of product TODO
# - VP product TODO
# - technical 



# In our org, it is Sr. PM --> Staff PM --> Principal PM (all IC) , this is one path

# another is: Sr. PM --> PM Lead --> GPM

# Basically PM Lead (have a few Jr PM report to them) = Staff PM (IC) = same salary

# GPM (have more report to them) = Principal PM (IC) = same salary