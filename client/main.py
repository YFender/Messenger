from os import path, remove
from re import findall, match
from sqlite3 import connect
from sys import argv, exit

from PyQt5 import QtWidgets, QtCore
from requests import post

from client import Ui_Client_MainWindow
from email_dialog import Ui_Dialog
from login import Ui_Login
from registration import Ui_Registration

response_address = "http://localhost:8080"


class MyWin(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Client_MainWindow()
        self.ui.setupUi(self)

        self.contacts_list = []

        self.ui.label_unlog.hide()
        self.ui.pushButton_unlog.hide()
        self.ui.tab_chat.setEnabled(False)

        self.timer = QtCore.QTimer()

        self.ui.login_pushbutton.clicked.connect(self.login_def)
        self.ui.reg_pushbutton.clicked.connect(self.registration)
        self.ui.pushButton_unlog.clicked.connect(self.unlog)
        self.ui.pushButton_send_message.clicked.connect(self.message_def)

        self.ui.pushButton_send_message.setShortcut("Enter")

        self.ui.pushButton_delete_user.setEnabled(False)
        self.ui.pushButton_send_message.setEnabled(False)
        self.ui.listWidget_contacts.itemClicked.connect(self.select_contact)
        self.ui.pushButton_add_contact.clicked.connect(self.add_contact)
        self.ui.pushButton_delete_user.clicked.connect(self.delete_contact)

        # print(self.ui.listWidget_contacts.count())

        self.auto_login_def()



    def auto_login_def(self):
        try:
            if not path.isfile("./user_log.sqlite"):
                self.ui.tabWidget.setCurrentIndex(1)
                self.ui.tab_chat.setEnabled(False)
                conn = connect("user_log.sqlite")
                cursor = conn.cursor()
                cursor.execute(
                    "CREATE TABLE User_log(Login VARCHAR(20) NOT NULL, Password VARCHAR(20) NOT NULL)")
                conn.commit()
                conn.close()
            else:
                conn = connect("user_log.sqlite")
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT Login, Password FROM User_log")
                result = cursor.fetchone()
                if result:
                    self.login, self.password = result[0], result[1]
                    result = {"login": self.login, "password": self.password}
                    print(result)
                    response_login = post(
                        f"{response_address}/login", data=result)

                    if response_login.status_code == 200:
                        closemes = QtWidgets.QMessageBox()
                        closemes.setWindowTitle("Успех")
                        closemes.setText("Подключение установлено")
                        closemes.buttonClicked.connect(closemes.close)
                        closemes = closemes.exec_()

                        self.ui.tab_chat.setEnabled(True)
                        self.ui.login_pushbutton.hide()
                        self.ui.reg_pushbutton.hide()
                        self.ui.label_unlog.setText(
                            f"Авторизован как {self.login}")
                        self.ui.tabWidget.setCurrentIndex(0)
                        self.ui.label_unlog.show()
                        self.ui.pushButton_unlog.show()

                    elif response_login.status_code == 404:
                        closemes = QtWidgets.QMessageBox()
                        closemes.setWindowTitle("Ошибка")
                        closemes.setText("Проверьте правильность логина/пароля")
                        closemes.buttonClicked.connect(self.close)
                        closemes = closemes.exec_()
                        remove("./user_log.sqlite")

                    self.check_new_contacts()
                    self.check_old_contacts()
                else:
                    self.ui.tabWidget.setCurrentIndex(1)
                    self.ui.tab_chat.setEnabled(False)
                conn.close()

        except Exception as ex:
            print(ex, "autologin error")
            closemes = QtWidgets.QMessageBox()
            closemes.setWindowTitle("Ошибка")
            closemes.setText("Ошибка подключения")
            closemes.buttonClicked.connect(closemes.close)
            closemes = closemes.exec_()

    def login_def(self):
        self.w2 = Login(self)
        self.w2.show()

    def registration(self):
        self.w3 = Registration(self)
        self.w3.show()

    def select_contact(self):
        self.ui.textBrowser_chat.clear()
        self.selected_contact = self.ui.listWidget_contacts.currentRow()

        self.ui.pushButton_delete_user.setEnabled(True)
        self.ui.pushButton_send_message.setEnabled(True)
        self.check_messages()

    def unlog(self):
        try:
            conn = connect("./user_log.sqlite")
            cursor = conn.cursor()
            cursor.execute('DELETE FROM User_log')
            conn.commit()
            conn.close()
            closemes = QtWidgets.QMessageBox()
            closemes.setWindowTitle("Внимание")
            closemes.setText("Приложение будет перезапущено")
            closemes.buttonClicked.connect(self.close)
            closemes = closemes.exec_()
        except Exception as ex:
            print(ex, "unlog_error")

    def add_contact(self):
        text, ok = QtWidgets.QInputDialog.getText(
            self, 'Добавление контакта', 'Введите имя пользователя')
        if ok and text != "":
            if text != self.login:
                try:
                    from_user = self.login.lower()
                    to_user = text.lower()
                    data = {"from_user": from_user, "to_user": to_user}
                    response = post(
                        f"{response_address}/friendship_request", data=data)
                    if response.status_code == 200:
                        closemes = QtWidgets.QMessageBox()
                        closemes.setWindowTitle("Успех")
                        closemes.setText(
                            f"Запрос на добавление отправлен контакту {to_user}")
                        closemes.buttonClicked.connect(
                            closemes.close)
                        closemes = closemes.exec_()

                    elif response.status_code == 404:
                        closemes = QtWidgets.QMessageBox()
                        closemes.setWindowTitle("Ошибка")
                        closemes.setText(
                            f"Пользователя {to_user} не существует")
                        closemes.buttonClicked.connect(
                            closemes.close)
                        closemes = closemes.exec_()

                    elif response.status_code == 406:
                        closemes = QtWidgets.QMessageBox()
                        closemes.setWindowTitle("Ошибка")
                        closemes.setText(
                            "Запрос уже был отправлен или пользователь уже в друзьях")
                        closemes.buttonClicked.connect(
                            closemes.close)
                        closemes = closemes.exec_()
                except Exception as ex:
                    print(ex)
            else:
                closemes = QtWidgets.QMessageBox()
                closemes.setWindowTitle("Ошибка")
                closemes.setText(
                    "Вы не можете отправить запроc самому себе")
                closemes.buttonClicked.connect(
                    closemes.close)
                closemes = closemes.exec_()

        # self.w4 = Add_contact(self)
        # self.w4.show()

    def check_new_contacts(self):
        try:
            response = post(
                f"{response_address}/friendship_requests_check", data={"login": self.login})
            # print(response)
            if response.status_code == 200:
                self.w7 = Check_contacts_dialog(self, response.text)
                self.w7.show()
            else:
                self.timer.singleShot(5000, self.check_new_contacts)

        except Exception as ex:
            print(ex)

    def check_old_contacts(self):
        response = post(f"{response_address}/friends_check", data={"login": self.login})

        if response.status_code == 200:
            if len(response.text.split(" ")) > len(self.contacts_list):
                if not self.contacts_list:
                    self.ui.listWidget_contacts.clear()
                    self.contacts_list = response.text.split(" ")
                    for i in self.contacts_list:
                        self.ui.listWidget_contacts.addItem(i)

                else:
                    diff = list(set(response.text.split(" ")).difference(set(self.contacts_list)))
                    closemes = QtWidgets.QMessageBox()
                    closemes.setWindowTitle("Уведомление")
                    closemes.setText(f"Пользователь {diff[0]} принял вашу заявку в дрьзья")
                    closemes.buttonClicked.connect(closemes.close)
                    closemes = closemes.exec_()

                    self.contacts_list = response.text.split(" ")

                    self.ui.listWidget_contacts.clear()
                    for i in self.contacts_list:
                        self.ui.listWidget_contacts.addItem(i)

            elif len(response.text.split(" ")) < len(self.contacts_list):
                diff = list(set(self.contacts_list).difference(set(response.text.split(" "))))
                closemes = QtWidgets.QMessageBox()
                closemes.setWindowTitle("Уведомление")
                closemes.setText(f"Пользователь {diff[0]} удалил вас")
                closemes.buttonClicked.connect(closemes.close)
                closemes = closemes.exec_()

                self.contacts_list = response.text.split(" ")

                self.ui.listWidget_contacts.clear()
                for i in self.contacts_list:
                    self.ui.listWidget_contacts.addItem(i)

        self.timer.singleShot(10000, self.check_old_contacts)

    def delete_contact(self):
        self.w8 = Delete_contact_dialog(self)
        self.w8.show()

    def message_def(self):
        try:
            if self.ui.lineEdit_message.text != "":
                response = post(f"{response_address}/message", data={"from_user":self.login, "to_user":self.ui.listWidget_contacts.currentItem().text(), "message_text":self.ui.lineEdit_message.text()})
                print(response)
                if response.status_code == 200:
                    self.check_messages()

                else:
                    for i in range(5):
                        response = post(f"{response_address}/message", data={"from_user":self.login, "to_user":self.ui.listWidget_contacts.currentItem().text(), "message_text":self.ui.lineEdit_message.text()})
                        if response.status_code == 200:
                            self.check_messages()
                            break

                        elif i == 4:
                            closemes = QtWidgets.QMessageBox()
                            closemes.setWindowTitle("Ошибка")
                            closemes.setText("Ошибка отправки сообщения")
                            closemes.buttonClicked.connect(closemes.close)
                            closemes = closemes.exec_()

                self.ui.lineEdit_message.clear()
        except Exception as ex:
            closemes = QtWidgets.QMessageBox()
            closemes.setWindowTitle("Ошибка")
            closemes.setText("Ошибка отправки сообщения")
            closemes.buttonClicked.connect(closemes.close)
            closemes = closemes.exec_()

    def check_messages(self):
        try:
            if self.ui.listWidget_contacts.currentItem() != None:
                response = post(f"{response_address}/check_messages", data={"from_user":self.login, "to_user":self.ui.listWidget_contacts.currentItem().text()})
                # print(response)
                if response.status_code == 200:
                    # print(response.json())
                    a = str()
                    data = response.json()
                    # print(data)
                    for i in data:
                        a += f'{data[i][0]} : {data[i][1]}' + '\n'
                    self.ui.textBrowser_chat.setText(a)

                self.timer.singleShot(1000, self.check_messages)
                # self.ui.listWidget_contacts.currentItem().setSelected(True)
            else:
                self.ui.listWidget_contacts.clear()
        except Exception as ex:
            print(ex, "check_messages_error")

class Login(QtWidgets.QWidget):
    def __init__(self, parent=MyWin):
        super(Login, self).__init__()
        self.ui = Ui_Login()
        self.ui.setupUi(self)
        self.parent = parent

        self.ui.pushButton_authorize.clicked.connect(self.login_def)

    def login_def(self):
        if self.ui.lineEdit_login.text().strip() != "" and self.ui.lineEdit_password.text().strip() != "":
            try:
                login = self.ui.lineEdit_login.text().lower()
                if not findall('[^..\w!@#\$%\^&\*\(\)\-_\+=;:,\./\?\\\|`~\[\]\{\}]', login):
                    password = self.ui.lineEdit_password.text()
                    if not findall('[^..\w!@#\$%\^&\*\(\)\-_\+=;:,\./\?\\\|`~\[\]\{\}]', password):
                        data = {"login": login, "password": password}
                        response = post(
                            f"{response_address}/login", data=data)
                        if response.status_code == 200:
                            closemes = QtWidgets.QMessageBox()
                            closemes.setWindowTitle("Успех")
                            closemes.setText("Подключение установлено")
                            closemes.buttonClicked.connect(self.close)
                            closemes = closemes.exec_()

                            conn = connect("user_log.sqlite")
                            cursor = conn.cursor()
                            cursor.execute(f'INSERT INTO User_log VALUES("{login}", "{password}")')
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

                            self.parent.check_new_contacts()
                            self.parent.check_old_contacts()

                        if response.status_code == 404:
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

            except Exception as ex:
                print(ex, "login_error")
                closemes = QtWidgets.QMessageBox()
                closemes.setWindowTitle("Ошибка")
                closemes.setText("Ошибка подключения")
                closemes.buttonClicked.connect(closemes.close)
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
    def __init__(self, parent=MyWin):
        super(Registration, self).__init__()
        self.ui = Ui_Registration()
        self.ui.setupUi(self)
        self.parent = parent

        self.ui.pushButton_reg.clicked.connect(self.registration)
        self.parent.setEnabled(False)

    def registration(self):
        try:
            email = self.ui.lineEdit_email.text().lower()
            self.login = self.ui.lineEdit_login.text().lower()
            self.password = self.ui.lineEdit_password.text()
            password_2 = self.ui.lineEdit_password_2.text()
            if email != "" and self.login != "" and self.password != "" and password_2 != "":
                if self.password == password_2:
                    if match(
                            '^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$',
                            email) != None:
                        if not findall('[^..\w!@#\$%\^&\*\(\)\-_\+=;:,\./\?\\\|`~\[\]\{\}]', self.login):
                            if not findall('[^..\w!@#\$%\^&\*\(\)\-_\+=;:,\./\?\\\|`~\[\]\{\}]', self.password):
                                response = post(f"{response_address}/registration", data={
                                    "email": email, "login": self.login, "password": self.password})
                                print(response)
                                if response.status_code == 200:
                                    self.dialog = Email_dialog(self)
                                    self.dialog.show()

                                elif response.status_code == 403:
                                    closemes = QtWidgets.QMessageBox()
                                    closemes.setWindowTitle("Ошибка")
                                    closemes.setText(
                                        "Пользователь с такими данными уже существует")
                                    closemes.buttonClicked.connect(
                                        closemes.close)
                                    closemes = closemes.exec_()

                                elif response.status_code == 550:
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
    def __init__(self, parent=Registration):
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

                if response.status_code == 200:
                    conn = connect("./user_log.sqlite")
                    cursor = conn.cursor()
                    cursor.execute(f'INSERT INTO User_log VALUES ("{self.login}", "{self.password}")')
                    conn.commit()
                    conn.close()

                    closemes = QtWidgets.QMessageBox()
                    closemes.setWindowTitle("Успех")
                    closemes.setText(
                        "Регистрация прошла успешно")
                    closemes.buttonClicked.connect(
                        self.close)
                    closemes = closemes.exec_()



                elif response.status_code == 403:
                    closemes = QtWidgets.QMessageBox()
                    closemes.setWindowTitle("Ошибка")
                    closemes.setText(
                        "Проверьте правильность ввода кода подтверждения")
                    closemes.buttonClicked.connect(
                        closemes.close)
                    closemes = closemes.exec_()
            except Exception as ex:
                print(ex)
                closemes = QtWidgets.QMessageBox.critical(
                    self, "Ошибка", "Ошибка подключения")
                closemes.buttonClicked.connect(
                    closemes.close)
                closemes = closemes.exec_()

    def closeEvent(self, event):
        self.hide()
        self.parent.close()
        try:
            self.parent.parent.auto_login_def()
            post(f"{response_address}/email_verification_delete",
                 data={"email": self.email, "login": self.login})
        except:
            pass


class Check_contacts_dialog(QtWidgets.QDialog):
    def __init__(self, parent=MyWin, from_user=None):
        super().__init__(parent)

        self.setWindowTitle("Запрос в друзья")
        self.parent = parent
        self.from_user = from_user

        QBtn = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel

        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout = QtWidgets.QVBoxLayout()
        message = QtWidgets.QLabel(f"Запрос в друзья от {self.from_user}")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def accept(self) -> None:
        try:
            response = post(f"{response_address}/friendship_requests_check_yes",
                            data={"to_login": self.parent.login, "from_login": self.from_user})
            print(response.status_code)
            if response.status_code == 200:
                self.parent.ui.listWidget_contacts.addItem(self.from_user)
                self.parent.contacts_list.append(self.from_user)
                self.hide()
                # self.parent.check_old_contacts()
                self.parent.check_new_contacts()
            else:
                print(response.status_code)
                closemes = QtWidgets.QMessageBox()
                closemes.setWindowTitle("Ошибка")
                closemes.setText("Неизвестная ошибка")
                closemes.buttonClicked.connect(closemes.hide)
                closemes = closemes.exec_()
        except Exception as ex:
            print(ex)

    def reject(self) -> None:
        response = post(f"{response_address}/friendship_requests_check_no", data={"to_login": self.parent.login, "from_login": self.from_user})
        self.hide()
        # self.parent.check_new_contacts()


class Delete_contact_dialog(QtWidgets.QDialog):
    def __init__(self, parent=MyWin):
        super().__init__(parent)

        self.setWindowTitle("Подтвердите действие")
        self.parent = parent

        QBtn = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel

        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout = QtWidgets.QVBoxLayout()
        message = QtWidgets.QLabel(
            f"Вы действительно хотите удалить контакт {self.parent.ui.listWidget_contacts.currentItem().text()}?")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def accept(self) -> None:
        try:
            self.parent.ui.textBrowser_chat.clear()

            response = post(f"{response_address}/delete_friend",
                            data={"from_login": self.parent.login,
                                  "delete_login": self.parent.ui.listWidget_contacts.currentItem().text()})
            if response.status_code == 200:
                for i in self.parent.contacts_list:
                    if i == self.parent.ui.listWidget_contacts.currentItem().text():
                        self.parent.contacts_list.pop(self.parent.ui.listWidget_contacts.currentRow())
                        break

                self.parent.ui.listWidget_contacts.takeItem(self.parent.ui.listWidget_contacts.currentRow())

                self.hide()

            if self.parent.ui.listWidget_contacts.count() == 0:
                self.parent.ui.pushButton_send_message.setEnabled(False)
                self.parent.ui.pushButton_delete_user.setEnabled(False)


                # self.parent.check_old_contacts()
            else:
                closemes = QtWidgets.QMessageBox()
                closemes.setWindowTitle("Ошибка")
                closemes.setText("Неизвестная ошибка")
                closemes.buttonClicked.connect(self.hide)
                closemes = closemes.exec_()
        except Exception as ex:
            print(ex)


if __name__ == "__main__":
    app = QtWidgets.QApplication(argv)
    myapp = MyWin()
    myapp.show()
    exit(app.exec_())
