import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from client import *
from login import *
from registration import *
from add_contact import *
import sqlite3
import os
import requests

# if not os.path.isfile("users.sqlite"):
#     conn = sqlite3.connect("users.sqlite")
#     cursor = conn.cursor()
#     cursor.execute(
#         "CREATE TABLE Contacts(ContactID INTEGER PRIMARY KEY, ContactName VARCHAR(20) NOT NULL, ContactLogin VARCHAR(20) NOT NULL)")
#     conn.close()
#
# try:
#     login = sqlite3.connect("./user_log.sqlite")
#     login_cursor = login.cursor()
#     login_cursor.execute("SELECT * FROM User")
#
# user_login = login_cursor.fetchall()[0][1]
# user_password = login_cursor.fetchall()[0][2]
#
#     login.close()
# except Exception:
#     login.close()

# conn = sqlite3.connect('./Contacts.sqlite')
# cursor = conn.cursor()

#sock = socket.socket()
#sock.connect(("localhost", 5555))


class MyWin(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Client_MainWindow()
        self.ui.setupUi(self)

        if not os.path.isfile("./user_log.sqlite"):
            self.ui.tabWidget.setCurrentIndex(1)
            self.ui.tab_chat.setEnabled(False)

        self.ui.login_pushbutton.clicked.connect(self.login)
        self.ui.reg_pushbutton.clicked.connect(self.registration)
        self.ui.pushButton_add_contact.clicked.connect(self.add_contacts)

        self.ui.pushButton_delete_user.setEnabled(False)
        self.ui.listWidget_contacts.itemClicked.connect(self.select_contact)

        # self.read_contacts()

    def read_contacts(self):
        cursor.execute("SELECT ContactName FROM Contacts")
        results = cursor.fetchall()
        for i in results:
            print(i[0])
            self.ui.listWidget_contacts.addItem(i[0])

    def login(self):
        self.w2 = Login(self)
        self.w2.show()

    def registration(self):
        self.w3 = Registration()
        self.w3.show()

    def select_contact(self):
        pass

    def add_contacts(self):
        self.w4 = Add_contacts()
        self.w4.show()


class Login(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Login, self).__init__()
        self.ui = Ui_Login()
        self.ui.setupUi(self)
        self.parent = parent

        # self.parent.ui.tabWidget.setEnabled(False)

        self.ui.pushButton_authorize.clicked.connect(self.login)

    def login(self):
        if self.ui.lineEdit_login.text() != "" and self.ui.lineEdit_password.text() != "":
            try:
                data = {"login": self.ui.lineEdit_login.text().lower(
                ), "password": self.ui.lineEdit_password.text()}
                response = requests.post(
                    "http://localhost:8080/login", data=data)
                if str(response) == "<Response [200]>":
                    closemes = QtWidgets.QMessageBox()
                    closemes.setWindowTitle("Успешно")
                    closemes.setText("Подключение установлено")
                    closemes.buttonClicked.connect(self.close)
                    closemes = closemes.exec_()
                    self.parent.ui.tab_chat.setEnabled(True)

                if str(response) == "<Response [404]>":
                    closemes = QtWidgets.QMessageBox()
                    closemes.setWindowTitle("Ошибка")
                    closemes.setText("Проверьте правильность логина/пароля")
                    closemes.buttonClicked.connect(self.close)
                    closemes = closemes.exec_()

            except:
                closemes = QtWidgets.QMessageBox()
                closemes.setWindowTitle("Ошибка")
                closemes.setText("Ошибка подключения")
                closemes.buttonClicked.connect(self.close)
                closemes = closemes.exec_()

    def closeEvent(self, event):
        self.parent.ui.tabWidget.setEnabled(True)


class Registration(QtWidgets.QMainWindow):
    def __init__(self):
        super(Registration, self).__init__()
        self.ui = Ui_Registration()
        self.ui.setupUi(self)


class Add_contacts(QtWidgets.QMainWindow):
    def __init__(self):
        super(Add_contacts, self).__init__()
        self.ui = Ui_Add_contact()
        self.ui.setupUi(self)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())
