from openai import OpenAI
from dotenv import load_dotenv
import os



def set_open_config():
    if "openai_api_key" in os.environ:
        #get github env var
        API_KEY = os.environ["openai_api_key"] 
    else:
        # Load local env var from .env file
        load_dotenv(".env")
        API_KEY = os.getenv("OPENAI_API_KEY")
    
    client = OpenAI(api_key=API_KEY,)
    return(client)
