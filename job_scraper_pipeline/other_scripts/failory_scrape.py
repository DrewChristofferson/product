import requests
from bs4 import BeautifulSoup
from .company_mapping import linkedInCompanyCodes as l, Airtable_codes as a
from ..scraper.utils import set_airtable_config
from datetime import datetime
from .companies_to_add import companies
from ..utils.company_mapping_2 import airtable_codes as a2




def get_unicorns():
    failory = requests.get('https://www.failory.com/startups/united-states-unicorns')
    soup = BeautifulSoup(failory.content, "html.parser")
    names = []
    valuation_amts = []
    valuation_dates = []
    new_companies = []

    headers = soup.find_all("h3")

    for name in headers:
        text_name = name.text
        split_name = text_name.split(')')
        number_removed = split_name[1].strip()
        names.append(number_removed)

    details = soup.find_all("ul")

    for detail in details:
        valuation = detail.find('li')
        valuation_text = valuation.text
        split_detail = valuation_text.split(':')
        split_detail_2 = split_detail[1].split('(')
        valuation_amt = split_detail_2[0].strip()[1:-1]
        valuation_date = split_detail_2[1].strip()[:-1]
        valuation_date = datetime.strptime(valuation_date, '%B %Y')
        formatted_valuation_date = valuation_date.strftime('%Y-%m')
        valuation_amts.append(float(valuation_amt))
        valuation_dates.append(formatted_valuation_date)
    
    for index, value in enumerate(names):
        new_companies.append({
            'Name': names[index],
            'Last Valuation Amount ($B)': valuation_amts[index],
            'Last Valuation Date': valuation_dates[index]
        })
    # add_companies_to_list(new_companies)
    add_valuation_to_airtable(new_companies)
    # print(a)


def add_companies_to_list(new_company_names):
    for company in new_company_names:
        if company['Name'] not in a:
            airtable = set_airtable_config('tblGwlPqq03yEQjV1')
            response = airtable.create(company)
            new_id = response['id']
            print(new_id, "created!")
            a[company['Name']] = new_id
        else:
            print(company['Name'], " already exists")

def add_valuation_to_airtable(new_company_names):
    for company in new_company_names:
        print("trying", company['Name'])
        if company['Name'] in a2:
            airtable = set_airtable_config('tblGwlPqq03yEQjV1')
            try:
                response = airtable.update(a2[company['Name']], {
                    "Last Valuation Amount ($B)": company['Last Valuation Amount ($B)'],
                    "Last Valuation Date": company['Last Valuation Date']
                })
                print(response['fields']['Name'])
            except Exception as e:
                print(f'failed to get {company["Name"]}')


def add_extra_companies_to_list():
    # repurposed to add more companies to airtable
    for company in companies:
        if company not in a2:
            airtable = set_airtable_config('tblGwlPqq03yEQjV1')
            response = airtable.create({'Name': company})
            new_id = response['id']
            print(new_id, "created!")
            a2[company] = new_id
    # for key, value in a2.items():
    #     if not value:
    #         response = airtable.create({'Name': key})
    #         new_id = response['id']
    #         print(new_id, "created!")
    #         a2[key] = new_id
    #     else:
    #         print(key, " already exists")
    print(a2)

    
    
