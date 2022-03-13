import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from client import *
from login import *
from registration import *
from add_contact import *
import sqlite3
import os
import requests


class MyWin(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Client_MainWindow()
        self.ui.setupUi(self)

        self.ui.label_unlog.hide()
        self.ui.pushButton_unlog.hide()

        try:
            if not os.path.isfile("./user_log.sqlite"):
                self.ui.tabWidget.setCurrentIndex(1)
                self.ui.tab_chat.setEnabled(False)
            else:
                conn = sqlite3.connect("user_log.sqlite")
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT Login, Password FROM User_log WHERE UserId = 1")
                result = cursor.fetchall()
                login, password = result[0][0], result[0][1]
                result = {"login": login, "password": password}
                print(result)
                conn.close()

                response = requests.post(
                    "http://localhost:8080/login", data=result)

                if str(response) == "<Response [200]>":
                    closemes = QtWidgets.QMessageBox()
                    closemes.setWindowTitle("Успех")
                    closemes.setText("Подключение установлено")
                    closemes.buttonClicked.connect(self.close)
                    closemes = closemes.exec_()

                    self.ui.tab_chat.setEnabled(True)
                    self.ui.login_pushbutton.hide()
                    self.ui.reg_pushbutton.hide()
                    self.ui.label_unlog.setText(f"Авторизован как {login}")
                    self.ui.tabWidget.setCurrentIndex(0)
                    self.ui.label_unlog.show()
                    self.ui.pushButton_unlog.show()

                if str(response) == "<Response [404]>":
                    closemes = QtWidgets.QMessageBox()
                    closemes.setWindowTitle("Ошибка")
                    closemes.setText("Проверьте правильность логина/пароля")
                    closemes.buttonClicked.connect(self.close)
                    closemes = closemes.exec_()
                    os.remove("./user_log.sqlite")
        except:
            closemes = QtWidgets.QMessageBox()
            closemes.setWindowTitle("Ошибка")
            closemes.setText("Ошибка подключения")
            closemes.buttonClicked.connect(self.close)
            closemes = closemes.exec_()

        self.ui.login_pushbutton.clicked.connect(self.login)
        self.ui.reg_pushbutton.clicked.connect(self.registration)
        self.ui.pushButton_unlog.clicked.connect(self.unlog)
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

    def unlog(self):
        os.remove("./user_log.sqlite")
        closemes = QtWidgets.QMessageBox()
        closemes.setWindowTitle("Внимание")
        closemes.setText("Приложение будет перезапущено")
        closemes.buttonClicked.connect(self.close)
        closemes = closemes.exec_()


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
                login = self.ui.lineEdit_login.text().lower()
                password = self.ui.lineEdit_password.text()
                data = {"login": login, "password": password}
                response = requests.post(
                    "http://localhost:8080/login", data=data)
                if str(response) == "<Response [200]>":
                    closemes = QtWidgets.QMessageBox()
                    closemes.setWindowTitle("Успех")
                    closemes.setText("Подключение установлено")
                    closemes.buttonClicked.connect(self.close)
                    closemes = closemes.exec_()

                    conn = sqlite3.connect("user_log.sqlite")
                    cursor = conn.cursor()
                    cursor.execute(
                        "CREATE TABLE User_log(UserId INTEGER PRIMARY KEY, Login VARCHAR(20) NOT NULL, Password VARCHAR(20) NOT NULL)")
                    cursor.execute(
                        f'INSERT INTO User_log VALUES (Null, "{login}", "{password}")')
                    conn.commit()
                    conn.close()

                    self.parent.ui.tab_chat.setEnabled(True)
                    self.parent.ui.login_pushbutton.hide()
                    self.parent.ui.reg_pushbutton.hide()
                    self.parent.ui.label_unlog.setText(
                        f"Авторизован как {login}")
                    self.parent.ui.label_unlog.show()
                    self.parent.ui.pushButton_unlog.show()

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


class Registration(QtWidgets.QWidget):
    def __init__(self):
        super(Registration, self).__init__()
        self.ui = Ui_Registration()
        self.ui.setupUi(self)

        self.ui.pushButton_reg.clicked.connect(self.registration)

    def registration(self):
        try:
            email = self.ui.lineEdit_email.text()
            login = self.ui.lineEdit_login.text()
            password = self.ui.lineEdit_password.text()
            password_2 = self.ui.lineEdit_password_2.text()
            if email != "" and login != "" and password != "" and password_2 != "":
                if password == password_2:
                    if "." in email and "@" in email:
                        if not "[" in email and not "]" in email and not "'" in email:
                            if not "[" in login and not "]" in login and not "'" in login:
                                if not "[" in password and not "]" in password and not "'" in password:
                                    response = requests.post(
                                        "http://localhost:8080/registration", data={"email": email, "login": login, "password": password})
                                    print(response)
                                else:
                                    closemes = QtWidgets.QMessageBox()
                                    closemes.setWindowTitle("Ошибка")
                                    closemes.setText(
                                        "Пароль содержит запрещенные символы")
                                    closemes.buttonClicked.connect(
                                        closemes.close)
                                    closemes = closemes.exec_()
                            else:
                               closemes = QtWidgets.QMessageBox()
                               closemes.setWindowTitle("Ошибка")
                               closemes.setText(
                                    "Адрес электронной почты содержит запрещенные символы")
                               closemes.buttonClicked.connect(closemes.close)
                               closemes = closemes.exec_()
                        else:
                            closemes = QtWidgets.QMessageBox()
                            closemes.setWindowTitle("Ошибка")
                            closemes.setText(
                                "Логин содержит запрещенные символы")
                            closemes.buttonClicked.connect(closemes.close)
                            closemes = closemes.exec_()
                    else:
                        closemes = QtWidgets.QMessageBox()
                        closemes.setWindowTitle("Ошибка")
                        closemes.setText("Неверный формат электронной почты")
                        closemes.buttonClicked.connect(closemes.close)
                        closemes = closemes.exec_()
                else:
                    closemes = QtWidgets.QMessageBox()
                    closemes.setWindowTitle("Ошибка")
                    closemes.setText("Пароли не совпадают")
                    closemes.buttonClicked.connect(closemes.close)
                    closemes = closemes.exec_()
            else:
                closemes = QtWidgets.QMessageBox()
                closemes.setWindowTitle("Ошибка")
                closemes.setText("Введите данные во все поля")
                closemes.buttonClicked.connect(closemes.close)
                closemes = closemes.exec_()

            if str(response) == "<Response [200]>":
                print(response)

            if str(response) == "<Response [403]>":
                closemes = QtWidgets.QMessageBox()
                closemes.setWindowTitle("Ошибка")
                closemes.setText(
                    "Пользователь с такими данными уже существует")
                closemes.buttonClicked.connect(closemes.close)
                closemes = closemes.exec_()

        except:
            closemes = QtWidgets.QMessageBox()
            closemes.setWindowTitle("Ошибка")
            closemes.setText("Ошибка подключения")
            closemes.buttonClicked.connect(closemes.close)
            closemes = closemes.exec_()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())
