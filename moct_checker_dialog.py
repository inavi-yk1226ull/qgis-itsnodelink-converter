# -*- coding: utf-8 -*-

# import base module
import os
import logging

# import qgis core
from qgis.core import QgsWkbTypes, QgsProject, Qgis, QgsApplication

# import qgis pyqt
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

# import pyqt5
from PyQt5.QtWidgets import QMessageBox

# import make by me
from .update_id import UpdateId, task_create_and_execute
from .db_post import DbPost

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'moct_checker_dialog_base.ui'))


class MoctCheckerDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(MoctCheckerDialog, self).__init__(parent)
        self.tm = QgsApplication.taskManager()

        # 초기화
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
        QMessageBox.information(self.iface.mainWindow(), '완료', '작업이 종료되었습니다.')
        pass

    def button_enabled(self, enabled):
        self.btn_check.setEnabled(enabled)
        self.btn_load_link.setEnabled(enabled)
        self.btn_load_node.setEnabled(enabled)
        pass

    def ButtonLoadLinkLayerListener(self):
        # 검증 결과  호출 구문_링크
        if self.islive is not None:
            pass
        else:
            self.iface.messageBar().pushMessage('Test/Live 선택', '실행 버전을 선택해 주세요.', level=Qgis.Warning)
            return

        if self.islive is True:
            self.post_db.load_pg_layer('61.33.249.242', '5432', 'kslink', 'kslink_agent', 'ag9TmuS875',
                                       QgsWkbTypes.MultiLineString,
                                       '5186', 'moct', self.link_layer_dbname, '_geom', '', self.link_layer_name)
            pass
        elif self.islive is False:
            self.post_db.load_pg_layer('61.33.249.241', '5432', 'testdb', 'yk1226ull', 'inavi9610',
                                       QgsWkbTypes.MultiLineString,
                                       '5186', 'moct', self.link_layer_dbname, '_geom', '', self.link_layer_name)
            pass
        self.link_layer = QgsProject.instance().mapLayersByName(self.link_layer_name)[0]

    def ButtonLoadNodeLayerListener(self):
        # 검증 결과 호출 구문_노드
        if self.islive is not None:
            pass
        else:
            self.iface.messageBar().pushMessage('Test/Live 선택', '실행 버전을 선택해 주세요.', level=Qgis.Warning)
            return

        if self.islive is True:
            self.post_db.load_pg_layer('61.33.249.242', '5432', 'kslink', 'kslink_agent', 'ag9TmuS875',
                                       QgsWkbTypes.Point,
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

    def RbtnSetVersionListener(self):
        if self.rbtn_istest.isChecked():
            print('is test')
            self.islive = False
            self.post_db = DbPost(self.islive)
            pass
        elif self.rbtn_islive.isChecked():
            print('is live')
            self.islive = True
            self.post_db = DbPost(self.islive)
            pass
        pass

    def show(self, iface):
        self.iface = iface
        super(MoctCheckerDialog, self).show()

    def ButtonSetIdListener(self):
        # task_create_and_execute(self.mlogger, self.islive)
        print('1')
        task = UpdateId('UpdateId', self.mlogger, self.islive)
        task.run()
        print('2')
        # self.tm.addTask(task)
        # QgsApplication.taskManager().addTask(task)
        print('3')
        pass
