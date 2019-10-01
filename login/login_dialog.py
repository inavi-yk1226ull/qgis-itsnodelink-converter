# -*- coding: utf-8 -*-
import qgis, os

from PyQt5 import uic, QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QAction, QMessageBox
from qgis.core import QgsMessageLog
from .LoginModule.Account import UserAccount 


import datetime, time

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'login_dialog.ui'))

class LoginDialog(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)
        self.setupUi(self)
        self.name = ""
        pass

    def btn_reject(self):
        qbox = QMessageBox()
        qbox.setWindowModality(True)
        qbox.setWindowTitle("로그인")
        qbox.setText("로그인을 취소합니다.")
        qbox.setStandardButtons(QMessageBox.Yes)
        reply = qbox.exec_()
        self.close()
        self.setResult(0)
    
    def btn_accept(self):
        ua = UserAccount.UserAccount("Plugin")
        result, msg = ua.ServerLogin(self.tb_id.text(), self.tb_pw.text())
        qbox = QMessageBox()
        qbox.setWindowModality(True)
        qbox.setWindowTitle("로그인")
        qbox.setText(msg)
        qbox.setStandardButtons(QMessageBox.Yes)
        self.name = self.tb_id.text()
        reply = qbox.exec_()
        self.close()
        self.setResult(result)
    
    def show(self, iface):
        self.iface = iface
        super(LoginDialog, self).show()
        
    pass # class