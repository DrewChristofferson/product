from .utils.set_airtable_configs import set_airtable_config
from pyairtable.formulas import match

FIELDS_TO_RETURN = [
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
            "hq_country",
            "ticker_symbol",
            "estimated_revenue",
            "total_funding",
            "company_valuation",
            "office_locations",
            "num_employees",
            "logo",
            "Industry Name",
            "Count of Jobs"
        ]

def pull_companies(companies_filter=None):
    if companies_filter and len(companies_filter) < 1:
        companies_filter = None
    all_companies = []
    all_companies_raw = []
    airtable = set_airtable_config('companies')
    if companies_filter is None:
        print('here')
        response = airtable.all(
            # sort=["-Count of Jobs"], 
            sort=["name"],
            fields=FIELDS_TO_RETURN
            )
        all_companies_raw = response
    elif len(companies_filter) == 1:
        formula = match({"name": companies_filter[0]})
        response = airtable.all(
            formula=formula,
            fields=FIELDS_TO_RETURN
            )
        all_companies_raw = response
    elif len(companies_filter) > 1:
        response = airtable.all(
            sort=["name"], 
            fields=FIELDS_TO_RETURN
            )
        for company in response:
            if company['fields']['name'] in companies_filter:
                all_companies_raw.append(company)
    else:
        print("Invalid company filter")
        return
    for company in all_companies_raw:
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
                "hq_country": company['fields']['hq_country'] if 'hq_country' in company['fields'] else None,
                "ticker_symbol": company['fields']['ticker_symbol'] if 'ticker_symbol' in company['fields'] else None,
                "estimated_revenue": company['fields']['estimated_revenue'] if 'estimated_revenue' in company['fields'] else None,
                "total_funding": company['fields']['total_funding'] if 'total_funding' in company['fields'] else None,
                "company_valuation": company['fields']['company_valuation'] if 'company_valuation' in company['fields'] else None,
                "office_locations": company['fields']['office_locations'] if 'office_locations' in company['fields'] else None,
                "num_employees": company['fields']['num_employees'] if 'num_employees' in company['fields'] else None,
                "logo": company['fields']['logo'] if 'logo' in company['fields'] else None,
                "Industry Name": company['fields']['Industry Name'] if 'Industry Name' in company['fields'] else None,
                "Count of Jobs": company['fields']['Count of Jobs'] if 'Count of Jobs' in company['fields'] else None            })

        else:
            pass
            # print(f"removed {company['fields']['Name']}")
    # print(all_companies)
    return(all_companies)


def get_one_company(company_name):
    all_companies = []
    airtable = set_airtable_config('companies')
    formula = match({"name": company_name})
    response = airtable.first(formula=formula)
    return(response)



