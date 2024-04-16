from flask import Flask, render_template
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Hello!</h1>"

def run():
  app.run(host='0.0.0.0',port=8000)

def keep_alive():
    t = Thread(target=run)
    t.start()