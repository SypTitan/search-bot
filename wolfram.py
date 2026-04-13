import requests
import dotenv

from os import environ

dotenv.load_dotenv()

APP_ID = environ.get("WOLFRAM_APP_ID")

def get_answer(query: str) -> str:
    BASE_URL = "http://api.wolframalpha.com/v1/result"
    
    BASE_PARAMS = {
        "appid": APP_ID,
        "units": "metric",
    }
    
    BASE_PARAMS["i"] = query
    
    result = requests.get(BASE_URL, params=BASE_PARAMS)
    
    if (result.status_code == 200):
        return result.content.decode()
    else:
        return f"Failed to get answer: {result.content.decode()}"