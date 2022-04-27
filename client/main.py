from os import path, remove
from re import findall, match
from sqlite3 import connect
from sys import argv, exit

from PyQt5 import QtWidgets, QtCore
from requests import post

"""Импорт отдельно прописанных интерфейсов"""
from client import Ui_Client_MainWindow
from email_dialog import Ui_Dialog
from login import Ui_Login
from registration import Ui_Registration

from time import sleep
from collections import deque

response_address = "http://localhost:8080" # переменная основного адреса HTTP-запросов. Была создана для упрощения отладки.

"""Класс главного окна, в нем происходит основная работа программы"""
class MyWin(QtWidgets.QMainWindow):
    """Инициализация инструментов, с которыми придется работать"""
    def __init__(self, parent=None):
        """Инициализация интерфейса"""
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Client_MainWindow()
        self.ui.setupUi(self)

        """Создание коллекций для последующего хранения списка контактов и сообщений"""
        self.contacts_list = []
        self.messages = {}
        self.selected_contact = None

        """Скрытие и отключение отдельных элементов интерфейса перед авторизацией"""
        self.ui.label_unlog.hide()
        self.ui.pushButton_unlog.hide()
        self.ui.tab_chat.setEnabled(False)

        """Таймеры, будут запущены позже для проверки наличия сообщений и состояния списка друзей"""
        self.timer_check_messages = QtCore.QTimer()
        self.timer_check_new_contacts = QtCore.QTimer()
        self.timer_check_old_contacts = QtCore.QTimer()

        """Инициализация выполнения функций по истечению времени в таймерах"""
        self.timer_check_new_contacts.timeout.connect(self.check_new_contacts)
        self.timer_check_old_contacts.timeout.connect(self.check_old_contacts)
        self.timer_check_messages.timeout.connect(self.check_messages)

        """Инициализация триггеров, если пользователь кликнет на определенную кнопку"""
        self.ui.login_pushbutton.clicked.connect(self.login_def)
        self.ui.reg_pushbutton.clicked.connect(self.registration)
        self.ui.pushButton_unlog.clicked.connect(self.unlog)
        self.ui.pushButton_send_message.clicked.connect(self.message_def)

        """Инициализация горячей клавиши для кнопки отправки сообщения"""
        self.ui.pushButton_send_message.setShortcut("Return")

        """Отключение кнопок 'добавить' и 'удалить', пока пользователь не выберет какой-либо контакт"""
        """Используется как 'защита от дурака'"""
        self.ui.pushButton_delete_user.setEnabled(False)
        self.ui.pushButton_send_message.setEnabled(False)

        """Инициализация триггеров, если пользователь выберет контакт или сделает с ним какое-либо действие"""
        self.ui.listWidget_contacts.itemClicked.connect(self.select_contact)
        self.ui.pushButton_add_contact.clicked.connect(self.add_contact)
        self.ui.pushButton_delete_user.clicked.connect(self.delete_contact)

        """Функция автоматического логина, если пользователь уже заходил с этого устройства"""
        self.auto_login_def()



    def auto_login_def(self):
        try:
            """Если файла БД не существует"""
            if not path.isfile("./user_log.sqlite"):
                """Автоматический переход к окну с регистрацией/логином"""
                self.ui.tabWidget.setCurrentIndex(1)
                """Отключение интерфейса чата"""
                self.ui.tab_chat.setEnabled(False)

                """Создание файла БД sqlite и подключение к ней"""
                conn = connect("user_log.sqlite")
                cursor = conn.cursor()
                """Формирование запроса создания таблицы БД и его выполнение"""
                cursor.execute(
                    "CREATE TABLE User_log(Login VARCHAR(20) NOT NULL, Password VARCHAR(20) NOT NULL)")
                conn.commit()
                """Закрытие подключения к БД для экономии оперативной памяти"""
                conn.close()
            else:
                """Если файл БД существует"""

                """Подключение к БД"""
                conn = connect("user_log.sqlite")
                cursor = conn.cursor()

                """Запрос на считывание информации о логине и пароле пользователя"""
                cursor.execute(
                    "SELECT Login, Password FROM User_log")
                result = cursor.fetchone()

                if result:
                    """Если есть какой-то результат"""
                    self.login, self.password = result[0], result[1]
                    result = {"login": self.login, "password": self.password}

                    """Отправка запроса серверу на логин с информацией о логине и пароле"""
                    response_login = post(
                        f"{response_address}/login", data=result)

                    """Если сервер нашел соответствие и удовлетворен"""
                    if response_login.status_code == 200:
                        """Появление окна с сообщением об успехе"""
                        closemes = QtWidgets.QMessageBox()
                        closemes.setWindowTitle("Успех")
                        closemes.setText("Подключение установлено")
                        closemes.buttonClicked.connect(closemes.close)
                        closemes = closemes.exec_()

                        """Включение элементов интерфейса и открытие доступа к использованию"""
                        self.ui.tab_chat.setEnabled(True)
                        self.ui.login_pushbutton.hide()
                        self.ui.reg_pushbutton.hide()
                        self.ui.label_unlog.setText(
                            f"Авторизован как {self.login}")
                        self.ui.tabWidget.setCurrentIndex(0)
                        self.ui.label_unlog.show()
                        self.ui.pushButton_unlog.show()

                        """Проверка запросов в друзья и проверка старых друзей"""
                        self.check_new_contacts()
                        self.check_old_contacts()

                        """Запуск таймеров проверки старых друзей, запросов в друзья и наличия сообщений (время в мс)"""
                        self.timer_check_new_contacts.start(5000)
                        self.timer_check_messages.start(1000)
                        self.timer_check_old_contacts.start(10000)

                        """Если сервер не нашел соответствия и не удовлетворен"""
                    elif response_login.status_code == 404:
                        closemes = QtWidgets.QMessageBox()
                        closemes.setWindowTitle("Ошибка")
                        closemes.setText("Проверьте правильность логина/пароля")
                        closemes.buttonClicked.connect(self.close)
                        closemes = closemes.exec_()
                        remove("./user_log.sqlite")

                    """Если никакого результата"""
                else:
                    """Отключение интерфейса"""
                    self.ui.tabWidget.setCurrentIndex(1)
                    self.ui.tab_chat.setEnabled(False)
                conn.close()

            """Если произошла непредвиденная ошибка"""
        except Exception as ex:
            print(ex, "autologin error")
            closemes = QtWidgets.QMessageBox()
            closemes.setWindowTitle("Ошибка")
            closemes.setText("Ошибка подключения")
            closemes.buttonClicked.connect(closemes.close)
            closemes = closemes.exec_()

    """Метод, вызывающий диалоговое окно логина при нажатии на соответствующую кнопку"""
    def login_def(self):
        self.w2 = Login(self)
        self.w2.show()


    """Метод, вызывающий диалоговое окно регистрации при нажатии на соответствующую кнопку"""
    def registration(self):
        self.w3 = Registration(self)
        self.w3.show()

    """Функция, выполняющаяся, если пользователь кликнул на контакт"""
    def select_contact(self):
        if self.selected_contact != self.ui.listWidget_contacts.currentRow():
            self.selected_contact = self.ui.listWidget_contacts.currentRow()

            self.check_messages()

        self.ui.pushButton_delete_user.setEnabled(True)
        self.ui.pushButton_send_message.setEnabled(True)


    """Функция разлогирования"""
    def unlog(self):
        try:
            """Подключение к БД пользователя и удаление его данных"""
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

    """Функция, выполняющаяся, если пользователь хочет добавить кого-то в друзья"""
    def add_contact(self):
        text, ok = QtWidgets.QInputDialog.getText(
            self, 'Добавление контакта', 'Введите имя пользователя')

        """Если нажата клавиша ОК и пользователь ввел логин"""
        if ok and text != "":
            """Если пользователь ввел НЕ свой логин"""
            if text != self.login:
                try:
                    from_user = self.login.lower()
                    to_user = text.lower()
                    data = {"from_user": from_user, "to_user": to_user}
                    """Отправка запроса на добавлене в друзья с информацией о себе и логине другого пользователя"""
                    response = post(
                        f"{response_address}/friendship_request", data=data)

                    """Если сервер нашел такого пользователя и удовлетворен"""
                    if response.status_code == 200:
                        closemes = QtWidgets.QMessageBox()
                        closemes.setWindowTitle("Успех")
                        closemes.setText(
                            f"Запрос на добавление отправлен контакту {to_user}")
                        closemes.buttonClicked.connect(
                            closemes.close)
                        closemes = closemes.exec_()

                        """Если сервер не нашел такого пользователя"""
                    elif response.status_code == 404:
                        closemes = QtWidgets.QMessageBox()
                        closemes.setWindowTitle("Ошибка")
                        closemes.setText(
                            f"Пользователя {to_user} не существует")
                        closemes.buttonClicked.connect(
                            closemes.close)
                        closemes = closemes.exec_()

                        """Если заявка была отправлена ранее или искомый пользователь уже в друзьях"""
                    elif response.status_code == 406:
                        closemes = QtWidgets.QMessageBox()
                        closemes.setWindowTitle("Ошибка")
                        closemes.setText(
                            "Запрос уже был отправлен или пользователь уже в друзьях")
                        closemes.buttonClicked.connect(
                            closemes.close)
                        closemes = closemes.exec_()

                except Exception as ex:
                    """Непредвиденная ошибка"""
                    print(ex)

                """Если пользователь попытался ввести свой логин"""
            else:
                closemes = QtWidgets.QMessageBox()
                closemes.setWindowTitle("Ошибка")
                closemes.setText(
                    "Вы не можете отправить запроc самому себе")
                closemes.buttonClicked.connect(
                    closemes.close)
                closemes = closemes.exec_()

    """Проверка заявок в друзья"""
    def check_new_contacts(self):
        try:
            """Отправка запроса на проверку заявок"""
            response = post(
                f"{response_address}/friendship_requests_check", data={"login": self.login})

            """Если заявки найдены"""
            if response.status_code == 200:
                """Вызов диалогового окна"""
                self.w7 = Check_contacts_dialog(self, response.text)
                self.w7.show()

        except Exception as ex:
            print(ex)

    """Функция проверки состояния списка друзей"""
    def check_old_contacts(self):
        """Отправка запроса на проверку"""
        response = post(f"{response_address}/friends_check", data={"login": self.login})

        """Если сервер нашел друзей"""
        if response.status_code == 200:
            """Если полученный список больше имеющегося"""
            if len(response.text.split(" ")) > len(self.contacts_list):
                """Если внутренний список пустой (например, если пользователь только-только авторизовался)"""
                if not self.contacts_list:
                    """Обновление списка друзей и добавление контактов в список"""
                    self.ui.listWidget_contacts.clear()
                    self.contacts_list = response.text.split(" ")
                    for i in self.contacts_list:
                        self.ui.listWidget_contacts.addItem(i)

                    """Если внутренний список контактов не пустой"""
                else:
                    """Высчитывание разницы между полученным списком и имеющимся списком"""
                    diff = list(set(response.text.split(" ")).difference(set(self.contacts_list)))

                    """Уведомление о новом друге"""
                    closemes = QtWidgets.QMessageBox()
                    closemes.setWindowTitle("Уведомление")
                    closemes.setText(f"Пользователь {diff[0]} принял вашу заявку в друзья")
                    closemes.buttonClicked.connect(closemes.close)
                    closemes = closemes.exec_()

                    """Обновление списка"""
                    self.contacts_list = response.text.split(" ")

                    self.ui.listWidget_contacts.clear()
                    for i in self.contacts_list:
                        self.ui.listWidget_contacts.addItem(i)

                """Если полученный список короче имеющегося"""
            elif len(response.text.split(" ")) < len(self.contacts_list):
                """Просчет разницы"""
                diff = list(set(self.contacts_list).difference(set(response.text.split(" "))))

                """Уведомление об удалении из друзей"""
                closemes = QtWidgets.QMessageBox()
                closemes.setWindowTitle("Уведомление")
                closemes.setText(f"Пользователь {diff[0]} удалил вас")
                closemes.buttonClicked.connect(closemes.close)
                closemes = closemes.exec_()

                """Обновление списка"""
                self.contacts_list = response.text.split(" ")

                self.ui.listWidget_contacts.clear()
                for i in self.contacts_list:
                    self.ui.listWidget_contacts.addItem(i)

    """Функция, выполняющаяся при удалении контакта"""
    def delete_contact(self):
        self.w8 = Delete_contact_dialog(self)
        self.w8.show()

    """Функция отправки сообщения"""
    def message_def(self):
        try:
            """Если текст в поле не пустой"""
            if self.ui.lineEdit_message.text() != "":
                """Отправка запроса: текст сообщения, от кого, кому"""
                response = post(f"{response_address}/message", data={"from_user":self.login, "to_user":self.ui.listWidget_contacts.currentItem().text(), "message_text":self.ui.lineEdit_message.text()})

                """Если сервер НЕ получил запрос и неудовлетворен"""
                if response.status_code != 200:
                    """Цикл попыток отправки сообщения"""
                    for i in range(15):
                        """Отправка запроса"""
                        response = post(f"{response_address}/message", data={"from_user":self.login, "to_user":self.ui.listWidget_contacts.currentItem().text(), "message_text":self.ui.lineEdit_message.text()})

                        """Если сервер получил запрос и удовлетворен"""
                        if response.status_code == 200:
                            """Проверка и обновление сообщений"""
                            self.check_messages()
                            """Прерывание цикла"""
                            break

                            """Если произошло 15 попыток и сервер до сих пор не удовлетворен"""
                        elif i == 14:
                            closemes = QtWidgets.QMessageBox()
                            closemes.setWindowTitle("Ошибка")
                            closemes.setText("Ошибка отправки сообщения")
                            closemes.buttonClicked.connect(closemes.close)
                            closemes = closemes.exec_()

                        sleep(200)
                else:
                    self.check_messages()

                self.ui.lineEdit_message.clear()

        except Exception as ex:
            """Непредвиденная ошибка"""
            closemes = QtWidgets.QMessageBox()
            closemes.setWindowTitle("Ошибка")
            closemes.setText("Ошибка отправки сообщения")
            closemes.buttonClicked.connect(closemes.close)
            closemes = closemes.exec_()

    """Функция проверки наличия сообщений"""
    def check_messages(self):
        try:
            """Если выбран контакт из списка"""
            if self.ui.listWidget_contacts.currentItem() != None:
                """Запрос проверки сообщений этому контакту"""
                response = post(f"{response_address}/check_messages", data={"from_user":self.login, "to_user":self.ui.listWidget_contacts.currentItem().text()})

                """Если сервер удовлетворен"""
                if response.status_code == 200:
                    """Прием текста сообщений"""
                    data = response.json()

                    """Если в имеющемся списке уже есть сообщения"""
                    if self.messages:
                        """И последние сообщения различаются"""
                        if deque(self.messages)[-1] != deque(data)[-1]:
                            """Обновить окно сообщений"""
                            self.ui.textBrowser_chat.clear()
                            self.messages = data
                            a = str()
                            for i in self.messages:
                                a += f'{self.messages[i][0]} : {self.messages[i][1]}' + '\n'
                            self.ui.textBrowser_chat.append(a)

                        """Если ничего нет"""
                    else:
                        a = str()
                        self.messages = data
                        for i in self.messages:
                            a += f'{self.messages[i][0]} : {self.messages[i][1]}' + '\n'
                        self.ui.textBrowser_chat.append(a)

                    """Если сервер не удовлетворен"""
                else:
                    """И это не из-за того, что сообщений нет"""
                    if response.status_code != 404:
                        """До тех пор, пока сервер не ответит положительно"""
                        while response.status_code != 200:
                            """Отправка запроса на проверку сообщений"""
                            response = post(f"{response_address}/check_messages", data={"from_user": self.login, "to_user": self.ui.listWidget_contacts.currentItem().text()})

                            """Если сервер заявляет, что слишком много запросов"""
                            if response.status_code == 429:
                                """Перерыв в 500 мс"""
                                sleep(500)

                                """Если сервер заявляет о непредвиденной ошибке"""
                            elif response.status_code == 500:
                                closemes = QtWidgets.QMessageBox()
                                closemes.setWindowTitle("Ошибка")
                                closemes.setText("Неизвестная ошибка")
                                closemes.buttonClicked.connect(closemes.close)
                                closemes = closemes.exec_()
                                """Прервать цикл"""
                                break

                                """Если ни то, ни другое"""
                            else:
                                """Перерыв 200 мс"""
                                sleep(200)

                        """Перепроверка сообщений"""
                        data = response.json()
                        """Если уже имеются сообщения"""
                        if self.messages:
                            """Если последние сообщения различаются"""
                            if deque(self.messages)[-1] != deque(data)[-1]:
                                self.ui.textBrowser_chat.clear()
                                self.messages = data
                                a = str()
                                for i in self.messages:
                                    a+=f'{self.messages[i][0]} : {self.messages[i][1]}' + '\n'
                                self.ui.textBrowser_chat.append(a)
                        else:
                            a = str()
                            self.messages = data
                            for i in self.messages:
                                a += f'{self.messages[i][0]} : {self.messages[i][1]}' + '\n'
                            self.ui.textBrowser_chat.append(a)
                    else:
                        self.messages = []
        except Exception as ex:
            print(ex, "check_messages_error")
            closemes = QtWidgets.QMessageBox()
            closemes.setWindowTitle("Ошибка")
            closemes.setText("Неизвестная ошибка")
            closemes.buttonClicked.connect(closemes.close)
            closemes = closemes.exec_()

"""Класс диалогового окна логина"""
class Login(QtWidgets.QWidget):
    def __init__(self, parent=MyWin):
        super(Login, self).__init__()
        self.ui = Ui_Login()
        self.ui.setupUi(self)
        self.parent = parent

        """Триггер функции логина на нажатие кнопки"""
        self.ui.pushButton_authorize.clicked.connect(self.login_def)

    def login_def(self):
        """Если форма заполнения не пустая"""
        if self.ui.lineEdit_login.text().strip() != "" and self.ui.lineEdit_password.text().strip() != "":
            try:
                login = self.ui.lineEdit_login.text().lower()
                """Если в логине не находятся запрещенные символы"""
                if not findall('[^..\w!@#\$%\^&\*\(\)\-_\+=;:,\./\?\\\|`~\[\]\{\}]', login):
                    password = self.ui.lineEdit_password.text()
                    """Если в пароле не находятся запрещенные символы"""
                    if not findall('[^..\w!@#\$%\^&\*\(\)\-_\+=;:,\./\?\\\|`~\[\]\{\}]', password):
                        data = {"login": login, "password": password}
                        """Отправка запроса на логин"""
                        response = post(
                            f"{response_address}/login", data=data)

                        """Если информация верна и сервер удовлетворен"""
                        if response.status_code == 200:
                            closemes = QtWidgets.QMessageBox()
                            closemes.setWindowTitle("Успех")
                            closemes.setText("Подключение установлено")
                            closemes.buttonClicked.connect(self.close)
                            closemes = closemes.exec_()

                            """Создание в файле БД таблицы с данными пользователя"""
                            conn = connect("user_log.sqlite")
                            cursor = conn.cursor()
                            cursor.execute(f'INSERT INTO User_log VALUES("{login}", "{password}")')
                            conn.commit()
                            conn.close()

                            """Включение основного интерфейса и выдача доступа к нему"""
                            self.parent.ui.tab_chat.setEnabled(True)
                            self.parent.ui.login_pushbutton.hide()
                            self.parent.ui.reg_pushbutton.hide()
                            self.parent.ui.label_unlog.setText(
                                f"Авторизован как {login}")
                            self.parent.ui.label_unlog.show()
                            self.parent.ui.pushButton_unlog.show()
                            self.parent.login = login

                            """Запуска функций проверки запросов в друзья и состояния контактов, а также таймеров для этих функций"""
                            self.parent.check_new_contacts()
                            self.parent.check_old_contacts()
                            self.parent.timer_check_new_contacts.start(5000)
                            self.parent.timer_check_messages.start(1000)
                            self.parent.timer_check_old_contacts.start(10000)

                            """Если какая-либо информация не верна"""
                        elif response.status_code == 404:
                            closemes = QtWidgets.QMessageBox()
                            closemes.setWindowTitle("Ошибка")
                            closemes.setText(
                                "Проверьте правильность логина/пароля")
                            closemes.buttonClicked.connect(closemes.close)
                            closemes = closemes.exec_()

                            """Если пароль содержит запрещенные символы"""
                    else:
                        closemes = QtWidgets.QMessageBox()
                        closemes.setWindowTitle("Ошибка")
                        closemes.setText("Пароль содержит запрещенные символы")
                        closemes.buttonClicked.connect(closemes.close)
                        closemes = closemes.exec_()

                        """Если логин содержит запрещенные символы"""
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

            """Если формы заполнения пустые"""
        else:
            closemes = QtWidgets.QMessageBox()
            closemes.setWindowTitle("Ошибка")
            closemes.setText("Введите логин и пароль")
            closemes.buttonClicked.connect(closemes.close)
            closemes = closemes.exec_()

    """Если пользователь закрыл диалоговое окно"""
    def closeEvent(self, event):
        self.parent.ui.tabWidget.setEnabled(True)

"""Класс диалогового окна регистрации"""
class Registration(QtWidgets.QWidget):
    def __init__(self, parent=MyWin):
        super(Registration, self).__init__()
        self.ui = Ui_Registration()
        self.ui.setupUi(self)
        self.parent = parent

        self.ui.pushButton_reg.clicked.connect(self.registration)
        self.parent.setEnabled(False)

    """Функция регистрации"""
    def registration(self):
        try:
            email = self.ui.lineEdit_email.text().lower()
            self.login = self.ui.lineEdit_login.text().lower()
            self.password = self.ui.lineEdit_password.text()
            password_2 = self.ui.lineEdit_password_2.text()
            """Если все введенные формы не пустые"""
            if email != "" and self.login != "" and self.password != "" and password_2 != "":
                """Если оба пароля совпадают"""
                if self.password == password_2:
                    """Если email адрес соблюдает формат"""
                    if match(
                            '^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$',
                            email) != None:
                        """Если логин не содержит запрещенных символов"""
                        if not findall('[^..\w!@#\$%\^&\*\(\)\-_\+=;:,\./\?\\\|`~\[\]\{\}]', self.login):
                            """Если пароль не содержит запрещенных символов"""
                            if not findall('[^..\w!@#\$%\^&\*\(\)\-_\+=;:,\./\?\\\|`~\[\]\{\}]', self.password):

                                """Запрос на регистрацию"""
                                response = post(f"{response_address}/registration", data={
                                    "email": email, "login": self.login, "password": self.password})

                                """Если сервер получиил запрос и удовлетворен"""
                                if response.status_code == 200:
                                    """Вызов диалогового окна подтверждения регистрации через email"""
                                    self.dialog = Email_dialog(self)
                                    self.dialog.show()

                                    """Если существует пользователь с таким же логином или email"""
                                elif response.status_code == 403:
                                    closemes = QtWidgets.QMessageBox()
                                    closemes.setWindowTitle("Ошибка")
                                    closemes.setText(
                                        "Пользователь с такими данными уже существует")
                                    closemes.buttonClicked.connect(
                                        closemes.close)
                                    closemes = closemes.exec_()

                                    """Если сервер сообщил, что введенной электронной почты не существует"""
                                elif response.status_code == 550:
                                    closemes = QtWidgets.QMessageBox()
                                    closemes.setWindowTitle("Ошибка")
                                    closemes.setText(
                                        "Такой электронной почты не существует")
                                    closemes.buttonClicked.connect(
                                        closemes.close)
                                    closemes = closemes.exec_()

                            else:
                                """Если пароль содержит запрещенные символы"""
                                closemes = QtWidgets.QMessageBox()
                                closemes.setWindowTitle("Ошибка")
                                closemes.setText(
                                    "Пароль содержит запрещенные символы")
                                closemes.buttonClicked.connect(
                                    closemes.close)
                                closemes = closemes.exec_()
                        else:
                            """Если логин содержит запрещенные символы"""
                            closemes = QtWidgets.QMessageBox()
                            closemes.setWindowTitle("Ошибка")
                            closemes.setText(
                                "Логин содержит запрещенные символы")
                            closemes.buttonClicked.connect(closemes.close)
                            closemes = closemes.exec_()
                    else:
                        """Если email не соответствует формату"""
                        closemes = QtWidgets.QMessageBox()
                        closemes.setWindowTitle("Ошибка")
                        closemes.setText(
                            "Адрес электронной почты не соответствует формату или/и содержит запрещенные символы")
                        closemes.buttonClicked.connect(closemes.close)
                        closemes = closemes.exec_()
                else:
                    """Если пароли не совпадают"""
                    closemes = QtWidgets.QMessageBox()
                    closemes.setWindowTitle("Ошибка")
                    closemes.setText("Пароли не совпадают")
                    closemes.buttonClicked.connect(closemes.close)
                    closemes = closemes.exec_()
            else:
                """Если заполнены не все поля"""
                closemes = QtWidgets.QMessageBox()
                closemes.setWindowTitle("Ошибка")
                closemes.setText("Введите данные во все поля")
                closemes.buttonClicked.connect(closemes.close)
                closemes = closemes.exec_()

        except Exception as ex:
            """Непредвиденная ошибка"""
            print(ex)
            closemes = QtWidgets.QMessageBox()
            closemes.setWindowTitle("Ошибка")
            closemes.setText("Ошибка подключения")
            closemes.buttonClicked.connect(closemes.close)
            closemes = closemes.exec_()

    """Если пользователь закрыл диалоговое окно"""
    def closeEvent(self, event):
        self.parent.setEnabled(True)

"""Класс диалогового окна подтверждения регистрации"""
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

    """Функция отправки кода верификации на подтверждение"""
    def send_verification(self):
        """Если форма заполнения не пуста"""
        if self.ui.lineEdit.text() != "":
            try:
                self.check_str = self.ui.lineEdit.text().upper()
                """Отправка запроса с информацией о email, логине, пароле и коде верификации"""
                response = post(f"{response_address}/email_verification", data={
                    "email": self.email, "login": self.login, "password": self.password, "check_str": self.check_str})

                """Если сервер получил запрос и удовлетворен"""
                if response.status_code == 200:
                    """Добавление логина и пароля в БД пользователя для автоматического логина"""
                    conn = connect("./user_log.sqlite")
                    cursor = conn.cursor()
                    cursor.execute(f'INSERT INTO User_log VALUES ("{self.login}", "{self.password}")')
                    conn.commit()
                    conn.close()

                    """Запуск таймеров для проверки новых контактов, запросов в друзья и сообщений"""
                    self.parent.parent.timer_check_new_contacts.start(5000)
                    self.parent.parent.timer_check_messages.start(1000)
                    self.parent.parent.timer_check_old_contacts.start(10000)

                    closemes = QtWidgets.QMessageBox()
                    closemes.setWindowTitle("Успех")
                    closemes.setText(
                        "Регистрация прошла успешно")
                    closemes.buttonClicked.connect(
                        self.close)
                    closemes = closemes.exec_()


                    """Если сервер заявляет, что код подтверждения не совпадает"""
                elif response.status_code == 403:
                    closemes = QtWidgets.QMessageBox()
                    closemes.setWindowTitle("Ошибка")
                    closemes.setText(
                        "Проверьте правильность ввода кода подтверждения")
                    closemes.buttonClicked.connect(
                        closemes.close)
                    closemes = closemes.exec_()

            except Exception as ex:
                """Непредвиденная ошибка"""
                print(ex)
                closemes = QtWidgets.QMessageBox.critical(
                    self, "Ошибка", "Ошибка подключения")
                closemes.buttonClicked.connect(
                    closemes.close)
                closemes = closemes.exec_()

    """Если пользователь закрыл окно верификации"""
    def closeEvent(self, event):
        """Скрытие лишних интерфейсов"""
        self.hide()
        self.parent.close()
        try:
            """Попытка автологина"""
            self.parent.parent.auto_login_def()
            post(f"{response_address}/email_verification_delete",
                 data={"email": self.email, "login": self.login})
        except:
            """Если происходит какая-либо ошибка, то ничего не происходит"""
            pass

"""Класс диалогового окна подтверждения заявки в друзья"""
class Check_contacts_dialog(QtWidgets.QDialog):
    def __init__(self, parent=MyWin, from_user=None):
        super().__init__(parent)

        self.setWindowTitle("Запрос в друзья")
        self.parent = parent
        self.from_user = from_user

        QBtn = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel

        """Формирование диалогового окна"""
        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout = QtWidgets.QVBoxLayout()
        message = QtWidgets.QLabel(f"Запрос в друзья от {self.from_user}")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    """Если пользователь принял заявку"""
    def accept(self) -> None:
        try:
            """Отправка запроса серверу с подтверждением заявки"""
            response = post(f"{response_address}/friendship_requests_check_yes",
                            data={"to_login": self.parent.login, "from_login": self.from_user})

            """Если сервер получил запрос и был удовлетворен"""
            if response.status_code == 200:
                """Добавление пользователя в список друзей"""
                self.parent.ui.listWidget_contacts.addItem(self.from_user)
                self.parent.contacts_list.append(self.from_user)

                """Перепроверка контактов и проверка новых запросов"""
                self.parent.check_old_contacts()
                self.parent.check_new_contacts()

                self.hide()

            else:
                """Если сервер прислал ответ, отличный от удовлетворительного"""
                closemes = QtWidgets.QMessageBox()
                closemes.setWindowTitle("Ошибка")
                closemes.setText("Неизвестная ошибка")
                closemes.buttonClicked.connect(closemes.hide)
                closemes = closemes.exec_()

        except Exception as ex:
            print(ex)

    """Если пользователь отклонил заявку"""
    def reject(self) -> None:
        """Отправка серверу запроса с отклонением заяки"""
        response = post(f"{response_address}/friendship_requests_check_no", data={"to_login": self.parent.login, "from_login": self.from_user})
        self.hide()

"""Класс диалогового окна с подтверждением удаления пользователя"""
class Delete_contact_dialog(QtWidgets.QDialog):
    def __init__(self, parent=MyWin):
        super().__init__(parent)

        self.setWindowTitle("Подтвердите действие")
        self.parent = parent

        QBtn = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel

        """Формирование интерфейса диалогового окна"""
        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout = QtWidgets.QVBoxLayout()
        message = QtWidgets.QLabel(
            f"Вы действительно хотите удалить контакт {self.parent.ui.listWidget_contacts.currentItem().text()}?")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    """Если пользователь подтвердил удаление"""
    def accept(self) -> None:
        try:
            self.parent.ui.textBrowser_chat.clear()

            """Отправка запроса серверу на удаление пользователя из друзей"""
            response = post(f"{response_address}/delete_friend",
                            data={"from_login": self.parent.login,
                                  "delete_login": self.parent.ui.listWidget_contacts.currentItem().text()})

            """Если сервер получил и успешно выполнил запрос"""
            if response.status_code == 200:
                """Обход циклом по внутреннему списку друзей с поиском удаляемого пользователя"""
                for i in self.parent.contacts_list:
                    """Если удаляемый пользователь найден"""
                    if i == self.parent.ui.listWidget_contacts.currentItem().text():
                        """Удаление его из внутреннего списка и прерывание цикла"""
                        self.parent.contacts_list.pop(self.parent.ui.listWidget_contacts.currentRow())
                        break

                """удаление пользователя из виджета списка друзей"""
                self.parent.ui.listWidget_contacts.takeItem(self.parent.ui.listWidget_contacts.currentRow())

                """Скрытие окна"""
                self.hide()

                """Если друзей не осталось"""
                if self.parent.ui.listWidget_contacts.count() == 0:
                    """Блокировка кнопок отправки сообщений и удаления"""
                    self.parent.ui.pushButton_send_message.setEnabled(False)
                    self.parent.ui.pushButton_delete_user.setEnabled(False)

                """Если сервер прислал ответ, отличный от удовлетворительного"""
            else:
                closemes = QtWidgets.QMessageBox()
                closemes.setWindowTitle("Ошибка")
                closemes.setText("Неизвестная ошибка")
                closemes.buttonClicked.connect(self.hide)
                closemes = closemes.exec_()

        except Exception as ex:
            print(ex)

"""Иницализация программы и ее запуск"""
if __name__ == "__main__":
    app = QtWidgets.QApplication(argv)
    myapp = MyWin()
    myapp.show()
    exit(app.exec_())
