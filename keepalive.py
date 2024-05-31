from flask import Flask, send_file
from threading import Thread
import json, shutil, requests

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Hello!</h1>"
  
@app.route("/fox")
def get_fox():
    res = requests.get("https://randomfox.ca/floof")
    content = json.loads(res.content)
    image = requests.get(content["image"], stream=True)
    if image.status_code == 200:
        image.raw.decode_content = True
        with open("fox.jpg", "wb") as f:
            shutil.copyfileobj(image.raw, f)
    return send_file("fox.jpg", mimetype="image/jpeg")


def run():
  app.run(host='0.0.0.0',port=8000)

def keep_alive():
    t = Thread(target=run)
    t.start()