import requests

def is_valid_code(code: int) -> bool:
    if (code < 100 or code > 599):
        return False
    if (code <= 103):
        return True
    if (code >= 200 and code <= 208):
        return True
    if (code in {214, 226}):
        return True
    if (code >= 300 and code <= 308 and code != 306):
        return True
    if (code >= 400 and code <= 431 and code != 427):
        return True
    if (code in {444, 450, 451}):
        return True
    if (code >= 495 and code <= 511 and code != 505):
        return True
    if (code in {521, 522, 523, 525, 530, 599}):
        return True
    return False  

def __get_cat_raw(cat: int) -> bytes:
    res = requests.get(f"https://http.cat/{cat}.jpg")
    if (res.status_code == 200):
        return res.content
    else:
        raise ConnectionError(res)

def get_cat(cat: int) -> bytes|str:
    if (is_valid_code(cat)):
        return __get_cat_raw(cat)
    else:
        return "Not a valid code!"