import requests
import datetime as dt
import json
import jsonstorage as storage
from enum import Enum

universal_headers = {'User-Agent': 'Appie/8.22.3','Content-Type': 'application/json'}

class Sorts(str, Enum):
    Relevance = "RELEVANCE"
    PriceAscending = "PRICELOWHIGH"
    PriceDescending = "PRICEHIGHLOW"
    Nutriscore = "NUTRISCORE"

def __fetch_new_token() -> tuple[str,dt.datetime,str]:
    token = requests.post("https://api.ah.nl/mobile-auth/v1/auth/token/anonymous", headers=universal_headers, json={'clientId':'appie'})
    if (token.status_code == 200):
        content = json.loads(token.content)
        expiry_time = dt.datetime.now() + dt.timedelta(seconds=content['expires_in'])
        return content['access_token'], expiry_time, content['refresh_token']
    else:
        raise ConnectionError(token)
    
def get_token() -> tuple[str,int,str]:
    stored = storage.read()
    if ('ah_token' in stored):
        if is_token_expired(stored['ah_token']):
            print("Token expired, fetching new token")
            token = __fetch_new_token()
            fixedtoken = list(token)
            fixedtoken[1] = int(fixedtoken[1].timestamp())
            stored['ah_token'] = tuple(fixedtoken)
            storage.write(stored)
        return stored['ah_token']
    else:
        print("No token stored, fetching new token")
        token = __fetch_new_token()
        fixedtoken = list(token)
        fixedtoken[1] = int(fixedtoken[1].timestamp())
        stored['ah_token'] = tuple(fixedtoken)
        storage.write(stored)
        return stored['ah_token']
    
def is_token_expired(token: tuple[str,int,str]) -> bool:
    return dt.datetime.fromtimestamp(token[1]) < dt.datetime.now()
    
def __get_search_raw(token: str, query: str, sort: str = Sorts.Relevance) -> dict:
    assert(sort in Sorts)
    if (type(token) != str):
        if(type(token) in [tuple,list] and type(token[0]) == str):
            token = token[0]
        else:
            raise TypeError("Please use a string for token")
    headers = universal_headers
    headers['Authorization'] = 'Bearer ' + token
    headers['X-Application'] = 'AHWEBSHOP'
    params = {'query': query, 'sortOn': sort}
    search = requests.get("https://api.ah.nl/mobile-services/product/search/v2", headers=headers, params=params)
    if (search.status_code == 200):
        return search.content
    else:
        raise ConnectionError(search)
    
def get_search(token: str, query: str, sort: str = Sorts.Relevance) -> list:
    search = __get_search_raw(token, query, sort)
    search = json.loads(search)
    return search['products']