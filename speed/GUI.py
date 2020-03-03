#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
ZetCode PyQt5 tutorial

In this example, we receive data from
a QInputDialog dialog.

Aauthor: Jan Bodnar
Website: zetcode.com
Last edited: August 2017
"""

from PyQt5.QtWidgets import (QWidget, QPushButton, QLineEdit,
                             QInputDialog, QApplication, QFileDialog, QCheckBox, QLabel)
import sys
import os


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.btn = QPushButton('Vehicle video', self)
        self.btn.move(20, 20)
        self.btn.clicked.connect(self.openFileNameDialog)

        self.btn2 = QPushButton('Pedestrian video', self)
        self.btn2.move(20, 50)
        self.btn2.clicked.connect(self.openFileNameDialog2)

        self.btn3 = QPushButton('Start', self)
        self.btn3.move(20, 120)
        self.btn3.clicked.connect(self.exe_another)

        self.le = QLineEdit(self)
        self.le.move(130, 20)

        self.le2 = QLineEdit(self)
        self.le2.move(130, 50)

        self.ckbox = QCheckBox('mask', self)
        self.ckbox.move(250, 20)

        self.lbl1 = QLabel('Frame Ratio', self)
        self.lbl1.move(20, 80)

        self.lbl2 = QLabel('Vehicle', self)
        self.lbl2.move(80, 80)

        self.lbl3 = QLabel('Pedestrians', self)
        self.lbl3.move(80, 100)

        self.le3 = QLineEdit(self)
        self.le3.move(130, 80)

        self.le4 = QLineEdit(self)
        self.le4.move(130, 100)

        self.ckbox2 = QCheckBox('Reference Speed mode', self)
        self.ckbox2.move(130, 125)

        self.setGeometry(300, 300, 290, 150)
        self.setWindowTitle('Control Center')
        self.show()

    def showDialog(self):
        text, ok = QInputDialog.getText(self, 'Input Dialog',
                                        'Enter your name:')

        if ok:
            self.le.setText(str(text))

    def exe_another(self):
        buff = "no"
        if self.ckbox.isChecked():
            buff = "yes"

        buff2 = "no"
        if self.ckbox2.isChecked():
            buff2 = "yes"
        comnd = "python Real-time.py " + "-i1 " + self.le.text() + " -i2 " + self.le2.text() + " -i3 " + buff + " -i4 " + self.le3.text() + " -i5 " + self.le4.text() + " -i6 " + buff2
        print(comnd)
        os.system(comnd)

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            print(fileName)
            self.le.setText(str(fileName))
    def test(self):
        print("")
    def openFileNameDialog2(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            print(fileName)
            self.le2.setText(str(fileName))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())