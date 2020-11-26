import sys
import time
import socket


import keyboard
import pyautogui
import json

import requests



def add_fish(name):
    pass


def getCoords():
    while True:
        try:
            if keyboard.is_pressed('alt'):
                return pyautogui.position()
        except:
            break

def account_status(token):
    url = "http://139.59.128.182/api/fishbot/check/{}/".format(token)
    request = requests.get(url)
    response = json.loads(request.text)
    return response

def start_program(token, stop_event, stop_fishing):
    url = "http://139.59.128.182/api/fishbot/check/{}/".format(token)
    data = "start"
    request = requests.get(url, data=data)
    response = json.loads(request.text)
    i = 0
    if not response["sub_status"]:
        stop_fishing.set()
        stop_event.set()
    while not stop_event.isSet():
        time.sleep(3)
        if i % 100 == 0:
            url = "http://139.59.128.182/api/fishbot/{}/".format(token)
            hostname = socket.gethostname()
            ip = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [
                [(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in
                 [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]
            data = "{}_{}".format(ip, hostname)

            request = requests.get(url, data=data)
            response = json.loads(request.text)
            if not response["status"]:
                stop_fishing.set()
                stop_event.set()
        i += 1


def stop_program(token):
    url = "http://139.59.128.182/api/fishbot/check/{}/".format(token)
    data = "stop"
    request = requests.get(url, data=data)
    response = json.loads(request.text)
    if not response["sub_status"]:
        sys.exit(0)


def send_telegram_message(bot_message, chat_id):
    url = "http://139.59.128.182/api/fishbot/telegram_token/"
    request = requests.get(url)
    response = json.loads(request.text)
    bot_token = "865299523:{}".format(response["token"])
    bot_chat_id = str(chat_id)
    api_url = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chat_id + '&parse_mode=Markdown&text=' + str(bot_message)
    requests.get(api_url)
