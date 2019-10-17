# -*- coding: utf-8 -*-

# import base module
import os
import logging

# import qgis core
from qgis.core import QgsWkbTypes, QgsProject, Qgis

# import qgis pyqt
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

# import pyqt5
from PyQt5.QtWidgets import QMessageBox

# import make by me
from .update_id import UpdateId
from .db_post import DbPost
# from .test import test_thread

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'moct_checker_dialog_base.ui'))


class MoctCheckerDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(MoctCheckerDialog, self).__init__(parent)

        # 초기화
        self.post_db = DbPost()
        self.islive = None

        self.link_layer = None
        self.link_layer_name = 'Inavi_link_error'
        self.link_layer_dbname = 'moct_link_err'
        self.node_layer = None
        self.node_layer_name = 'Inavi_node_error'
        self.node_layer_dbname = 'moct_node_err'

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

    def query_check_moctdata(self, table, code):
        self.logging_info("checker", "테이블: {}".format(table))
        sqlstr_node = "select * from moct.fn_node_insert_error('{0}')"
        sqlstr_link = "select * from moct.fn_link_insert_error('{0}')"

        if table == "link":
            sqlstr = sqlstr_link.format(code)
            pass
        elif table == "node":
            sqlstr = sqlstr_node.format(code)
            pass
        else:
            self.logging_info("checker", "return")
            return

        self.logging_info("checker", "검수 시작: {0}".format(sqlstr))
        self.post_db.execute(sqlstr)
        self.logging_info("checker", "검수 종료")

    def ButtonCheckListener(self):
        # 체크박스 버튼 확인
        workstate_code = ''
        if self.rbtn_forall.isChecked():
            workstate_code = "a"
        elif self.rbtn_fornew.isChecked():
            workstate_code = "n"
        else:
            workstate_code = "b"
            pass

        # DB 연결 구문
        # 검출 DB 연결 후 T/F 반환
        self.logging_info("info", "연결 구문 시작")

        if self.post_db.connect == 1:
            # 연결 실패
            return
        pass

        # 스레드 처리 필요
        # 데이터 처리 시간 동안 별도 안내 필요
        # 결과 적재
        # 검증 쿼리 실행 구문
        QMessageBox.information(self.iface.mainWindow(), '시작', '검수 과정을 시작합니다.')

        self.button_enabled(False)

        # 검증
        self.query_check_moctdata("link", workstate_code)
        self.query_check_moctdata("node", workstate_code)

        self.completed()
        pass

    def completed(self):
        self.button_enabled(True)
        QMessageBox.information(self.iface.mainWindow(), '시작', '검수 과정이 종료되었습니다.')
        pass

    def button_enabled(self, enabled):
        self.btn_check.setEnabled(enabled)
        self.btn_load_link.setEnabled(enabled)
        self.btn_load_node.setEnabled(enabled)
        pass

    def ButtonLoadLinkLayerListener(self):
        # 검증 결과  호출 구문_링크
        if self.link_layer is not None:
            pass
        else:
            self.iface.messageBar().pushMessage('Test/Live 선택', '실행 버전을 선택해 주세요.', level=Qgis.Warning)
            pass

        if self.islive is True:
            self.post_db.load_pg_layer('61.33.249.242', '5432', 'kslink', 'kslink_agent', 'ag9TmuS875', QgsWkbTypes.MultiLineString,
                                       '5186', 'moct', self.link_layer_dbname, '_geom', '', self.link_layer_name)
            pass
        elif self.islive is False:
            self.post_db.load_pg_layer('61.33.249.241', '5432', 'testdb', 'yk1226ull', 'inavi9610', QgsWkbTypes.MultiLineString,
                                       '5186', 'moct', self.link_layer_dbname, '_geom', '', self.link_layer_name)
            pass

        self.link_layer = QgsProject.instance().mapLayersByName(self.link_layer_name)[0]

    def ButtonLoadNodeLayerListener(self):
        # 검증 결과 호출 구문_노드
        if self.node_layer is not None:
            pass
        else:
            self.iface.messageBar().pushMessage('Test/Live 선택', '실행 버전을 선택해 주세요.', level=Qgis.Warning)
            pass

        if self.islive is True:
            self.post_db.load_pg_layer('61.33.249.242', '5432', 'kslink', 'kslink_agent', 'ag9TmuS875', QgsWkbTypes.Point,
                                       '5186', 'moct', self.node_layer_dbname, '_geom', '', self.node_layer_name)
            pass
        elif self.islive is False:
            self.post_db.load_pg_layer('61.33.249.241', '5432', 'testdb', 'yk1226ull', 'inavi9610', QgsWkbTypes.Point,
                                       '5186', 'moct', self.node_layer_dbname, '_geom', '', self.node_layer_name)
            pass

        self.node_layer = QgsProject.instance().mapLayersByName(self.node_layer_name)[0]

    def ButtonRemoveFeatureListener(self):
        # 선택 피쳐 삭제
        features = None
        active_layer = self.iface.activeLayer()
        if active_layer.name() == self.node_layer_name:
            features = active_layer.selectedFeatures()
            pass
        elif active_layer.name() == self.link_layer_name:
            features = active_layer.selectedFeatures()
        else:
            QMessageBox.information(self.iface.mainWindow(), '오류', '_error 레이어를 선택해주세요.')
        pass

        if features is None:
            self.iface.messageBar().pushMessage('피쳐 선택', '선택된 피쳐가 없습니다.', level=Qgis.Warning)
            return
        else:
            pr = active_layer.dataProvider()
            pr.deleteFeatures(features.id())
            pass
        pass

    def ButtonTruncateTableListener(self):
        qbox = QMessageBox()
        qbox.setWindowModality(True)
        qbox.setWindowTitle('오류 테이블 초기화')
        qbox.setText('오류 테이블을 모두 초기화 합니까?')
        qbox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        reply = qbox.exec_()
        if reply == QMessageBox.Yes:
            self.post_db.execute('Truncate moct.moct_link_err;')
            self.post_db.execute('Truncate moct.moct_node_err;')
            QMessageBox.information(self.iface.mainWindow(), '완료', '테이블 초기화 종료.')
        else:
            pass
        pass

    def tmp_ButtonSetIdListener(self):
        tc = UpdateId(self.mlogger)
        tc.main_process()
        pass

    def RbtnSetVersionListener(self):
        if self.rbtn_istest.isChecked():
            self.islive = False
            pass
        elif self.rbtn_islive.isChecked():
            self.islive = True
            pass
        pass

    def show(self, iface):
        self.iface = iface
        super(MoctCheckerDialog, self).show()

    def ButtonSetIdListener(self):
        print("ButtonSetIdListener")
        task2 = QgsTask.fromFunction('waste cpu 2', run1, on_finished=completed, wait_time=5)
        QgsApplication.taskManager().addTask(task2)
        pass

from time import sleep
import random

from qgis.core import QgsMessageLog, Qgis, QgsTask, QgsApplication

MESSAGE_CATEGORY = 'My tasks from a function'


def run(task, wait_time):
    # QgsMessageLog.logMessage('Started task {}'.format(task.description()), MESSAGE_CATEGORY, Qgis.Info)

    wait_time = wait_time / 100

    total = 0
    iterations = 0
    for i in range(101):
        # QgsMessageLog.logMessage('Started task2 {}'.format(i), MESSAGE_CATEGORY, Qgis.Info)
        # sleep(wait_time)
        # use task.setProgress to report progress
        task.setProgress(i)
        total += random.randint(0, 100)
        iterations += 1
        # check task.isCanceled() to handle cancellation
        if task.isCanceled():
            stopped(task)
            return None
        # raise exceptions to abort task
        # if random.randint(0, 500) == 42:
        #     raise Exception('bad value!')
    return {
        'total': total, 'iterations': iterations, 'task': task.description()
    }


def stopped(task):
    QgsMessageLog.logMessage('Task "{name}" was cancelled'.format(name=task.description()), MESSAGE_CATEGORY, Qgis.Info)


def completed(exception, result=None):
    QgsMessageLog.logMessage('end qgstask' ,MESSAGE_CATEGORY, Qgis.Info)
    if exception is None:
        if result is None:
            # QgsMessageLog.logMessage(
            #     'Completed with no exception and no result ' \
            #     '(probably the task was manually canceled by the user)',
            #     MESSAGE_CATEGORY, Qgis.Warning)
            pass
        else:
            # QgsMessageLog.logMessage(
            #     'Task {name} completed'.format(
            #         name=result['task'], total=result['total'], iterations=result['iterations']),
            #     MESSAGE_CATEGORY, Qgis.Info)
            pass
    else:
        # QgsMessageLog.logMessage("Exception: {}".format(exception),
        #                          MESSAGE_CATEGORY, Qgis.Critical)
        raise exception


def run1(task, wait_time):
    for i in range(101):
        task.setProgress(i)
        sleep(wait_time)
        # for _ in range(1000000000):
        #     pass
        pass
    pass


# def test_thread():
#     print('start test_thread')
#     # a bunch of tasks
#     task2 = QgsTask.fromFunction('waste cpu 2', run1, on_finished=completed, wait_time=5)
#     QgsApplication.taskManager().addTask(task2)
#
#     # task1 = QgsTask.fromFunction('waste cpu 1', run, on_finished=completed, wait_time=4)
#     # QgsApplication.taskManager().addTask(task1)


