from openai import OpenAI
from dotenv import load_dotenv
import os



def set_open_config():
    load_dotenv(".env")
    client = OpenAI(
    api_key=os.environ.get("CUSTOM_ENV_NAME"),
    )
    return(client)
