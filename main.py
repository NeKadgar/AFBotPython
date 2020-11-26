import threading
import time
from threading import Thread

from PIL import ImageGrab
from PyQt5 import QtWidgets
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from ui import Ui_MainWindow  # импорт нашего сгенерированного файла
import sys
import config
import pyautogui
import fishCore
from utils import account_status, getCoords, start_program, stop_program, send_telegram_message


class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Fish bot")
        self.ui.toolButton_11.clicked.connect(self.saveFunc)
        self.ui.toolButton_2.clicked.connect(self.setFishAreaTopLeft)
        self.ui.toolButton.clicked.connect(self.setFishAreaDownRight)
        self.ui.toolButton_3.clicked.connect(self.setFishCords)
        self.ui.toolButton_4.clicked.connect(self.setLastBackpackCords)
        self.ui.toolButton_6.clicked.connect(self.setPoleCords)
        self.ui.toolButton_12.clicked.connect(self.setDeathLeaveCord)
        self.ui.toolButton_9.clicked.connect(self.addFishColor)
        self.ui.toolButton_10.clicked.connect(self.deleteFish)
        self.ui.pushButton.clicked.connect(self.startFishing)
        self.ui.pushButton_2.clicked.connect(self.stopFishing)
        self.ui.toolButton_5.clicked.connect(self.setFullBackpackColor)
        self.model = QStandardItemModel(self)
        self.ui.listView.setModel(self.model)
        self.showSavedSettings()
        self.p = ""
        self.q = ""
        self.statistic = ""

    def showSavedSettings(self):
        try:
            x, y = config.getSettingsValue("move_to").split(",")
            self.ui.lineEdit_21.setText(y)
            self.ui.lineEdit_22.setText(x)
        except:
            pass
        try:
            res = account_status(config.getSettingsValue("token"))
        except:
            res = {"sub_status": "Token pls", "sub_time": "None"}
        self.ui.label_30.setText("Subscription status: {}".format(res["sub_status"]))
        self.ui.label_31.setText("To: {}".format(res["sub_time"]))
        self.ui.lineEdit.setText(config.getSettingsValue("token"))
        self.ui.lineEdit_2.setText(config.getSettingsValue("chat_id"))
        self.ui.lineEdit_19.setText(config.getSettingsValue("bait_size"))
        self.ui.lineEdit_20.setText(config.getSettingsValue("diff"))
        try:
            self.ui.label_20.setText("Current color ({}, {}, {})".format(*config.getSettingsValue("full_backpack_color").split(",")))
            #full_backpack_color
        except:
            pass
        for fish in config.getAllFish():
            item = QStandardItem("{} >> ({}, {} ,{})".format(*fish))
            item.setCheckable(True)
            self.model.appendRow(item)
        if config.getSettingsValue("is_full_backpack_active") == "True":
            self.ui.checkBox.setChecked(True)
        if config.getSettingsValue("new_ver") == "True":
            self.ui.checkBox_4.setChecked(True)
        if config.getSettingsValue("update_pole") == "True":
            self.ui.checkBox_2.setChecked(True)
        if config.getSettingsValue("is_death_leave") == "True":
            self.ui.checkBox_3.setChecked(True)
        try:
            x, y = config.getSettingsValue("pole_cords").split(",")
        except:
            x, y = "0", "0"
        self.ui.lineEdit_11.setText(x)
        self.ui.lineEdit_12.setText(y)
        self.ui.lineEdit_16.setText(config.getSettingsValue("bait_button"))
        self.ui.lineEdit_17.setText(config.getSettingsValue("pole_button"))
        self.ui.lineEdit_18.setText(config.getSettingsValue("telegram_message"))
        try:
            x, y = config.getSettingsValue("death_leave_cords").split(",")
            self.ui.lineEdit_15.setText(x)
            self.ui.lineEdit_14.setText(y)
        except:
            pass
        try:
            x, y = config.getSettingsValue("last_backpack_slot").split(",")
            self.ui.lineEdit_9.setText(x)
            self.ui.lineEdit_10.setText(y)
        except:
            pass
        try:
            pointA, pointB = config.getSettingsValue("fish_area").split("//")
            Ax, Ay = pointA.split(",")
            Bx, By = pointB.split(",")
            self.ui.lineEdit_3.setText(Ax)
            self.ui.lineEdit_4.setText(Ay)
            self.ui.lineEdit_5.setText(Bx)
            self.ui.lineEdit_6.setText(By)
        except:
            pass
        try:
            x, y = config.getSettingsValue("fish_cords").split(",")
            self.ui.lineEdit_8.setText(x)
            self.ui.lineEdit_7.setText(y)
        except:
            pass

    def saveFunc(self):
        token = self.ui.lineEdit.text()
        config.setSettingValue("token", token)
        bait_button = self.ui.lineEdit_16.text()
        config.setSettingValue("bait_button", bait_button)
        pole_button = self.ui.lineEdit_17.text()
        config.setSettingValue("pole_button", pole_button)
        telegram_message = self.ui.lineEdit_18.text()
        config.setSettingValue("telegram_message", telegram_message)
        chat_id = self.ui.lineEdit_2.text()
        config.setSettingValue("chat_id", chat_id)
        config.setSettingValue("move_to", "{},{}".format(self.ui.lineEdit_22.text(), self.ui.lineEdit_21.text()))
        fish_area = "{},{}//{},{}".format(self.ui.lineEdit_3.text(), self.ui.lineEdit_4.text(),
                                          self.ui.lineEdit_5.text(), self.ui.lineEdit_6.text())
        # self.ui.lineEdit_19.setText(config.getSettingsValue("bait_size"))
        # self.ui.lineEdit_20.setText(config.getSettingsValue("diff"))
        config.setSettingValue("bait_size", self.ui.lineEdit_19.text())
        config.setSettingValue("diff", self.ui.lineEdit_20.text())
        config.setSettingValue("new_ver", str(self.ui.checkBox_4.isChecked()))
        config.setSettingValue("fish_area", fish_area)
        fish_cords = "{},{}".format(self.ui.lineEdit_8.text(), self.ui.lineEdit_7.text())
        config.setSettingValue("fish_cords", fish_cords)
        is_full_backpack_active = self.ui.checkBox.isChecked()
        config.setSettingValue("is_full_backpack_active", str(is_full_backpack_active))
        last_backpack_slot = "{},{}".format(self.ui.lineEdit_9.text(), self.ui.lineEdit_10.text())
        config.setSettingValue("last_backpack_slot", last_backpack_slot)
        update_pole = self.ui.checkBox_2.isChecked()
        config.setSettingValue("update_pole", str(update_pole))
        is_death_leave = self.ui.checkBox_3.isChecked()
        config.setSettingValue("is_death_leave", str(is_death_leave))
        pole_cords = "{},{}".format(self.ui.lineEdit_11.text(), self.ui.lineEdit_12.text())
        config.setSettingValue("pole_cords", pole_cords)
        death_leave_cords = "{},{}".format(self.ui.lineEdit_15.text(), self.ui.lineEdit_14.text())
        config.setSettingValue("death_leave_cords", death_leave_cords)


    def deleteFish(self):
        for row in range(self.model.rowCount()):
            item = self.model.item(row)
            if item.checkState() == 2:
                name = item.text().split(" >> ")[0]
                config.deleteFish(name)
                self.model.removeRow(item.row())

    def OK(self):
        self.stop_event = threading.Event()
        self.c_thread = threading.Thread(target=self.myEvenListener, args=(self.stop_event,))
        self.c_thread.start()

    def cancel(self):
        self.stop_event.set()
        self.close()
    def startFishing(self):
        res = account_status(config.getSettingsValue("token"))
        if res["sub_status"]:
            self.stop_event = threading.Event()
            self.stop_event2 = threading.Event()

            self.statistic = fishCore.Statistic()

            self.c_thread = threading.Thread(target=fishCore.FishCore().run, args=(self.stop_event, self.stop_event2, self.statistic))
            self.g_thread = threading.Thread(target=start_program, args=(config.getSettingsValue("token"), self.stop_event2, self.stop_event))
            self.c_thread.start()
            self.g_thread.start()
        # try:
        #     res = account_status(config.getSettingsValue("token"))
        #     if res["sub_status"]:
        #         # self.p = Thread(target=fishCore.FishCore().run).start()
        #         # self.q = Thread(target=start_program, args=(config.getSettingsValue("token"),)).start()
        #         r = fishCore.FishCore()
        #         # while True:
        #         r.run()
        # except Exception as e:
        #     print(e.with_traceback())

    def stopFishing(self):
        send_telegram_message(config.getSettingsValue("telegram_message"), config.getSettingsValue("chat_id"))
        send_telegram_message(self.statistic.final(), config.getSettingsValue("chat_id"))
        stop_program(config.getSettingsValue("token"))
        self.stop_event.set()
        self.stop_event2.set()
        self.close()

    def addFishColor(self):
        time.sleep(3)
        name = self.ui.lineEdit_13.text()
        x, y = config.getSettingsValue("fish_cords").split(",")
        image = ImageGrab.grab()
        r, g, b = image.getpixel((int(x), int(y)))
        pyautogui.moveTo(int(x), int(y))
        config.setFishValue(name, r, g, b)
        item = QStandardItem("{} >> ({}, {}, {})".format(name, r, g, b))
        item.setCheckable(True)
        self.model.appendRow(item)



    def setFishAreaTopLeft(self):
        self.ui.toolButton_2.setText("Click alt to set point")
        pos = getCoords()
        self.ui.lineEdit_3.setText(str(pos.x))
        self.ui.lineEdit_4.setText(str(pos.y))
        self.ui.toolButton_2.setText("Press to set cords")

    def setDeathLeaveCord(self):
        pos = getCoords()
        self.ui.lineEdit_15.setText(str(pos.x))
        self.ui.lineEdit_14.setText(str(pos.y))

    def setFishAreaDownRight(self):
        pos = getCoords()
        self.ui.lineEdit_5.setText(str(pos.x))
        self.ui.lineEdit_6.setText(str(pos.y))

    def setFishCords(self):
        pos = getCoords()
        self.ui.lineEdit_8.setText(str(pos.x))
        self.ui.lineEdit_7.setText(str(pos.y))

    def setLastBackpackCords(self):
        pos = getCoords()
        self.ui.lineEdit_9.setText(str(pos.x))
        self.ui.lineEdit_10.setText(str(pos.y))

    def setPoleCords(self):
        pos = getCoords()
        self.ui.lineEdit_11.setText(str(pos.x))
        self.ui.lineEdit_12.setText(str(pos.y))

    def setFullBackpackColor(self):
        x, y = config.getSettingsValue("last_backpack_slot").split(",")
        image = ImageGrab.grab()
        r, g, b = image.getpixel((int(x), int(y)))
        self.ui.label_20.setText("Current color: ({}, {}, {})".format(r, g, b))
        config.setSettingValue("full_backpack_color", "{},{},{}".format(r, g, b))

app = QtWidgets.QApplication([])
application = mywindow()
application.show()

sys.exit(app.exec())
