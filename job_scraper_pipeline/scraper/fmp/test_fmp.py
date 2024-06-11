from .utils.set_fmp_config import set_fmp_config
import fmpsdk
from ..db_requests.update_company import update_company
from ..db_requests.get_companies import pull_companies

# https://site.financialmodelingprep.com/developer/docs/dashboard
# https://pypi.org/project/fmpsdk/

def test_fmp():
    companies = pull_companies()
    for company in companies:
        name_uppercase = company['name'].upper()
        print(name_uppercase, name_uppercase[0], name_uppercase[0] > 'D')
        if name_uppercase[0] > 'F' and company['ticker_symbol']:
            apikey = set_fmp_config()
            profiles = fmpsdk.quote(apikey=apikey, symbol=company['ticker_symbol'])
            for profile in profiles:
                mktcap = profile['marketCap']
                print(mktcap)
                update_company(company['airtable_id'], { 'market_cap': mktcap})
    # symbols = fmpsdk.symbols_list(apikey=apikey)
    # uscompanies = []
    # for symbol in symbols:
    #     if symbol['exchangeShortName'] == 'NYSE' or symbol['exchangeShortName'] == 'NASDAQ':
    #         uscompanies.append(symbol)
    # print(len(uscompanies))
