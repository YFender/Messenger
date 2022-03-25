from sys import argv, exit
from PyQt5 import QtWidgets, QtCore
from client import Ui_Client_MainWindow
from login import Ui_Login
from registration import Ui_Registration
from add_contact import Ui_Add_contact
from sqlite3 import connect
from os import path, remove
from requests import post
from email_dialog import Ui_Dialog
from re import findall, match

response_address = "http://localhost:8080"


class MyWin(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Client_MainWindow()
        self.ui.setupUi(self)

        self.ui.label_unlog.hide()
        self.ui.pushButton_unlog.hide()
        self.ui.tab_chat.setEnabled(False)

        try:
            if not path.isfile("./user_log.sqlite"):
                self.ui.tabWidget.setCurrentIndex(1)
                self.ui.tab_chat.setEnabled(False)
            else:
                conn = connect("user_log.sqlite")
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT Login, Password FROM User_log WHERE UserId = 1")
                result = cursor.fetchone()
                self.login, self.password = result[0], result[1]
                result = {"login": self.login, "password": self.password}
                print(result)
                conn.close()

                response_login = post(
                    f"{response_address}/login", data=result)

                if str(response_login) == "<Response [200]>":
                    closemes = QtWidgets.QMessageBox()
                    closemes.setWindowTitle("Успех")
                    closemes.setText("Подключение установлено")
                    closemes.buttonClicked.connect(self.close)
                    closemes = closemes.exec_()

                    self.ui.tab_chat.setEnabled(True)
                    self.ui.login_pushbutton.hide()
                    self.ui.reg_pushbutton.hide()
                    self.ui.label_unlog.setText(
                        f"Авторизован как {self.login}")
                    self.ui.tabWidget.setCurrentIndex(0)
                    self.ui.label_unlog.show()
                    self.ui.pushButton_unlog.show()

                elif str(response_login) == "<Response [404]>":
                    closemes = QtWidgets.QMessageBox()
                    closemes.setWindowTitle("Ошибка")
                    closemes.setText("Проверьте правильность логина/пароля")
                    closemes.buttonClicked.connect(self.close)
                    closemes = closemes.exec_()
                    remove("./user_log.sqlite")

                self.timer = QtCore.QTimer()
                self.timer.timeout.connect(self.check_contacts)
                self.timer.start(1000)

        except:
            closemes = QtWidgets.QMessageBox()
            closemes.setWindowTitle("Ошибка")
            closemes.setText("Ошибка подключения")
            closemes.buttonClicked.connect(self.close)
            closemes = closemes.exec_()

        self.ui.login_pushbutton.clicked.connect(self.login_def)
        self.ui.reg_pushbutton.clicked.connect(self.registration)
        self.ui.pushButton_unlog.clicked.connect(self.unlog)

        self.ui.pushButton_delete_user.setEnabled(False)
        self.ui.listWidget_contacts.itemClicked.connect(self.select_contact)
        self.ui.pushButton_add_contact.clicked.connect(self.add_contact)

        self.check_contacts()

        # buttons = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        # buttonBox = QtWidgets.QDialogButtonBox(buttons)

    def login_def(self):
        self.w2 = Login(self)
        self.w2.show()

    def registration(self):
        self.w3 = Registration(self)
        self.w3.show()

    def select_contact(self):
        pass

    def unlog(self):
        remove("./user_log.sqlite")
        closemes = QtWidgets.QMessageBox()
        closemes.setWindowTitle("Внимание")
        closemes.setText("Приложение будет перезапущено")
        closemes.buttonClicked.connect(self.close)
        closemes = closemes.exec_()

    def add_contact(self):
        text, ok = QtWidgets.QInputDialog.getText(
            self, 'Добавление контакта', 'Введите имя пользователя')
        if ok and text != "":
            try:
                from_user = self.login.lower()
                to_user = text.lower()
                data = {"from_user": from_user, "to_user": to_user}
                response = post(
                    f"{response_address}/friendship_request", data=data)
                print(response)
                if str(response) == "<Response [200]>":
                    closemes = QtWidgets.QMessageBox()
                    closemes.setWindowTitle("Успех")
                    closemes.setText(
                            f"Запрос на добавление отправлен контакту {to_user}")
                    closemes.buttonClicked.connect(
                            self.close)
                    closemes = closemes.exec_()

                elif str(response) == "<Response [404]>":
                    closemes = QtWidgets.QMessageBox()
                    closemes.setWindowTitle("Ошибка")
                    closemes.setText(
                            f"Пользователя {to_user} не существует")
                    closemes.buttonClicked.connect(
                            closemes.close)
                    closemes = closemes.exec_()

                elif str(response) == "<Response [403]>":
                    closemes = QtWidgets.QMessageBox()
                    closemes.setWindowTitle("Ошибка")
                    closemes.setText(
                            "Запрос уже был отправлен")
                    closemes.buttonClicked.connect(
                            closemes.close)
                    closemes = closemes.exec_()
            except Exception as ex:
                print(ex)

        # self.w4 = Add_contact(self)
        # self.w4.show()

    def check_contacts(self):
        try:
            response = post(f"{response_address}/check_contacts")
            if response == "<Response [200]>":
                self.w7 = Check_contacts_dialog()
                self.w7.show()
            else:
                self.timer.stop()
        except:
            self.timer.stop()


class Login(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Login, self).__init__()
        self.ui = Ui_Login()
        self.ui.setupUi(self)
        self.parent = parent

        self.ui.pushButton_authorize.clicked.connect(self.login)

    def login(self):
        if self.ui.lineEdit_login.text() != "" and self.ui.lineEdit_password.text() != "":
            try:
                login = self.ui.lineEdit_login.text().lower()
                if not findall('[^..\w!@#\$%\^&\*\(\)\-_\+=;:,\./\?\\\|`~\[\]\{\}]', login):
                    password = self.ui.lineEdit_password.text()
                    if not findall('[^..\w!@#\$%\^&\*\(\)\-_\+=;:,\./\?\\\|`~\[\]\{\}]', password):
                        data = {"login": login, "password": password}
                        response = post(
                            f"{response_address}/login", data=data)
                        if str(response) == "<Response [200]>":
                            closemes = QtWidgets.QMessageBox()
                            closemes.setWindowTitle("Успех")
                            closemes.setText("Подключение установлено")
                            closemes.buttonClicked.connect(self.close)
                            closemes = closemes.exec_()

                            conn = connect("user_log.sqlite")
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
                            self.parent.login = login

                            self.timer = QtCore.QTimer()
                            self.timer.timeout.connect(self.check_contacts)
                            self.timer.start(1000)

                        if str(response) == "<Response [404]>":
                            closemes = QtWidgets.QMessageBox()
                            closemes.setWindowTitle("Ошибка")
                            closemes.setText(
                                "Проверьте правильность логина/пароля")
                            closemes.buttonClicked.connect(closemes.close)
                            closemes = closemes.exec_()
                    else:
                        closemes = QtWidgets.QMessageBox()
                        closemes.setWindowTitle("Ошибка")
                        closemes.setText("Пароль содержит запрещенные символы")
                        closemes.buttonClicked.connect(closemes.close)
                        closemes = closemes.exec_()
                else:
                    closemes = QtWidgets.QMessageBox()
                    closemes.setWindowTitle("Ошибка")
                    closemes.setText("Логин содержит запрещенные символы")
                    closemes.buttonClicked.connect(closemes.close)
                    closemes = closemes.exec_()

            except:
                closemes = QtWidgets.QMessageBox()
                closemes.setWindowTitle("Ошибка")
                closemes.setText("Ошибка подключения")
                closemes.buttonClicked.connect(self.close)
                closemes = closemes.exec_()
        else:
            closemes = QtWidgets.QMessageBox()
            closemes.setWindowTitle("Ошибка")
            closemes.setText("Введите логин и пароль")
            closemes.buttonClicked.connect(closemes.close)
            closemes = closemes.exec_()

    def closeEvent(self, event):
        self.parent.ui.tabWidget.setEnabled(True)


class Registration(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Registration, self).__init__()
        self.ui = Ui_Registration()
        self.ui.setupUi(self)
        self.parent = parent

        self.ui.pushButton_reg.clicked.connect(self.registration)
        self.parent.setEnabled(False)

    def registration(self):
        try:
            email = self.ui.lineEdit_email.text().lower()
            login = self.ui.lineEdit_login.text().lower()
            password = self.ui.lineEdit_password.text()
            password_2 = self.ui.lineEdit_password_2.text()
            if email != "" and login != "" and password != "" and password_2 != "":
                if password == password_2:
                    if match('^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$', email) != None:
                        if not findall('[^..\w!@#\$%\^&\*\(\)\-_\+=;:,\./\?\\\|`~\[\]\{\}]', login):
                            if not findall('[^..\w!@#\$%\^&\*\(\)\-_\+=;:,\./\?\\\|`~\[\]\{\}]', password):
                                response = post(f"{response_address}/registration", data={
                                                         "email": email, "login": login, "password": password})
                                print(response)
                                if str(response) == "<Response [200]>":
                                    self.dialog = Email_dialog(self)
                                    self.dialog.show()
                                    # closemes = QtWidgets.QMessageBox()
                                    #
                                    # closemes.setWindowTitle("Успех")
                                    # closemes.setText(
                                    #     "На ваш Email пришел код")
                                    # closemes.buttonClicked.connect(self.close)
                                    # closemes = closemes.exec_()

                                elif str(response) == "<Response [403]>":
                                    closemes = QtWidgets.QMessageBox()
                                    closemes.setWindowTitle("Ошибка")
                                    closemes.setText(
                                            "Пользователь с такими данными уже существует")
                                    closemes.buttonClicked.connect(
                                            closemes.close)
                                    closemes = closemes.exec_()

                                elif str(response) == "<Response [550]>":
                                    closemes = QtWidgets.QMessageBox()
                                    closemes.setWindowTitle("Ошибка")
                                    closemes.setText(
                                            "Такой электронной почты не существует")
                                    closemes.buttonClicked.connect(
                                            closemes.close)
                                    closemes = closemes.exec_()

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
                                    "Логин содержит запрещенные символы")
                            closemes.buttonClicked.connect(closemes.close)
                            closemes = closemes.exec_()
                    else:
                        closemes = QtWidgets.QMessageBox()
                        closemes.setWindowTitle("Ошибка")
                        closemes.setText(
                                "Адрес электронной почты имеет формат или/и содержит запрещенные символы")
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

        except Exception as ex:
            print(ex)
            closemes = QtWidgets.QMessageBox()
            closemes.setWindowTitle("Ошибка")
            closemes.setText("Ошибка подключения")
            closemes.buttonClicked.connect(closemes.close)
            closemes = closemes.exec_()

    def closeEvent(self, event):
        self.parent.setEnabled(True)


class Email_dialog(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Email_dialog, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.parent = parent

        self.ui.label.setText(
            f"Введите код, отправленный на \n{self.parent.ui.lineEdit_email.text()}")
        self.ui.pushButton.clicked.connect(self.send_verification)
        self.parent.setEnabled(False)

        self.email = self.parent.ui.lineEdit_email.text().lower()
        self.login = self.parent.ui.lineEdit_login.text().lower()
        self.password = self.parent.ui.lineEdit_password.text()

    def send_verification(self):
        if self.ui.lineEdit.text() != "":
            try:
                self.check_str = self.ui.lineEdit.text().upper()
                response = post(f"{response_address}/email_verification", data={
                                "email": self.email, "login": self.login, "password": self.password, "check_str": self.check_str})

                if str(response) == "<Response [200]>":
                    closemes = QtWidgets.QMessageBox()
                    closemes.setWindowTitle("Успех")
                    closemes.setText(
                            "Регистрация прошла успешно")
                    closemes.buttonClicked.connect(
                            self.close)
                    closemes = closemes.exec_()

                elif str(response) == "<Response [403]>":
                    closemes = QtWidgets.QMessageBox()
                    closemes.setWindowTitle("Ошибка")
                    closemes.setText(
                            "Проверьте правильность ввода кода подтверждения")
                    closemes.buttonClicked.connect(
                            closemes.close)
                    closemes = closemes.exec_()
            except:
                closemes = QtWidgets.QMessageBox.critical(
                    self, "Ошибка", "Ошибка подключения")
                closemes.buttonClicked.connect(
                        closemes.close)
                closemes = closemes.exec_()

    def closeEvent(self, event):
        self.parent.setEnabled(True)
        try:
            post(f"{response_address}/email_verification_delete",
                 data={"email": self.email, "login": self.login})
        except:
            pass


class Add_contact(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Add_contact, self).__init__()
        self.ui = Ui_Add_contact()
        self.ui.setupUi(self)
        self.parent = parent

        self.from_login = self.parent.login.lower()
        self.to_login = self.ui.lineEdit.text().lower()

        self.ui.pushButton.clicked.connect(self.friendship_request)

    def friendship_request(self):
        self.from_login = self.parent.login.lower()
        self.to_login = self.ui.lineEdit.text().lower()
        if self.to_login != "":
            if self.to_login != self.parent.login:
                try:
                    data = {"from_user": self.from_login,
                            "to_user": self.to_login}
                    response = post(
                        f"{response_address}/friendship_request", data=data)
                    print(response)
                    if str(response) == "<Response [200]>":
                        closemes = QtWidgets.QMessageBox()
                        closemes.setWindowTitle("Успех")
                        closemes.setText(
                                f"Запрос на добавление отправлен контакту {self.to_login}")
                        closemes.buttonClicked.connect(
                                self.close)
                        closemes = closemes.exec_()

                    elif str(response) == "<Response [404]>":
                        closemes = QtWidgets.QMessageBox()
                        closemes.setWindowTitle("Ошибка")
                        closemes.setText(
                                f"Пользователя {self.to_login} не существует")
                        closemes.buttonClicked.connect(
                                closemes.close)
                        closemes = closemes.exec_()

                    elif str(response) == "<Response [403]>":
                        closemes = QtWidgets.QMessageBox()
                        closemes.setWindowTitle("Ошибка")
                        closemes.setText(
                                "Запрос уже был отправлен")
                        closemes.buttonClicked.connect(
                                closemes.close)
                        closemes = closemes.exec_()

                except Exception as ex:
                    print(ex)

            else:
                closemes = QtWidgets.QMessageBox()
                closemes.setWindowTitle("Ошибка")
                closemes.setText(
                        "Вы не можете отправить запрос самому себе")
                closemes.buttonClicked.connect(
                        closemes.close)
                closemes = closemes.exec_()


class Check_contacts_dialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("HELLO!")

        QBtn = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel

        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QtWidgets.QVBoxLayout()
        message = QtWidgets.QLabel("Something happened, is that OK?")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


if __name__ == "__main__":
    app = QtWidgets.QApplication(argv)
    myapp = MyWin()
    myapp.show()
    exit(app.exec_())
    myapp.show()
    exit(app.exec_())
