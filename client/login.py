# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\login.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Login(object):
    def setupUi(self, Login):
        Login.setObjectName("Login")
        Login.resize(400, 600)
        Login.setMinimumSize(QtCore.QSize(400, 600))
        Login.setMaximumSize(QtCore.QSize(400, 600))
        self.centralwidget = QtWidgets.QWidget(Login)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 0, 0, 1, 1)
        self.label_login = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setStyleStrategy(QtGui.QFont.PreferDefault)
        self.label_login.setFont(font)
        self.label_login.setAlignment(QtCore.Qt.AlignCenter)
        self.label_login.setObjectName("label_login")
        self.gridLayout.addWidget(self.label_login, 1, 0, 1, 1)
        self.pushButton_authorize = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.pushButton_authorize.setFont(font)
        self.pushButton_authorize.setObjectName("pushButton_authorize")
        self.gridLayout.addWidget(self.pushButton_authorize, 6, 0, 1, 1)
        self.lineEdit_login = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.lineEdit_login.sizePolicy().hasHeightForWidth())
        self.lineEdit_login.setSizePolicy(sizePolicy)
        self.lineEdit_login.setMinimumSize(QtCore.QSize(200, 50))
        self.lineEdit_login.setObjectName("lineEdit_login")
        self.gridLayout.addWidget(self.lineEdit_login, 2, 0, 1, 1)
        self.lineEdit_password = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_password.sizePolicy().hasHeightForWidth())
        self.lineEdit_password.setSizePolicy(sizePolicy)
        self.lineEdit_password.setMinimumSize(QtCore.QSize(200, 50))
        self.lineEdit_password.setMaximumSize(QtCore.QSize(399, 120))
        self.lineEdit_password.setObjectName("lineEdit_password")
        self.gridLayout.addWidget(self.lineEdit_password, 4, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 5, 0, 1, 1)
        self.label_password = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_password.setFont(font)
        self.label_password.setAlignment(QtCore.Qt.AlignCenter)
        self.label_password.setObjectName("label_password")
        self.gridLayout.addWidget(self.label_password, 3, 0, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout)
        Login.setCentralWidget(self.centralwidget)

        self.retranslateUi(Login)
        QtCore.QMetaObject.connectSlotsByName(Login)

    def retranslateUi(self, Login):
        _translate = QtCore.QCoreApplication.translate
        Login.setWindowTitle(_translate("Login", "MainWindow"))
        self.label_login.setText(_translate("Login", "Логин"))
        self.pushButton_authorize.setText(_translate("Login", "Авторизоваться"))
        self.label_password.setText(_translate("Login", "Пароль"))
