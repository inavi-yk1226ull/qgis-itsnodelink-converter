# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .resources import *
from .moct_checker_dialog import MoctCheckerDialog
from .login.login_dialog import LoginDialog
import os.path

isLocal = True


class MoctChecker:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = self.tr(u'&Moct Checker')
        self.first_start = None
        self.is_login = False

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        return QCoreApplication.translate('MoctChecker', message)

    def add_action(
            self, icon_path, text, callback, enabled_flag=True,
            add_to_menu=True, add_to_toolbar=True, status_tip=None,
            whats_this=None, parent=None):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_toolbar:
            self.iface.addToolBarIcon(action)
        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)
        self.actions.append(action)

        return action

    def initGui(self):
        icon_path = ':/plugins/moct_checker/icon.png'
        self.add_action(icon_path, text='Invai Moct Checker', callback=self.run, parent=self.iface.mainWindow())
        self.first_start = True

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu('Moct Checker', action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        if not isLocal:
            if not self.is_login:
                ld = LoginDialog()
                result = ld.exec_()
                if result == 1:
                    self.is_login = True
                    pass
                else:
                    return
                pass
            pass
        else:
            pass

        if self.first_start:
            self.first_start = False
        self.dlg = MoctCheckerDialog()
        self.dlg.show(self.iface)
        result = self.dlg.exec_()

        del self.dlg.mlogger
        del self.dlg
        if result:
            pass
