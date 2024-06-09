from pyairtable import Api
from pyairtable.formulas import match
from dotenv import load_dotenv
import os

def set_airtable_config(table):
    AIRTABLE_BASE_ID = 'appT4TIFvWbwAQ35G'
    AIRTABLE_COMPANIES_TABLE_ID = 'tblGwlPqq03yEQjV1'
    AIRTABLE_JOBS_TABLE_ID = 'tbliHYwp5pTrRxqJk'
    AIRTABLE_INVESTORS_TABLE_ID = 'tblyBpDbT7x1nQSho'

    if "airtable_api_key" in os.environ:
        #get github env var
        API_KEY = os.environ["airtable_api_key"] 
    else:
        # Load local env var from .env file
        load_dotenv(".env")
        API_KEY = os.getenv("AIRTABLE_API_KEY")

    airtable_api_key = Api(API_KEY)
    if table == 'companies':
        table_id = AIRTABLE_COMPANIES_TABLE_ID
    elif table == 'jobs':
        table_id = AIRTABLE_JOBS_TABLE_ID
    elif table == 'investors':
        table_id = AIRTABLE_INVESTORS_TABLE_ID
    else:
        table_id = None
    airtable_table = airtable_api_key.table(AIRTABLE_BASE_ID, table_id)
    return(airtable_table)
