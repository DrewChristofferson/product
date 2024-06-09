from dotenv import load_dotenv
import os



def set_fmp_config():
    load_dotenv(".env")
    apikey=os.environ.get("FMP_API_KEY")
    return(apikey)

