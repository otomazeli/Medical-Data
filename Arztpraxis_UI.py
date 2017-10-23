# -*- coding: utf-8 -*-

import datetime
import pickle
import json
import os
from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from ListWidget import *
from Customer import * 

class Ui_MainWindow(object):
    current_path = "C:/Users/Administrator/Desktop/Arztpraxis"
    max_width = 0
    max_height = 0
    height_button = 0
    width_button = 0
    offset_left = 100
    active_treatment_rooms = 0
    active_waiting_rooms = 0

    def addCustomer(self):
        name, _ = QtWidgets.QInputDialog.getText(None, 'Text Eingabe', 'Patienten Name:', QtWidgets.QLineEdit.Normal, "")
        print("Added Customer", name)
        print(datetime.datetime.now().strftime('%H:%M %d.%m.%Y'))
        self.customerList.append(Customer(self.centralwidget, name, self))
        self.customerList[-1].times.append('Betreten:'+datetime.datetime.now().strftime('%H:%M %d.%m.%Y'))
        self.customerList[-1].setText(name)
        self.comboBox.addItem(self.customerList[-1].name)
        customer = QtWidgets.QListWidgetItem(self.customerList[-1].name) 
        self.listWidget.addItem(customer)

    def deleteCustomer(self):
        if len(self.customerList) > 0:
            for index, customer in enumerate(self.customerList):
                if customer.name == self.comboBox.currentText():
                    print("Deleting Customer: ", customer.name)
                    print(datetime.datetime.now().strftime('%H:%M %d.%m.%Y'))
                    self.customerList[index].times.append('Verlassen:'+datetime.datetime.now().strftime('%H:%M %d.%m.%Y'))
                    self.comboBox.removeItem(index)
                    with open(self.current_path+'/Zeiten/Data '+ datetime.datetime.now().strftime('%d-%m-%Y')+'/' +str(self.customerList[index].id)+'.txt', 'w') as f:
                        json.dump(self.customerList[index].times, f, separators=(',',':'), indent=2)
                    for room in self.rooms:
                        items = room.findItems(customer.name, QtCore.Qt.MatchExactly)
                        if len(items) > 0:
                            for item in items:
                                row = room.row(item)
                                room.takeItem(row)
                    del self.customerList[index]
                    
    def updateNames(self, customer_id, old_name):
        print("hanged Name of Customer with ID: " + str(customer_id))
        for index, customer in enumerate(self.customerList):
            if customer.id == customer_id:
                self.comboBox.setItemText(index, self.customerList[index].name)

    def roomChange(self, date, customer_name, room_name):
        for indx, customer in enumerate(self.customerList):
            if customer.name == customer_name:
                self.customerList[indx].times.append('Raumwechsel von ' + customer.act_room + ' zu ' + room_name +  ', um: ' + date) 
                customer.act_room = room_name

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("Arztpraxis")
        MainWindow.resize(1920, 1080)
        MainWindow.setWindowState(QtCore.Qt.WindowMaximized)

        file_path_data = self.current_path + "/Zeiten/Data " + datetime.datetime.now().strftime('%d-%m-%Y')
        if not os.path.exists(file_path_data):
            print('Creating new Dir for today')
            os.makedirs(file_path_data)

        with open(self.current_path+'/settings.txt', 'r') as f:
            for nr, line in zip(range(2), f):
                if nr == 0:
                    self.active_treatment_rooms = int(line)
                elif nr == 1:
                    self.active_waiting_rooms = int(line)
            print('Loaded settings: ')
            print(self.active_treatment_rooms, self.active_waiting_rooms)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.customerList = []
        self.rooms = []
        self.waiting_rooms = []
        self.labels = []
        self.labels_waiting = []
        self.max_width = MainWindow.frameGeometry().width()
        self.max_height = MainWindow.frameGeometry().height()
        self.height_button = 41
        self.width_button = 121
        self.create_rooms()
        self.number_rooms = 0
        self.number_rooms_old = self.active_treatment_rooms
        self.number_waiting_rooms = 0
        self.number_waiting_rooms_old = self.active_waiting_rooms
        self.ui_logic()
        self.ui_setup(MainWindow)

    def menu_bar(self):
        self.settings = self.menubar.addMenu('Settings')  
        # Treatment Rooms
        self.rooms_number = QtWidgets.QAction('Behandlungszimmer', self.centralwidget)
        number = self.rooms_number.triggered.connect(lambda: self.text_input('Anzahl an Behandlungszimmer:                           '))
        self.settings.addAction(self.rooms_number)
        # Waiting Rooms
        self.waiting_rooms_number = QtWidgets.QAction('Wartezimmer', self.centralwidget)
        number = self.waiting_rooms_number.triggered.connect(lambda: self.text_input('Anzahl an Wartezimmer:                         '))
        self.settings.addAction(self.waiting_rooms_number)
        # Add Save Button for Number of Treatment and Waiting Rooms
        self.save = self.menubar.addMenu('Save')
        self.save_action = QtWidgets.QAction('Behandlungszimmer', self.centralwidget)
        self.save_action.triggered.connect(lambda: self.save_settings())
        self.save.addAction(self.save_action)

    def save_settings(self):
        print('Trigger save settings')
        self.active_treatment_rooms = sum([room.isVisible() for room in self.rooms])
        self.active_waiting_rooms = sum([waiting_room.isVisible() for waiting_room in self.waiting_rooms])
        print(self.active_treatment_rooms, self.active_waiting_rooms)
        with open(self.current_path+'/settings.txt', 'w') as f:
            f.write(str(self.active_treatment_rooms))
            f.write("\n")
            f.write(str(self.active_waiting_rooms))

    def text_input(self, question):
        if 'Wartezimmer' in question:
            input_text, _ = QtWidgets.QInputDialog.getText(self.centralwidget, 'Zahlen Eingabe (1-2)', question, QtWidgets.QLineEdit.Normal)
            if input_text != "" and input_text.isdigit():
                self.number_waiting_rooms = int(input_text)
                self.reshape_waiting_rooms()
        elif 'Behandlung' in question:
            input_text, _ = QtWidgets.QInputDialog.getText(self.centralwidget, 'Zahlen Eingabe (1-10)', question, QtWidgets.QLineEdit.Normal)
            if input_text != "" and input_text.isdigit():
                self.number_rooms = int(input_text)
                self.reshape_rooms()

    def ui_setup(self, MainWindow):
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 962, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.menu_bar()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Arztpraxis"))
        self.label.setText(_translate("MainWindow", "Wartezimmer"))
        self.label_2.setText(_translate("MainWindow", "Raum 1"))
        self.label_3.setText(_translate("MainWindow", "Raum 2"))
        self.label_4.setText(_translate("MainWindow", "Raum 3"))
        self.label_5.setText(_translate("MainWindow", "Raum 4"))
        self.label_6.setText(_translate("MainWindow", "Wartezimmer 2"))
        self.label_7.setText(_translate("MainWindow", "Raum 5"))
        self.label_8.setText(_translate("MainWindow", "Raum 6"))
        self.label_9.setText(_translate("MainWindow", "Raum 7"))
        self.label_10.setText(_translate("MainWindow", "Raum 8"))
        self.pushButton.setText(_translate("MainWindow", "Patient erstellen"))
        self.pushButton_2.setText(_translate("MainWindow", "Patient löschen"))

    def create_rooms(self):
        self.listWidget = ListWidget(self.centralwidget, 'Wartezimmer', self)
        self.listWidget.setGeometry(QtCore.QRect(self.offset_left, 20, 256, 192))
        self.listWidget.setObjectName("listWidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(self.offset_left, 0, 251, 16))
        self.label.setObjectName("label")
        self.waiting_rooms.append(self.listWidget)
        self.labels_waiting.append(self.label)

        self.listWidget_2 = ListWidget(self.centralwidget, 'Raum1', self)
        self.listWidget_2.setGeometry(QtCore.QRect(640, 20, 256, 192))
        self.listWidget_2.setObjectName("listWidget_2")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(640, 0, 51, 16))
        self.label_2.setObjectName("label_2")
        self.rooms.append(self.listWidget_2)
        self.labels.append(self.label_2)

        self.listWidget_3 = ListWidget(self.centralwidget, 'Raum2', self)
        self.listWidget_3.setGeometry(QtCore.QRect(900, 20, 256, 192))
        self.listWidget_3.setObjectName("listWidget_3")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(900, 0, 61, 16))
        self.label_3.setObjectName("label_3")
        self.rooms.append(self.listWidget_3)
        self.labels.append(self.label_3)

        self.listWidget_4 = ListWidget(self.centralwidget, 'Raum3', self)
        self.listWidget_4.setGeometry(QtCore.QRect(1160, 20, 256, 192))
        self.listWidget_4.setObjectName("listWidget_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(1160, 0, 61, 16))
        self.label_4.setObjectName("label_4")
        self.rooms.append(self.listWidget_4)
        self.labels.append(self.label_4)

        self.listWidget_5 = ListWidget(self.centralwidget, 'Raum4', self)
        self.listWidget_5.setGeometry(QtCore.QRect(1420, 20, 256, 192))
        self.listWidget_5.setObjectName("listWidget_3")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(1420, 0, 61, 16))
        self.label_5.setObjectName("label_5")
        self.rooms.append(self.listWidget_5)
        self.labels.append(self.label_5)

        # New Line
        self.listWidget_6 = ListWidget(self.centralwidget, 'Wartezimmer2', self)
        self.listWidget_6.setGeometry(QtCore.QRect(self.offset_left, 250, 256, 192))
        self.listWidget_6.setObjectName("listWidget")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(self.offset_left, 230, 451, 16))
        self.label_6.setObjectName("label_6")
        self.labels_waiting.append(self.label_6)
        self.waiting_rooms.append(self.listWidget_6)

        self.listWidget_7 = ListWidget(self.centralwidget, 'Raum5', self)
        self.listWidget_7.setGeometry(QtCore.QRect(640, 250, 256, 192))
        self.listWidget_7.setObjectName("listWidget_2")
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(640, 230, 51, 16))
        self.label_7.setObjectName("label_7")
        self.rooms.append(self.listWidget_7)
        self.labels.append(self.label_7)

        self.listWidget_8 = ListWidget(self.centralwidget, 'Raum6', self)
        self.listWidget_8.setGeometry(QtCore.QRect(900, 250, 256, 192))
        self.listWidget_8.setObjectName("listWidget_3")
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(900, 230, 61, 16))
        self.label_8.setObjectName("label_8")
        self.rooms.append(self.listWidget_8)
        self.labels.append(self.label_8)

        self.listWidget_9 = ListWidget(self.centralwidget, 'Raum7', self)
        self.listWidget_9.setGeometry(QtCore.QRect(1160, 250, 256, 192))
        self.listWidget_9.setObjectName("listWidget_3")
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setGeometry(QtCore.QRect(1160, 230, 61, 16))
        self.label_9.setObjectName("label_9")
        self.rooms.append(self.listWidget_9)
        self.labels.append(self.label_9)

        self.listWidget_10 = ListWidget(self.centralwidget, 'Raum8', self)
        self.listWidget_10.setGeometry(QtCore.QRect(1420, 250, 256, 192))
        self.listWidget_10.setObjectName("listWidget_3")
        self.label_10 = QtWidgets.QLabel(self.centralwidget)
        self.label_10.setGeometry(QtCore.QRect(1420, 230, 61, 16))
        self.label_10.setObjectName("label_10")
        self.rooms.append(self.listWidget_10)
        self.labels.append(self.label_10)

        for i in range(self.active_treatment_rooms, len(self.rooms)):
            self.rooms[i].hide()
            self.labels[i].hide()
        self.number_rooms_old = 0
        self.number_rooms = self.active_treatment_rooms

        for i in range(self.active_waiting_rooms, len(self.waiting_rooms)):
            self.waiting_rooms[i].hide()
        self.number_waiting_rooms_old = 0
        self.number_waiting_rooms = self.active_waiting_rooms

    def reshape_rooms(self):
        if self.number_rooms > len(self.rooms):
            self.number_rooms = len(self.rooms)
        print('Reshape Treatment Rooms from: ', self.number_rooms_old, ' to: ', self.number_rooms)
        if self.number_rooms_old > self.number_rooms:
            for indx in range(self.number_rooms, self.number_rooms_old):
                self.rooms[indx].hide()
                self.labels[indx].hide()
            self.number_rooms_old = self.number_rooms
        elif self.number_rooms_old < self.number_rooms:
            for indx in range(self.number_rooms_old, self.number_rooms):
                self.rooms[indx].show()
                self.labels[indx].show()
            self.number_rooms_old = self.number_rooms

    def reshape_waiting_rooms(self):
        if self.number_waiting_rooms > len(self.waiting_rooms):
            self.number_waiting_rooms = len(self.waiting_rooms)
        print('Reshape Treatment Rooms from: ', self.number_waiting_rooms_old, ' to: ', self.number_waiting_rooms)
        if self.number_waiting_rooms_old > self.number_waiting_rooms:
            for indx in range(self.number_waiting_rooms, self.number_waiting_rooms_old):
                self.waiting_rooms[indx].hide()
                self.labels_waiting[indx].hide()
            self.number_waiting_rooms_old = self.number_waiting_rooms
        elif self.number_waiting_rooms_old < self.number_waiting_rooms:
            for indx in range(self.number_waiting_rooms_old, self.number_waiting_rooms):
                self.waiting_rooms[indx].show()
                self.labels_waiting[indx].show()
            self.number_waiting_rooms_old = self.number_waiting_rooms

    def ui_logic(self):
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        print(self.max_height)
        print(self.max_width)
        self.pushButton.setGeometry(QtCore.QRect(self.width_button, self.max_height -  5 * self.height_button, self.width_button, self.height_button))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.addCustomer)

        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(self.max_width - 4 * self.width_button, self.max_height - 6 * self.height_button, self.width_button, self.height_button))
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(self.max_width - 4 * self.width_button, self.max_height -  5 * self.height_button, self.width_button, self.height_button))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.deleteCustomer)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())