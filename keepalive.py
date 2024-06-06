from flask import Flask, send_file, jsonify, request
from threading import Thread
import json, shutil, requests

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Hello!</h1>"
  
#@app.route("/fox")
def get_fox():
    res = requests.get("https://randomfox.ca/floof")
    content = json.loads(res.content)
    print(content)
    image = requests.get(content["image"], stream=True)
    if image.status_code == 200:
        image.raw.decode_content = True
        with open("fox.jpg", "wb") as f:
            shutil.copyfileobj(image.raw, f)
    return send_file("fox.jpg", mimetype="image/jpeg")

@app.route("/content", methods=['POST'])
def jsonify_content():
    url = request.get_json(True)
    res = requests.get(url['url'])
    content = res.content.decode()
    return jsonify({'content': content})

def run():
  app.run(host='0.0.0.0',port=5000)

def keep_alive():
    t = Thread(target=run)
    t.start()
    
if __name__ == "__main__":
    run()