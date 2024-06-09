from ..scraper.db_requests.get_companies import pull_companies, get_one_company
from ..scraper.db_requests.get_investors import pull_investors
from ..scraper.db_requests.update_company import add_investors, update_company
from ..scraper.openai.test_openai import get_investors, gpt_get_company_info
from ..utils.utils_parsing import get_url_content, get_element_text
import json
from datetime import datetime
import re



def bulk_update():
    update_existing_company_data()
    # onboard_company("CarGurus")
    
    # TDOD: update_third_party_ratings("https://www.comparably.com/companies/cargurus")


def onboard_company(company_name, company_website=None):
    company_airtable = get_one_company(company_name)
    # print(company_airtable)
    id = company_airtable['id']
    website = ''
    if 'website' in company_airtable['fields']:
        website = company_airtable['fields']['website']
    else:
        website = company_website
    gpt_response = gpt_get_company_info(company_name, website)
    updated_company = update_company(id, gpt_response)

def update_existing_company_data():
    companies = pull_companies()
    for company in companies:
        if not company["hq_country"]:
            gpt_response = gpt_get_company_info(company['name'], company['website'])
            updated_company = update_company(company['airtable_id'], gpt_response)

def update_third_party_ratings(url):
    content = get_url_content(url)
    print(content)
    rating = get_element_text(content, "div", "starLabel")
    print(rating)

def update_company_investors():
    investors_map = {}
    investors_list_str = ""
    companies = pull_companies()
    # print(companies)
    investors = pull_investors()
    for investor in investors:
        investors_map[investor['fields']['name']] = investor['id']
        investors_list_str += f"{investor['fields']['name']}, "
    # print(investors_map)

    for company in companies:
        print(company['name'], investors_list_str)
        investors_gpt = get_investors(company['name'], investors_list_str)
        formatted_list_investors = []
        for response in investors_gpt:
            for investor in response['investors']:
                if investor in investors_map:
                    formatted_list_investors.append(investors_map[investor])
        print(formatted_list_investors)
        if formatted_list_investors:
            add_investors(company['airtable_id'], formatted_list_investors)
        # company_investors = company['Top 5 Investors']
        # if company_investors:
        #     formatted_list_investors = []
        #     for company_investor in company_investors:
        #         if company_investor in investors_map:
        #             formatted_list_investors.append(investors_map[company_investor])
        #     if formatted_list_investors:
        #         add_investors(company['airtable_id'], formatted_list_investors)
        #         print(company['name'], formatted_list_investors)


