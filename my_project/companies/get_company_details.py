from bs4 import BeautifulSoup
import csv
import os
import re
from pyairtable import Api
from dotenv import load_dotenv
from ..old_files.company_mapping import Airtable_codes as airtable_ids, linkedInCompanyCodes as linkedin_ids
from ..utils.company_mapping_2 import airtable_codes as new_airtable_codes 

airtable_api_key = ''
airtable_table = ''

def set_airtable_vars():
    global airtable_api_key
    global airtable_table
    # Load environment variables from .env file
    load_dotenv("../.env")

    api_key = os.getenv("AIRTABLE_API_KEY")
    # print(api_key)

    airtable_api_key = Api(api_key)
    airtable_table = airtable_api_key.table('appT4TIFvWbwAQ35G', 'tblGwlPqq03yEQjV1')
    print(airtable_table)

def create_csv_with_header():
    fieldnames = ["company_name", "hq_location", "description", "founded_date", "founders", "num_employees",
                  "funding_status", "last_funding_date", "last_funding_type", "estimated_revenue", "website",
                  "description_full", "last_funding_amount", "top_5_investors",
                  "total_funding_amount", "acquired_by", "acquired_date", "acquired_price", "ipo_status", "ipo_date", "stock_symbol"]

    with open(f"../my_project/companies/companies.csv", mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()


def pull_out_details(file_in): 
    with open(file_in, 'r') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    grid_rows = soup.find_all('grid-row')

    print(len(grid_rows))
    for row in grid_rows:
        company_details = []
        grid_cells = row.find_all('grid-cell')
        # Extract text from each grid-cell element
        for cell in grid_cells:
            text = cell.get_text(strip=True)
            text_without_newlines = text.replace('\n', '')
            if text_without_newlines:
                #check to see whether letter and/or number are present
                if not (bool(re.search(r'[a-zA-Z]', text_without_newlines)) or bool(re.search(r'\d', text_without_newlines))):
                    text_without_newlines = ''
                company_details.append(text_without_newlines)
        company_details[4] = company_details[4].split(',')
        company_details[14] = company_details[14].split(',')
        # write_row_to_csv(company_details)
        update_airtable(company_details)

def write_row_to_csv(company_details):
    csv_file_path = f"../my_project/companies/companies.csv"  # Replace with your CSV file path

    # Open the CSV file in append mode
    with open(csv_file_path, mode='a', newline='') as csv_file:
        # Create a CSV writer object
        csv_writer = csv.writer(csv_file)

        # Write the new row to the CSV file
        csv_writer.writerow(company_details)

def update_airtable(company_details):
    global airtable_table
    company_name = company_details[0]
    if company_name in new_airtable_codes:
        if company_name == 'Amazon':
            company_name = 'AWS'
            
        print(company_name)
        try:
            response = airtable_table.update(new_airtable_codes[company_name], {
                # "linkedin_id": linkedin_ids[company_name],
                "Name": company_details[0],
            "Headquarters": company_details[1],
            "Description": company_details[2],
            "Founded Date": company_details[3],
            "Founders": company_details[4],
            "Number of Employees": company_details[5],
            "Funding Status": company_details[6],
            "Last Funding Date": company_details[7],
            "Last Funding Type": company_details[8],
            "Estimated Revenue": company_details[9],
            "Website": company_details[10],
            "Last Funding Amount": company_details[11],
            "Full Description": company_details[12],
            "Total Funding Amount": company_details[13],
            "Top 5 Investors": company_details[14],
            "Acquired By": company_details[15],
            "Acquired Date": company_details[16],
            "Acquired Price": company_details[17],
            "IPO Status": company_details[18],
            "IPO Date": company_details[19],
            "Stock Symbol": company_details[20]

            }, typecast=True)
            company_id = response['id']
            print(company_id)
        except Exception as e:
                print(e, company_name, company_details)
    else:
        print("not here,", company_name)
    # 


def update_companies(): 
    company_html_files = [
        # f"../my_project/companies/companies_1-50.html",
        # f"../my_project/companies/companies_51-100.html",
        # f"../my_project/companies/companies_101-150.html",
        # f"../my_project/companies/companies_151-200.html",
        # f"../my_project/companies/companies_201-250.html"
        # f"../my_project/companies/new_comp3_1-50.html",
        # f"../my_project/companies/new_comp3_51-100.html",
        # f"../my_project/companies/new_comp3_101-150.html",
        # f"../my_project/companies/new_comp3_151-200.html",
        # f"../my_project/companies/new_comp3_missing.html",
        # f"../my_project/companies/new_comp_301-350.html",
        # f"../my_project/companies/new_comp_351-400.html",
        # f"../my_project/companies/new_comp_401-450.html",
        # f"../my_project/companies/new_comp_451-500.html"
        f"../my_project/companies/new_comp4_1-50.html",
    ]
    set_airtable_vars()
    create_csv_with_header()
    for file in company_html_files:
        pull_out_details(file)



