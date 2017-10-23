import json
from PyQt5 import QtCore, QtGui, QtWidgets

class Customer(QtWidgets.QListWidgetItem):  
 
    def __init__(self, centralwidget, name, Ui_MainWindow, parent=None):
        self.name = name
        self.act_room = "Wartezimmer"
        self.id = 0
        with open('id_count.txt', 'r') as f:
            self.id = int(f.readline())
        self.times = []
        self.mainWindow = Ui_MainWindow
        with open('id_count.txt', 'w') as f:
            json.dump(self.id + 1, f)
        super(QtWidgets.QListWidgetItem, self).__init__(parent)