from datetime import datetime, timedelta
from .utils.set_airtable_configs import set_airtable_config

def log_company_scrape(airtable_company_id):
    airtable_table = set_airtable_config('companies')
    response = airtable_table.update(
        airtable_company_id, 
        {
            "Last Scrape Date": datetime.today().isoformat()
        }, 
        typecast=True
    )
