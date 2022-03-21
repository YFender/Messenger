from PyQt5 import QtWidgets

closemes = QtWidgets.QMessageBox()
lineEdit_check = QtWidgets.QLineEdit(
    closemes)
closemes.addItem()
closemes.setWindowTitle("Успех")
closemes.setText(
    "На ваш Email пришел код")
closemes.buttonClicked.connect(lambda: print("asdasd"))
# closemes = closemes.exec_()
