import json
import xml.etree.ElementTree as ET
from .company_mapping import linkedInCompanyCodes as l


import json
import csv

def create_csv():
    fieldnames = ["Job ID", "Job Title", "Company", "Location", "Job Url", "External Job Url", "is_active",
                  "Min Salary", "Max Salary", "Pay Schedule", "Posted Date", "job_closed_date",
                  "Experience Requirements", "Seniority level", "Employment type",
                  "Job function", "Industries", "years_experience_required", "level", "airtable_id", "locations", "duplicate"]

    with open(f"../data/production/csv_export.csv", mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()


def convert_json_to_csv(json_data):
    fieldnames = ["Job ID", "Job Title", "Company", "Location", "Job Url", "External Job Url", "is_active",
                  "Min Salary", "Max Salary", "Pay Schedule", "Posted Date", "job_closed_date",
                  "Experience Requirements", "Seniority level", "Employment type",
                  "Job function", "Industries", "years_experience_required", "level", "airtable_id", "locations", "duplicate"]

    with open(f"../data/production/csv_export.csv", mode="a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for job_id, job_info in json_data.items():
            job_info["Job ID"] = job_id
            # print(job_info["Job Title"])
            del job_info["Description"]  # Remove "Description" field
            del job_info["is_scrape_done"]  # Remove "is_scrape_done" field
            writer.writerow(job_info)

# Load JSON data from file
def update_csv():
    create_csv()
    for key, value in l.items():
        with open(f"../data/production/data/{key}.json") as json_file:
            json_data = json.load(json_file)
            print(key)

        # Convert JSON to CSV
        convert_json_to_csv(json_data)


