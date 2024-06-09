from .utils.set_fmp_config import set_fmp_config
import fmpsdk

# https://site.financialmodelingprep.com/developer/docs/dashboard
# https://pypi.org/project/fmpsdk/

def test_fmp():
    apikey = set_fmp_config()
    symbol: str = "AAPL"
    tickers: list = ["AAPL"]
    profiles = fmpsdk.income_statement_growth(apikey=apikey, symbol=symbol)
    for profile in profiles:
        print(profile)
    # symbols = fmpsdk.symbols_list(apikey=apikey)
    # uscompanies = []
    # for symbol in symbols:
    #     if symbol['exchangeShortName'] == 'NYSE' or symbol['exchangeShortName'] == 'NASDAQ':
    #         uscompanies.append(symbol)
    # print(len(uscompanies))