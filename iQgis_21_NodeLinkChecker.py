# -*- coding: utf-8 -*-
import hashlib
import os.path
import os
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QToolBar
from qgis.core import QgsProject, Qgis

from .login.login_dialog import LoginDialog
from .moct_checker_dialog import MoctCheckerDialog
from .resources import *
from .login.LoginModule.CryptAES256 import encrypt_Data, decrypt_Data
from .login.LoginModule.JsonToTuple import convertStrToTuple


isLocal = False


class iQgisNodeLinkChecker:

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = self.tr(u'&Moct Checker')
        self.first_start = None
        self.is_login = False
        self.isLogin = False

    def tr(self, message):
        return QCoreApplication.translate('MoctChecker', message)

    def add_action(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True, add_to_toolbar=True, status_tip=None, whats_this=None, parent=None):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        self.actions.append(action)
        return action

    def initGui(self):
        icon_path = ':/plugins/moct_checker/icon.png'
        self.main_action = self.add_action(icon_path, text='표준노드링크 검증', callback=self.run_login, parent=self.iface.mainWindow())
        self.enable_action = QAction(QIcon(None), '', self.iface.mainWindow())
        self.enable_action.triggered.connect(self.enable_plugin)
        self.enable_action.setObjectName('moct_checker')
        self.enable_action.setEnabled(False)
        self.first_start = True
        self.toolbar = self.iface.mainWindow().findChild(QToolBar, u'아이나비 툴바')
        if not self.toolbar:
            self.toolbar = self.iface.addToolBar(u'아이나비 툴바')
            self.toolbar.setObjectName(u'아이나비 툴바')
        self.toolbar.addAction(self.main_action)

    def enable_plugin(self):
        self.isLogin=True
        # 생성
        self.toolbar.addAction(self.main_action)
        self.main_action.setEnabled(True)
        pass

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu('Moct Checker', action)
            self.iface.removeToolBarIcon(action)

    def run_login(self):
        if not self.isLogin:
            # 폴더 확인 / 로그인 하세요.
            _path = os.path.abspath(os.path.dirname(__file__))
            path = os.path.join(_path, "../iQgis_00_Common")
            if os.path.isdir(path):
                self.iface.messageBar().pushMessage("로그인이 필요합니다.", "", level=Qgis.Info, duration=2)
            else:
                self.iface.messageBar().pushMessage("통합 플러그인의 설치가 필요합니다.", "", level=Qgis.Info, duration=2)
                pass
            return

        # 파일 읽어서 확인
        path = "{0}\\Inavi\\_Login".format(os.getenv('APPDATA'))
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except :
            print("Error")
        os.chmod(path, 777)
        filepath_login = path + "\\" + "iLogin.JSON"
        sha1password = hashlib.sha1("inavi9610".encode("utf-8")).hexdigest()
        f = open(filepath_login, 'r')
        data = f.read()
        f.close()
        decrypt_string = decrypt_Data(data, str(sha1password[0:32]).encode())
        decrypt_tuple = convertStrToTuple(decrypt_string)
        self.run()

    def run(self):
        if self.first_start:
            self.first_start = False
        self.dlg = MoctCheckerDialog()
        self.dlg.show(self.iface)
        result = self.dlg.exec_()

        del self.dlg.mlogger
        del self.dlg
        if result:
            pass
