import json

def read() -> dict:
    try:
        with open('storage.json') as storagejson:
            data = storagejson.read()
            if (len(data) == 0):
                storage = {}
            else:
                storage = json.loads(data)
        return storage
    except FileNotFoundError:
        file = open('storage.json', 'x')
        file.close()
        return {}

def write(storage: dict) -> None:
    try:
        with open('storage.json', 'w') as file:
            json.dump(storage, file)
    except FileNotFoundError:
        with open('storage.json', 'x') as file:
            json.dump(storage, file)