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
import imagehash


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
        try:
            pointA, pointB = config.getSettingsValue("fish_area").split("//")
            Ax, Ay = pointA.split(",")
            Bx, By = pointB.split(",")
            self.BOX_ANGLE_LEFT = (int(Ax), int(Ay))
            self.BOX_ANGLE_RIGHT = (int(Bx), int(By))
        except:
            self.BOX_ANGLE_LEFT = (1, 1)
            self.BOX_ANGLE_RIGHT = (1, 1)
            print("BOX_ANGLE_LEFT/BOX_ANGLE_RIGHT error")
        self.MOVE_TO = config.getSettingsValue("move_to")
        self.IS_MOVE_TO = True if config.getSettingsValue("move_to") != "" else False
        self.get_classifier()
        self.BAIT_SIZE = 35 if config.getSettingsValue("bait_size") == "" else int(config.getSettingsValue("bait_size"))
        if config.getSettingsValue("bait_size") == "":
            self.CUSTOM_BAITSIZE = False
        else:
            self.CUSTOM_BAITSIZE = True
        # self.cascade = cv2.CascadeClassifier("D:\\cascade.xml")
        self.cascade = cv2.CascadeClassifier("bin")
        self.delete_classifier()
        self.POLE_BUTTON = config.getSettingsValue("pole_button")
        if self.POLE_BUTTON == "":
            self.POLE_BUTTON = "1"
        self.BAIT_BUTTON = config.getSettingsValue("bait_button")
        if self.BAIT_BUTTON == "":
            self.BAIT_BUTTON = "9"
        try:
            self.POLE_CORD = config.getSettingsValue("pole_cords").split(",")
        except:
            self.POLE_CORD = [1, 1]
            print("POLE CORD not set")
        if config.getSettingsValue("new_ver") == "True":
            self.IS_NEW_VERSION = True
        else:
            self.IS_NEW_VERSION = False
        self.DIFF = 7 if config.getSettingsValue("diff") == "" else float(config.getSettingsValue("diff"))
        try:
            self.FISH_CORD = config.getSettingsValue("fish_cords").split(",")
        except:
            self.FISH_CORD = [1, 1]
            print("FISH_CORD not set")
        self.FISH = config.getAllFish()
        try:
            self.DL_CORDS = config.getSettingsValue("death_leave_cords").split(",")
        except:
            self.DL_CORDS = [1, 1]
            print("Death/leave_CORDS not set")
        try:
            self.LAST_BACKPACK_SLOT_CORD = config.getSettingsValue("last_backpack_slot").split(",")
        except:
            self.LAST_BACKPACK_SLOT_CORD = [1, 1]
            print("LAST_BACKPACK_SLOT_CORD not set")
        self.BOT_MESSAGE = config.getSettingsValue("telegram_message")
        self.CHAT_ID = config.getSettingsValue("chat_id")
        try:
            self.FULL_BACKPACK_COLOR = config.getSettingsValue("full_backpack_color").split(",")
        except:
            self.FULL_BACKPACK_COLOR = ("1", "1", "1")
            print("FULL_BACKPACK_COLOR not set")
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
        url = "http://139.59.128.182/api/classifier/download/"
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
        if self.IS_DL:
            if r != 255 and r != 0:
                return True
        if self.IS_FULL_BACKPACK_ACTIVE:
            r, g, b = image.getpixel((int(self.LAST_BACKPACK_SLOT_CORD[0]), int(self.LAST_BACKPACK_SLOT_CORD[1])))
            if (str(r), str(g), str(b)) != tuple(self.FULL_BACKPACK_COLOR):
                return True
        return False

    def run(self, stop_event, stop_event2, statistic):
        last_update_pole = 0
        fish_try = 0
        while not stop_event.isSet():
            if time.time() - last_update_pole > 630 and self.UPDATE_POLE:
                last_update_pole = self.update_pole()
            time.sleep(1)
            if fish_try > 30:
                fish_try = 0
                send_telegram_message("We cannot fishing but still trying. Check for your computer", self.CHAT_ID)
                send_telegram_message(self.BOT_MESSAGE, self.CHAT_ID)

            if self.IS_DL or self.IS_FULL_BACKPACK_ACTIVE:
                # print(1)
                if self.stop():
                    # print(2)
                    send_telegram_message(self.BOT_MESSAGE, self.CHAT_ID)
                    send_telegram_message(str(statistic.final()), self.CHAT_ID)
                    try:
                        stop_event.set()
                        stop_event2.set()
                    except:
                        pass
                    break

            average = [0, ]
            pyautogui.keyDown(str(self.POLE_BUTTON))
            time.sleep(0.1)
            pyautogui.keyUp(str(self.POLE_BUTTON))
            time.sleep(2)
            if self.IS_NEW_VERSION:
                cords = self.classifier()

            else:
                x = 0
                y = 0
                image = ImageGrab.grab(
                    bbox=(self.BOX_ANGLE_LEFT[0], self.BOX_ANGLE_LEFT[1], self.BOX_ANGLE_RIGHT[0], self.BOX_ANGLE_RIGHT[1]))
                image.save('screen.jpg')
                image = cv2.imread("screen.jpg")
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (3, 3), 0)

                edged = cv2.Canny(gray, 10, 250)

                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
                closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)

                cnts, _ = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                total = 0
                for i in range(3, 30):
                    total = 0
                    if total != 1:
                        for c in cnts:
                            peri = cv2.arcLength(c, True)
                            approx = cv2.approxPolyDP(c, 0.06 * peri, True)

                            if len(approx) == i:
                                total += 1

                    if total == 1:
                        for c in cnts:
                            peri = cv2.arcLength(c, True)
                            approx = cv2.approxPolyDP(c, 0.06 * peri, True)
                            if len(approx) == i:
                                cv2.drawContours(image, [approx], -1, (255, 255, 0), 4)
                                x = 0
                                y = 0
                                for k in range(len(approx)):
                                    x = x + approx[k][0][0]
                                    y = y + approx[k][0][1]
                                x = int(x / len(approx)) + self.BOX_ANGLE_LEFT[0]
                                y = int(y / len(approx)) + self.BOX_ANGLE_LEFT[1]
                        break
                cords = [x, y, x + int(self.BAIT_SIZE), y + int(self.BAIT_SIZE)]

            if cords is not None and cords[0] != 0:
                if self.CUSTOM_BAITSIZE:
                    cords = [cords[0], cords[1],self.BAIT_SIZE,self.BAIT_SIZE]
                fish_try = 0
                fishing_time = time.time()
                screen = ImageGrab.grab(bbox=(cords[0], cords[1], cords[0] + cords[2], cords[1] + cords[3]))
                hash = imagehash.average_hash(screen)
                mean = np.mean(screen)
                average.append(mean)
                while (time.time() - fishing_time) < 31:
                    screen = ImageGrab.grab(bbox=(cords[0], cords[1], cords[0] + cords[2], cords[1] + cords[3]))
                    mean = np.mean(screen)
                    otherhash = imagehash.average_hash(screen)
                    # print("hash", hash - otherhash)
                    diff = abs(average[-1] - mean)
                    # print("diff", diff)
                    if diff >= self.DIFF:
                    # if hash - otherhash >= 8:
                    #     print("click")
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
                if self.IS_MOVE_TO:
                    try:
                        x, y = self.MOVE_TO.split(",")
                        pyautogui.moveTo(int(x), int(y))
                    except:
                        pass
            else:
                fish_try += 1
