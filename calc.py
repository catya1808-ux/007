from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(300, 400)
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Display
        self.label_result = QtWidgets.QLabel(self.centralwidget)
        self.label_result.setGeometry(QtCore.QRect(10, 10, 280, 50))
        self.label_result.setStyleSheet("font-size: 20px; border: 1px solid gray;")
        self.label_result.setAlignment(QtCore.Qt.AlignRight)
        self.label_result.setText("0")
        
        # Buttons grid
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', 'C', '=', '+'
        ]
        
        positions = [(i%4, i//4) for i in range(len(buttons))]
        
        for pos, name in zip(positions, buttons):
            button = QtWidgets.QPushButton(name, self.centralwidget)
            button.setGeometry(QtCore.QRect(10 + pos[0]*70, 70 + pos[1]*70, 65, 65))
            button.clicked.connect(lambda _, x=name: self.button_click(x))
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        # Calculator state
        self.is_equal = False

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Калькулятор"))

    def button_click(self, value):
        if self.is_equal:
            self.label_result.setText("0")
            self.is_equal = False
            
        text = self.label_result.text()
        
        if value == 'C':
            self.label_result.setText("0")
        elif value == '=':
            try:
                res = eval(text)
                self.label_result.setText(str(res))
                self.is_equal = True
            except:
                self.label_result.setText("Ошибка")
        else:
            if text == '0':
                self.label_result.setText(value)
            else:
                self.label_result.setText(text + value)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())