import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from client import *
from login import *
from registration import*

class MyWin(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MyWin, self).__init__()
        self.ui = Ui_Client_MainWindow()
        self.ui.setupUi(self)

        self.ui.login_pushbutton.clicked.connect(self.login)
        self.ui.reg_pushbutton.clicked.connect(self.registration)

    def login(self):
        self.w2 = Ui_Login()
        self.w2.show()

    def registration(self):
        pass

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())
