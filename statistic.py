
from datetime import datetime
import json


def add(name):
    with open("statistic.txt", "a") as stat:
        stat.write(str(name) + "//" + str(datetime.now().strftime("%d/%m/%Y\\%H:%M:%S")) + "\n")

add(2)