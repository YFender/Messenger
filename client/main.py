import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from client import *
from login import *
from registration import *
import sqlite3
import os
import socket

if not os.path.isfile("Contacts.sqlite"):
    conn = sqlite3.connect("Contacts.sqlite")
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE Contacts(ContactID INTEGER PRIMARY KEY, ContactName VARCHAR(20) NOT NULL, ContactLogin VARCHAR(20) NOT NULL)")
    conn.close()

conn = sqlite3.connect('./Contacts.sqlite')
cursor = conn.cursor()

sock = socket.socket()
sock.connect(("localhost", 5555))


class MyWin(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Client_MainWindow()
        self.ui.setupUi(self)

        self.ui.login_pushbutton.clicked.connect(self.login)
        self.ui.reg_pushbutton.clicked.connect(self.registration)

        self.ui.pushButton_delete_user.setEnabled(False)
        self.ui.listWidget_contacts.itemClicked.connect(self.select_contact)

        self.read_contacts()

    def read_contacts(self):
        cursor.execute("SELECT ContactName FROM Contacts")
        results = cursor.fetchall()
        for i in results:
            print(i[0])
            self.ui.listWidget_contacts.addItem(i[0])

    def login(self):
        self.w2 = Login()
        self.w2.show()

    def registration(self):
        self.w3 = Registration()
        self.w3.show()

    def select_contact(self):
        pass


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
