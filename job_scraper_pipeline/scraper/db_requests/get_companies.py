from .utils.set_airtable_configs import set_airtable_config
from pyairtable.formulas import match


def pull_companies():
    all_companies = []
    airtable = set_airtable_config('companies')
    formula = match({"name": "Salesforce"})
    response = airtable.all(
        # formula=formula,
        sort=["name"], 
        fields=[
            "name", 
            "linkedin_id", 
            "website",
            "is_inactive", 
            "Last Scrape Date", 
            "Careers Page URL", 
            "job_listings_xpath", 
            "job_url_xpath", 
            "job_title_xpath",
            "job_details_xpath",
            "next_btn_xpath",
            "investors",
            "hq_country"
        ])
    for company in response:
        if 'is_inactive' not in company['fields']:
            response = all_companies.append({
                "name": company['fields']['name'],
                "airtable_id": company['id'],
                "linkedin_id": company['fields']['linkedin_id'] if 'linkedin_id' in company['fields'] else None,
                "website": company['fields']['website'] if 'website' in company['fields'] else None,
                "careers_page_url": company['fields']['Careers Page URL'] if 'Careers Page URL' in company['fields'] else None,
                "Last Scrape Date": company['fields']['Last Scrape Date'] if 'Last Scrape Date' in company['fields'] else None,
                "job_listings_xpath": company['fields']['job_listings_xpath'] if 'job_listings_xpath' in company['fields'] else None,
                "job_url_xpath": company['fields']['job_url_xpath'] if 'job_url_xpath' in company['fields'] else None,
                "job_title_xpath": company['fields']['job_title_xpath'] if 'job_title_xpath' in company['fields'] else None,
                "job_details_xpath": company['fields']['job_details_xpath'] if 'job_details_xpath' in company['fields'] else None,
                "next_btn_xpath": company['fields']['next_btn_xpath'] if 'next_btn_xpath' in company['fields'] else None,
                "investors": company['fields']['investors'] if 'investors' in company['fields'] else None,
                "hq_country": company['fields']['hq_country'] if 'hq_country' in company['fields'] else None

            })

        else:
            pass
            # print(f"removed {company['fields']['Name']}")
    return(all_companies)


def get_one_company(company_name):
    all_companies = []
    airtable = set_airtable_config('companies')
    formula = match({"name": company_name})
    response = airtable.first(formula=formula)
    return(response)


