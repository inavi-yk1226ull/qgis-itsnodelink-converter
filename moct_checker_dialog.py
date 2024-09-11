# -*- coding: utf-8 -*-

import os
import logging
from qgis.core import QgsWkbTypes, QgsProject, Qgis, QgsApplication
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from qgis.core import QgsTask, QgsMessageLog, Qgis, QgsApplication
from .update_id import UpdateId
from .db_post import PG_DB_NAME, PG_EPSG, PG_GEOM, PG_HOST, PG_PASSWORD, PG_PORT, PG_USER, DbPost

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'moct_checker_dialog_base.ui'))


class MoctCheckerDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(MoctCheckerDialog, self).__init__(parent)
        self.tm = QgsApplication.taskManager()

        # 초기화
        self.islive = True
        self.post_db=DbPost(True)
        
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
        self.setupUi(self)

    def logging_info(self, log_name, msg):
        QgsMessageLog.logMessage(msg, log_name, Qgis.Success)

    def query_check_moctdata(self, table, code):
        sqlstr_node = "select * from moct.fn_node_insert_error('{0}')"
        sqlstr_link = "select * from moct.fn_link_insert_error('{0}')"

        if table == "link":
            sqlstr = sqlstr_link.format(code)
        elif table == "node":
            sqlstr = sqlstr_node.format(code)
        else:
            self.logging_info("Checker", "return")
            return

        self.logging_info("Checker", "검수 시작: {0}".format(table))
        self.post_db.execute(sqlstr)
        self.logging_info("Checker", "검수 종료")

    def ButtonCheckListener(self, _trash=None):
        qbox = QMessageBox()
        qbox.setWindowModality(True)
        qbox.setWindowTitle('무결성 검증')
        qbox.setText('무결성 검증 과정을 진행합니다.\r\n데이터를 수정할 경우 데이터에 영향을 줄 수 있으니,\r\n모든 작업이 끝난 뒤 실행하는 것을 권장합니다.\r\n실행합니까?')
        qbox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        reply = qbox.exec_()
        if reply == QMessageBox.Yes:
            self.button_enabled(False)
            check_data_task = QgsTask.fromFunction('Checker', self.CheckData, on_finished=self.CheckDataEnd)
            QgsApplication.taskManager().addTask(check_data_task)
            

    def CheckData(self, task):
        # 검증
        workstate_code = ''
        if self.rbtn_forall.isChecked():
            workstate_code = "a"
        elif self.rbtn_fornew.isChecked():
            workstate_code = "n"
        else:
            workstate_code = "b"

        # DB 연결 구문
        # 검출 DB 연결 후 T/F 반환
        self.logging_info("Checker", "DB 연결")

        if self.post_db.connect == 1:
            # 연결 실패
            return
        # 검증
        self.query_check_moctdata("link", workstate_code)
        self.query_check_moctdata("node", workstate_code)
        return True

    def button_enabled(self, enabled):
        '''기능 시작/종료 시 버튼 disable '''
        self.btn_check.setEnabled(enabled)
        self.btn_load_link.setEnabled(enabled)
        self.btn_load_node.setEnabled(enabled)
        self.btn_setid.setEnabled(enabled)
        self.btn_removefeature.setEnabled(enabled)
        self.btn_truncatetable.setEnabled(enabled)

    def ButtonLoadLinkLayerListener(self, _trash=None):
        # 검증 결과 호출 구문_링크
        self.post_db.load_pg_layer(PG_HOST, PG_PORT, PG_DB_NAME, PG_USER, PG_PASSWORD,
                                    QgsWkbTypes.MultiLineString,
                                    PG_EPSG, 'moct', self.link_layer_dbname, PG_GEOM, '', self.link_layer_name)
        self.link_layer = QgsProject.instance().mapLayersByName(self.link_layer_name)[0]

    def ButtonLoadNodeLayerListener(self, _trash=None):
        # 검증 결과 호출 구문_노드
        self.post_db.load_pg_layer(PG_HOST, PG_PORT, PG_DB_NAME, PG_USER, PG_PASSWORD,
                                       QgsWkbTypes.Point,
                                       PG_EPSG, 'moct', self.node_layer_dbname, PG_GEOM, '', self.node_layer_name)
        self.node_layer = QgsProject.instance().mapLayersByName(self.node_layer_name)[0]

    def ButtonRemoveFeatureListener(self, _trash=None):
        # 선택 피쳐 삭제
        features = None
        active_layer = self.iface.activeLayer()
        if active_layer.name() == self.node_layer_name:
            features = active_layer.selectedFeatures()
        elif active_layer.name() == self.link_layer_name:
            features = active_layer.selectedFeatures()
        else:
            QMessageBox.information(self.iface.mainWindow(), '오류', '_error 레이어를 선택해주세요.')

        if features is None:
            self.iface.messageBar().pushMessage('피쳐 선택', '선택된 피쳐가 없습니다.', level=Qgis.Warning)
            return
        else:
            pr = active_layer.dataProvider()
            for f in features:
                pr.deleteFeatures([f.id()])
        active_layer.triggerRepaint()

    def ButtonTruncateTableListener(self, _trash=None):
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

    def show(self, iface):
        self.iface = iface
        super(MoctCheckerDialog, self).show()

    def ButtonSetIdListener(self, _trash=None):
        qbox = QMessageBox()
        qbox.setWindowModality(True)
        qbox.setWindowTitle('ID 부여 진행')
        qbox.setText('ID 부여 과정을 진행합니다.\r\n데이터를 수정할 경우 데이터에 영향을 줄 수 있으니,\r\n모든 작업이 끝난 뒤 실행하는 것을 권장합니다.\r\n실행합니까?')
        qbox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        reply = qbox.exec_()
        if reply == QMessageBox.Yes:
            self.button_enabled(False)
            task = UpdateId('UpdateId', self.islive)
            task.end_signal.connect(self.SetIdEnd)
            QgsApplication.taskManager().addTask(task)

    def SetIdEnd(self, result):
        QMessageBox.information(self.iface.mainWindow(), '완료', '작업이 종료되었습니다.')
        self.button_enabled(True)

    def CheckDataEnd(self, exception, result=None):
        QMessageBox.information(self.iface.mainWindow(), '완료', '작업이 종료되었습니다.')
        self.button_enabled(True)
