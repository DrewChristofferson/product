from .utils.set_airtable_configs import set_airtable_config
from pyairtable.formulas import match


def pull_companies():
    all_companies = []
    airtable = set_airtable_config('companies')
    formula = match({"Name": "Zoom"})
    response = airtable.all(formula=formula, sort=["Name"], fields=["Name", "linkedin_id", "is_inactive", "Last Scrape Date"])
    for company in response:
        if 'linkedin_id' in company['fields'] and 'is_inactive' not in company['fields']:
            all_companies.append({
                "name": company['fields']['Name'],
                "linkedin_id": company['fields']['linkedin_id'],
                "airtable_id": company['id'],
                "Last Scrape Date": company['fields']['Last Scrape Date'] if 'Last Scrape Date' in company['fields'] else None
            })
        else:
            pass
            # print(f"removed {company['fields']['Name']}")
    return(all_companies)