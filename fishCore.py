import json
import os
import sys
import time
from datetime import datetime
from random import randrange

import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab
import requests
from utils import send_telegram_message
import config


class Statistic:
    def __init__(self):
        self.FISH = config.getAllFish()
        self.start = time.time()
        self.stat = {"start": str(datetime.now()), "All fish": 0, "Fishing time": "", "Fish per minute": 0}
        for fish in self.FISH:
            self.stat[fish[0]] = 0

    def show(self):
        self.stat["Fish per minute"] = float(self.stat["All fish"]) / round(((time.time() - self.start) / 60), 2)
        return self.stat

    def add(self, key):
        self.stat[key] += 1

    def final(self):
        time.sleep(0.5)
        self.stat["Fishing time"] = str(round(((time.time() - self.start) / 60), 2)) + " min"
        self.stat["Fish per minute"] = float(self.stat["All fish"]) / round(((time.time() - self.start) / 60), 2)
        return json.dumps(self.stat, indent=4)

class FishCore:
    def __init__(self):
        pointA, pointB = config.getSettingsValue("fish_area").split("//")
        Ax, Ay = pointA.split(",")
        Bx, By = pointB.split(",")
        self.BOX_ANGLE_LEFT = (int(Ax), int(Ay))
        self.BOX_ANGLE_RIGHT = (int(Bx), int(By))
        self.get_classifier()
        # self.cascade = cv2.CascadeClassifier("D:\\cascade.xml")
        self.cascade = cv2.CascadeClassifier("bin")
        self.delete_classifier()
        self.POLE_BUTTON = config.getSettingsValue("pole_button")
        self.BAIT_BUTTON = config.getSettingsValue("bait_button")
        self.POLE_CORD = config.getSettingsValue("pole_cords").split(",")
        self.DIFF = 6.5
        self.FISH_CORD = config.getSettingsValue("fish_cords").split(",")
        self.FISH = config.getAllFish()
        self.DL_CORDS = config.getSettingsValue("death_leave_cords").split(",")
        self.LAST_BACKPACK_SLOT_CORD = config.getSettingsValue("last_backpack_slot").split(",")
        self.BOT_MESSAGE = config.getSettingsValue("telegram_message")
        self.CHAT_ID = config.getSettingsValue("chat_id")
        self.FULL_BACKPACK_COLOR = config.getSettingsValue("full_backpack_color").split(",")
        if config.getSettingsValue("is_death_leave") == "True":
            self.IS_DL = True
        else:
            self.IS_DL = False
        if config.getSettingsValue("update_pole") == "True":
            self.UPDATE_POLE = True
        else:
            self.UPDATE_POLE = False
        if config.getSettingsValue("is_full_backpack_active") == "True":
            self.IS_FULL_BACKPACK_ACTIVE = True
        else:
            self.IS_FULL_BACKPACK_ACTIVE = False

    def get_classifier(self):
        url = "http://localhost:8000/api/classifier/download/"
        r = requests.get(url, allow_redirects=True)
        open("bin", 'wb').write(r.content)

    def delete_classifier(self):
        open("bin", 'w').write("What are u want to see here EBANAT? Brat prekraschai huinei zanimaza, ya tvoei materi v zopy piva nal'y i vip'u ottuda ti sin blyadi ebanoi, dermoed nahui konchenni ")
        os.remove("bin")

    def classifier(self):
        image = ImageGrab.grab(
            bbox=(self.BOX_ANGLE_LEFT[0], self.BOX_ANGLE_LEFT[1], self.BOX_ANGLE_RIGHT[0], self.BOX_ANGLE_RIGHT[1]))
        image.save('screen.jpg')
        image = cv2.imread("screen.jpg")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        pole = self.cascade.detectMultiScale(gray, 1.3, 5, minSize=(10, 10), maxSize=(80, 80),
                                             flags=cv2.CASCADE_SCALE_IMAGE)
        for (x, y, w, h) in pole:
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
            # cv2.imshow("img", image)
            return (int(self.BOX_ANGLE_LEFT[0] + x), int(self.BOX_ANGLE_LEFT[1] + y), w, h)
        return None

    def update_pole(self):
        pyautogui.keyDown(str(self.POLE_BUTTON))
        time.sleep(randrange(50, 100) / 100)
        pyautogui.keyUp(str(self.POLE_BUTTON))
        time.sleep(randrange(50, 100) / 100)
        pyautogui.keyDown(str(self.BAIT_BUTTON))
        time.sleep(randrange(50, 100) / 100)
        pyautogui.keyUp(str(self.BAIT_BUTTON))
        time.sleep(randrange(50, 100) / 100)
        pyautogui.moveTo(int(self.POLE_CORD[0]), int(self.POLE_CORD[1]))
        time.sleep(randrange(80, 150) / 100)
        pyautogui.click(button='right')
        time.sleep(randrange(1000, 1500) / 100)
        time.sleep(randrange(10, 50) / 100)
        return time.time()

    def isAlive(self):
        image = ImageGrab.grab()
        r, g, b = image.getpixel((int(self.DL_CORDS[0]), int(self.DL_CORDS[1])))
        return False if r == 255 else True

    def isFullBackpack(self):
        image = ImageGrab.grab()
        r, g, b = image.getpixel((int(self.LAST_BACKPACK_SLOT_CORD[0]), int(self.LAST_BACKPACK_SLOT_CORD[1])))
        if (str(r), str(g), str(b)) == tuple(self.FULL_BACKPACK_COLOR):
            return False
        return True

    def stop(self):
        image = ImageGrab.grab()
        r, g, b = image.getpixel((int(self.DL_CORDS[0]), int(self.DL_CORDS[1])))
        if r == 255 or r != 0:
            return True
        r, g, b = image.getpixel((int(self.LAST_BACKPACK_SLOT_CORD[0]), int(self.LAST_BACKPACK_SLOT_CORD[1])))
        if (str(r), str(g), str(b)) == tuple(self.FULL_BACKPACK_COLOR):
            return False
        return True

    def run(self, stop_event, stop_event2, statistic):
        last_update_pole = 0
        fish_try = 0
        while not stop_event.isSet():
            if time.time() - last_update_pole > 630 and self.UPDATE_POLE:
                last_update_pole = self.update_pole()
            time.sleep(1)
            if fish_try > 10:
                send_telegram_message("We cannot fishing but still trying. Check for your computer", self.CHAT_ID)
                send_telegram_message(self.BOT_MESSAGE, self.CHAT_ID)

            if self.IS_DL or self.IS_FULL_BACKPACK_ACTIVE:
                if not self.stop():
                    send_telegram_message(self.BOT_MESSAGE, self.CHAT_ID)
                    send_telegram_message(str(statistic.final()), self.CHAT_ID)
                    stop_event.set()
                    stop_event2.set()
                    break

            average = [0, ]
            pyautogui.keyDown(str(self.POLE_BUTTON))
            time.sleep(0.1)
            pyautogui.keyUp(str(self.POLE_BUTTON))
            time.sleep(2)
            cords = self.classifier()

            if cords is not None:
                fish_try = 0
                fishing_time = time.time()
                screen = ImageGrab.grab(bbox=(cords[0], cords[1], cords[0] + cords[2], cords[1] + cords[3]))
                mean = np.mean(screen)
                average.append(mean)
                while (time.time() - fishing_time) < 31:
                    screen = ImageGrab.grab(bbox=(cords[0], cords[1], cords[0] + cords[2], cords[1] + cords[3]))
                    mean = np.mean(screen)
                    diff = abs(average[-1] - mean)
                    if diff >= self.DIFF:
                        statistic.add("All fish")
                        # config.increaseFishValue("All fish")
                        pyautogui.moveTo(int(cords[0] + int(cords[2] / 2)), int(cords[1] + int(cords[3] / 2)))
                        pyautogui.click(button='right', clicks=1, interval=0.2)
                        time.sleep(1)
                        image2 = ImageGrab.grab()
                        for i in self.FISH:
                            fish_cord = (int(i[1]), int(i[2]), int(i[3]))
                            if image2.getpixel((int(self.FISH_CORD[0]), int(self.FISH_CORD[1]))) == fish_cord:
                                pyautogui.moveTo(int(self.FISH_CORD[0]), int(self.FISH_CORD[1]))
                                statistic.add(i[0])
                                pyautogui.click(button='right', clicks=1, interval=0.2)
                        break
            else:
                fish_try += 1
