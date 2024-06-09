from .utils.set_airtable_configs import set_airtable_config
from pyairtable.formulas import match


def pull_investors():
    airtable = set_airtable_config('investors')
    response = airtable.all(
        sort=["name"], 
        fields=[
            "name"
        ])
    return(response)