import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from client import *
from login import *

class MyWin(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Client_MainWindow()
        self.ui.setupUi(self)

    def login(self):
        self.w2 = Login()
        self.w2.show()

class Login(QtWidgets.QWidget):
    def __init__(self):
        super(Login, self).__init__()
        self.ui = Ui_Login()
        self.ui.setupUi(self)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())
