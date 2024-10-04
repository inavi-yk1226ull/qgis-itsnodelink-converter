# -*- coding: utf-8 -*-
import os.path
import os
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QToolBar
from qgis.core import Qgis

from .moct_checker_dialog import MoctCheckerDialog
from .resources import *


isLocal = False


class iQgisNodeLinkConverter:

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
        self.first_start = True
        self.toolbar = self.iface.mainWindow().findChild(QToolBar, u'아이나비 툴바')
        if not self.toolbar:
            self.toolbar = self.iface.addToolBar(u'아이나비 툴바')
            self.toolbar.setObjectName(u'아이나비 툴바')
        self.toolbar.addAction(self.main_action)

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu('Moct Checker', action)
            self.iface.removeToolBarIcon(action)

    def run_login(self, _trash=None):
        try:
            import iGlobal

            self.chk_user_permission = None
            self.user_name = None
            if hasattr(iGlobal, "user_permission"):
                self.chk_user_permission = iGlobal.user_permission
                self.user_name = iGlobal.user_name
            else:
                self.chk_user_permission = None
                self.user_name = None

            if self.chk_user_permission == None:
                _path = os.path.abspath(os.path.dirname(__file__))
                path = os.path.join(_path, "../iQ_Admin")
                if os.path.isdir(path):
                    self.iface.messageBar().pushMessage("로그인이 필요합니다.", "", level=Qgis.Info, duration=2)
                else:
                    self.iface.messageBar().pushMessage(
                        "통합 플러그인의 설치가 필요합니다.(1.7.0 이상)", "", level=Qgis.Info, duration=2
                    )
                return
            else:
                ischecked = False
                for permission in self.chk_user_permission:
                    if "ITS_NODELINK_VIEW" in permission:
                        ischecked = True

                if ischecked is False:
                    self.iface.messageBar().pushMessage(
                        "플러그인 사용권한이 없습니다. 관리자에게 문의 바랍니다.", "", level=Qgis.Info, duration=2
                    )
                    return

        except Exception as e:
            self.iface.messageBar().pushMessage(
                "관리자에게 문의 바랍니다. : " + str(e), "", level=Qgis.Info, duration=2
            )
            return

        self.run()

    def run(self):
        if self.first_start:
            self.first_start = False
            self.dlg = MoctCheckerDialog()
            self.dlg.show(self.iface)
            result = self.dlg.exec_()

            del self.dlg
            self.first_start = True
