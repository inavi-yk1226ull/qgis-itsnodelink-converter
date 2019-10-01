# -*- coding: utf-8 -*-

# import base module
import os
import logging
from concurrent.futures import ThreadPoolExecutor

# import qgis core
from qgis.core import Qgis, QgsTask, QgsApplication

# import qgis pyqt
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

# import pyqt5
from PyQt5.QtWidgets import QMessageBox

# import make by me
from .db_post import DbPost

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'moct_checker_dialog_base.ui'))


class MoctCheckerDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(MoctCheckerDialog, self).__init__(parent)

        # 초기화
        self.post_db = None

        # 로그
        absFilePath = os.path.abspath(__file__)
        os.chdir(os.path.dirname(absFilePath))
        self.logpath = os.path.join(os.getcwd(), "logging.log")
        self.mlogger = logging.getLogger("time")
        self.mlogger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler = logging.FileHandler(self.logpath)
        file_handler.setFormatter(formatter)
        self.mlogger.addHandler(file_handler)
        self.setupUi(self)
        pass

    def logging_info(self, log_name, msg):
        self.mlogger.info(msg)
        pass

    def query_check_moctdata(self, table):
        self.logging_info("checker", "테이블: {}".format(table))
        sqlstr_link = "select * from moct.err_check_link()"
        sqlstr_node = "select * from moct.err_check_node()"

        if table == "link":
            sqlstr = sqlstr_link
            pass
        elif table == "node":
            sqlstr = sqlstr_node
            pass
        else:
            self.logging_info("checker", "return")
            return

        self.logging_info("checker", "sqlstr: {}".format(sqlstr))

        self.logging_info("checker", "검수 시작")
        self.post_db.execute(sqlstr)
        self.logging_info("checker", "검수 종료")

    def ButtonCheckListener(self):
        # DB 연결 구문
        # 검출 DB 연결 후 T/F 반환
        print("연결 버튼")
        self.logging_info("info", "연결 구문 시작")

        self.post_db = DbPost()
        if self.post_db.connect == 1:
            # 연결 실패
            pass
        pass

        # 스레드 처리 필요
        # 데이터 처리 시간 동안 별도 안내 필요
        # 결과 적재
        # 검증 쿼리 실행 구문
        QMessageBox.information(self.iface.mainWindow(), '시작', '검수 과정을 시작합니다.')

        # self.button_enabled(False)

        li = ["link", "node"]
        task_link = QgsTask.fromFunction("link_check", self.query_check_moctdata, table="link")
        self.logging_info("debug", "create task link")
        task_node = QgsTask.fromFunction("node_check", self.query_check_moctdata, table="node")
        self.logging_info("debug", "create task node")

        QgsApplication.taskManager().addTask(task_link)
        self.logging_info("debug", "add task link")
        QgsApplication.taskManager().addTask(task_node)
        self.logging_info("debug", "add task node")
        # self.button_enabled(True)

        pass

    def completed(self):
        print("call onfinished")
        self.button_enabled(True)
        QMessageBox.information(self.iface.mainWindow(), '시작', '검수 과정이 종료되었습니다.')
        pass

    def button_enabled(self, enabled):
        self.btn_check.setEnabled(enabled)
        self.btn_load_link.setEnabled(enabled)
        self.btn_load_node.setEnabled(enabled)
        pass

    def ButtonLoadLayerListener(self):
        # 검증 결과 호출 구문
        pass

    def show(self, iface):
        self.iface = iface
        super(MoctCheckerDialog, self).show()
