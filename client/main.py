import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from client import *
from login import *
from registration import *

class MyWin(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Client_MainWindow()
        self.ui.setupUi(self)

        self.ui.login_pushbutton.clicked.connect(self.login)
        self.ui.reg_pushbutton.clicked.connect(self.registration)

        self.ui.pushButton_delete_user.setEnabled(False)

    def login(self):
        self.w2 = Login()
        self.w2.show()

    def registration(self):
        self.w3 = Registration()
        self.w3.show()

class Login(QtWidgets.QMainWindow):
    def __init__(self):
        super(Login, self).__init__()
        self.ui = Ui_Login()
        self.ui.setupUi(self)

class Registration(QtWidgets.QMainWindow):
    def __init__(self):
        super(Registration, self).__init__()
        self.ui = Ui_Registration()
        self.ui.setupUi(self)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())
