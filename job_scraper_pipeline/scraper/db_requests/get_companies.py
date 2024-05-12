from .utils.set_airtable_configs import set_airtable_config
from pyairtable.formulas import match


def pull_companies():
    all_companies = []
    airtable = set_airtable_config('companies')
    # formula = match({"Name": "Apple"})
    response = airtable.all(sort=["Name"], fields=["Name", "linkedin_id", "is_inactive", "Last Scrape Date", "Careers Page URL"])
    for company in response:
        if 'is_inactive' not in company['fields']:
            response = all_companies.append({
                "name": company['fields']['Name'],
                "airtable_id": company['id'],
                "linkedin_id": company['fields']['linkedin_id'] if 'linkedin_id' in company['fields'] else None,
                "careers_page_url": company['fields']['Careers Page URL'] if 'Careers Page URL' in company['fields'] else None,
                "Last Scrape Date": company['fields']['Last Scrape Date'] if 'Last Scrape Date' in company['fields'] else None
            })

        else:
            pass
            # print(f"removed {company['fields']['Name']}")
    return(all_companies)