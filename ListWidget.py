import datetime
import Customer
from PyQt5 import QtCore, QtGui, QtWidgets

class ListWidget(QtWidgets.QListWidget):
    def __init__(self, parent, name, ui=None):
        super().__init__(parent)
        self.name = name
        self.ui = ui
        self.setDragEnabled(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.setMovement(QtWidgets.QListView.Snap)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        event.accept()

    def dragMoveEvent(self, event):
        event.setDropAction(QtCore.Qt.CopyAction)
        event.accept()

    def dropEvent(self, event):
        insertPos   = event.pos()
        fromList = event.source()
        insertRow = fromList.row(fromList.itemAt(insertPos))
        for item in fromList.selectedItems():
            name = item.text()
        event.setDropAction(QtCore.Qt.MoveAction)
        super(ListWidget, self).dropEvent(event)
        date = datetime.datetime.now().strftime('%H:%M %d.%m.%Y')
        print("Customer", name, " moved to Treatment Room ", self.name)
        print(date)
        if self.ui is not None:
            self.ui.roomChange(date, name, self.name) 
        event.accept()