import requests
import urllib.parse
from enum import Enum

class Ecc(str, Enum):
    Low = 'L'
    Medium = 'M'
    Quality = 'Q'
    High = 'H'
    
class Formats(str, Enum):
    png = 'png'
    gif = 'gif'
    jpeg = 'jpeg'
    jpg = 'jpg'
    svg = 'svg'
    eps = 'eps'
    
def test_url(link: str) -> bool:
    try:
        output = requests.get(link)
        if (output.status_code == 404):
            return False
        return True
    except:
        print("Test failed: "+link)
        return False
    

def format_link(link: str) -> str:
    if (link.startswith("http://") or link.startswith("https://")):
        return urllib.parse.quote(link)
    else:
        return "https://"+urllib.parse.quote(link)

def __get_qr_raw(data: str, size: int = 400, **kwargs) -> bytes:
    if ('format' in kwargs and kwargs['format'] in Formats):
        imageformat = kwargs['format']
    else:
        imageformat = Formats.png
    if ('ecc' in kwargs and kwargs['ecc'] in Ecc):
        ecc = kwargs['ecc']
    else:
        ecc = Ecc.Low
    if (size > 1000):
        size = 1000
    if (size < 10):
        size = 10
    if ('margin' in kwargs and type(kwargs['margin']) == int):
        margin = kwargs['margin']
        if (margin < 0):
            margin = 0
        if (margin > 50):
            margin = 50
    else:
        margin = 1
    size = str(size)+'x'+str(size)
    
    parameters = {'data': data, 'size': size, 'ecc': ecc, 'format': imageformat, 'margin': margin}
    
    output = requests.post("https://api.qrserver.com/v1/create-qr-code", params=parameters)
    if (output.status_code != 200):
        raise ConnectionError(output.content)
    return output.content

def get_qr(url: str, size: int = 400, **kwargs) -> bytes:
    if (type(url) == str):
        url = format_link(url)
    else:
        raise TypeError("Please use a string for data")
    return __get_qr_raw(url, size, **kwargs)