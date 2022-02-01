#  Author: Ilya Polotsky (ipolo.box@gmail.com). Copyright (c) 2022.
import threading

from time import sleep
from flask import Flask
from main import get_updater

c = threading.Condition()

app = Flask("Flask")
print("Server is running")


@app.route('/')
def hello():
    updater = get_updater()
    c.acquire()
    updater.bot.send_message(75771603, "Привет, красавчик 6!")
    sleep(6)
    updater.bot.send_message(75771603, "6 secs finished")
    c.notify_all()
    c.release()
    return 'Hello, World 6!'


@app.route('/8')
def hello8():
    updater = get_updater()
    c.acquire()
    updater.bot.send_message(75771603, "Привет, красавчик 8!")
    sleep(8)
    updater.bot.send_message(75771603, "8 secs finished")
    c.notify_all()
    c.release()
    return 'Hello, World 8!'

def run_server():
    app.run(host="0.0.0.0")
