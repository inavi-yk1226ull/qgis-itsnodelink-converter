from PyQt5.QtCore import QThread
from qgis.core import QgsTask, QgsMessageLog, Qgis, QgsApplication

from .stopwatch import Stopwatch
from .db_post import DbPost
import logging
import os

MESSAGE_CATEGORY = 'UpdateId'


class UpdateId(QgsTask):
    def __init__(self, description, _logger, islive):
        super().__init__(description, QgsTask.CanCancel)
        self.description = description
        self.islive = islive
        self.post_db = DbPost(self.islive)
        # 로그
        absFilePath = os.path.abspath(__file__)
        os.chdir(os.path.dirname(absFilePath))
        self.logpath = os.path.join(os.getcwd(), "logging.log")
        self.mlogger = _logger

        # 링크의 권역 별 최대 일련번호 적재
        self._dict = {}
        self.logging_info("UpdateId init Create")
        pass

    def logging_info(self, msg):
        self.mlogger = logging.getLogger("time")
        self.mlogger.info(msg)
        pass

    # 노드 권역 반복작업
    def node_repeat_adm(self):
        sw = Stopwatch()
        sqlstr = "select region_cd from moct.adm_boundary"
        rows = self.post_db.execute_query(sqlstr)
        self.logging_info("  region select: {0}".format(sw.CheckPoint()))
        for row in rows:
            region_cd = row[0]
            serial_num = self.get_max_num(region_cd)
            # self.logging_info("  region_{0} get_max_num: {1}".format(region_cd, sw.CheckPoint()))
            print("region_cd: {0}, num: {1}".format(region_cd, serial_num))
            self.node_update_id(region_cd, int(serial_num) + 1, sw)
            self.logging_info("  region_{0} 처리 완료: {1}".format(region_cd, sw.CheckPoint()))
            pass

        # 노드 id null인 항목 업데이트
        sqlstr = " select gid from moct.moct_node_data where node_id is null or node_id = '' "
        rows = self.post_db.execute_query(sqlstr)

        for row in rows:
            _gid = row[0]
            sqlstr = """
            SELECT ab.region_cd 
            FROM moct.moct_node_data as nd, moct.adm_boundary as ab  
            WHERE nd.gid={0} AND ST_DWithin(nd._geom, ab._geom, 10000)  
            ORDER BY ST_Distance(nd._geom, ab._geom) limit 1;
            """.format(_gid)

            _rows = self.post_db.execute_query(sqlstr)
            _region_cd = _rows[0][0]

            sqlstr = """ UPDATE moct.moct_node_data
                                SET node_id = %s
                                WHERE gid = %s"""

            serial_num = self.get_max_num(_region_cd)
            serial_num = int(serial_num) + 1
            node_id = str(serial_num) + '00'

            self.post_db.execute_with_args(sqlstr, (node_id, _gid))

            pass

        self.logging_info("  if node_id is null 처리 완료: {0}".format(sw.CheckPoint()))
        pass

    # 권역 최대 일련번호 확인
    def get_max_num(self, _int):
        # 191022 where절 추가
        # WHERE substring(area_serial FROM 4 FOR 1) != '9'
        # 사유: 엠큐닉 입력 데이터의 id 부여가 9만번대로 이루어져 있음, 이를 제외함
        sqlstr = "select * from moct.fn_select_max_serial_num_node('{0}') WHERE substring(area_serial FROM 4 FOR 1) != '9'".format(
            _int)
        rows = self.post_db.execute_query(sqlstr)
        max_num = str(_int) + '00000'
        try:
            max_num = rows[0][0]
        except:
            max_num = str(_int) + '00000'

        return max_num

    # 권역 내 노드의 일련번호 & id 부여
    def node_update_id(self, current_adm, serial_num, sw):
        sqlstr = "select * from moct.fn_select_node_if_nodeid_is_null('{0}')".format(current_adm)
        cursor = self.post_db.execute_query_cursor(sqlstr)

        rows = cursor.fetchall()
        # get id field
        gid_field = [desc[0] for desc in cursor.description].index("gid")
        tmp_field = [desc[0] for desc in cursor.description].index("tmpid")

        # self.logging_info("    대상 노드 select 완료: {0}".format(sw.CheckPoint()))

        for row in rows:
            sqlstr = """ UPDATE moct.moct_node_data
                                SET node_id = %s
                                WHERE gid = %s"""
            node_id = str(serial_num) + '00'
            serial_num = serial_num + 1
            gid = row[gid_field]
            self.post_db.execute_with_args(sqlstr, (node_id, gid))

            # self.logging_info("    node id update complete: {0}".format(sw.CheckPoint()))

            # 연결된 링크 업데이트 _f
            tmpid = row[tmp_field]
            sqlstr = '''
            Update moct.moct_link_data
            SET f_node = %s
            WHERE sosfnodeid = %s
            '''
            self.post_db.execute_with_args(sqlstr, (node_id, tmpid))

            # self.logging_info("    F link id update complete: {0}".format(sw.CheckPoint()))

            # 연결된 링크 업데이트 _t
            tmpid = row[tmp_field]
            sqlstr = '''
            Update moct.moct_link_data
            SET t_node = %s
            WHERE sostnodeid = %s
            '''
            self.post_db.execute_with_args(sqlstr, (node_id, tmpid))

            # self.logging_info("    T link id update complete: {0}".format(sw.CheckPoint()))

            pass
        cursor.close()

    # ----------------------------------------------------------------------------------------------------------------------
    # 링크 # 못쓴다.
    # def link_repeat_adm(self, max_adm):
    #     for current_adm in range(1, max_adm):
    #         sqlstr = "select region_cd from moct.adm_boundary where gid = '{0}'".format(current_adm)
    #         rows = self.post_db.execute_query(sqlstr)
    #         region_cd = rows[0][0]
    #         serial_num = self.link_get_max_num(region_cd)
    #         print("region_cd: {0}, num: {1}".format(region_cd, serial_num))
    #         self.link_update_id(current_adm, int(serial_num) + 1)
    #         if current_adm == 30:
    #             break
    #         pass
    #     pass
    # 일련번호 & id 부여
    # def link_update_id(self, current_adm, serial_num):
    #     sqlstr = "select * from moct.fn_select_link_if_linkid_is_null('{0}')".format(current_adm)
    #     cursor = self.post_db.execute_query_cursor(sqlstr)
    #
    #     rows = cursor.fetchall()
    #     # get id field
    #     gid_field = [desc[0] for desc in cursor.description].index("gid")
    #     fnode_field = [desc[0] for desc in cursor.description].index("f_node")
    #     tnode_field = [desc[0] for desc in cursor.description].index("t_node")
    #
    #     for row in rows:
    #         sqlstr = """ UPDATE moct.moct_link_data
    #                     SET link_id = %s
    #                     WHERE gid = %s"""
    #         link_id = serial_num + '00'
    #         serial_num = serial_num + 1
    #         gid = row[gid_field]
    #         self.post_db.execute_with_args(sqlstr, (link_id, gid))
    #
    #         # 페어 확인 후 update
    #         link_id = serial_num + '00'
    #         serial_num = serial_num + 1
    #
    #         fnode = row[fnode_field]
    #         tnode = row[tnode_field]
    #
    #         sqlstr = """ UPDATE moct.moct_link_data
    #                     SET link_id = %s
    #                     WHERE f_node = %s AND t_node = %s """
    #
    #         self.post_db.execute_with_args(sqlstr, (link_id, tnode, fnode))
    #         pass
    #     cursor.close()
    # 최대 지역번호 + 일련번호 확인
    # return : 지역번호 + 일련번호 최대값, +1을 해야 신규 입력할 id값이 나온다
    # def link_get_max_num(self, current_adm):
    #     sqlstr = "select * from moct.fn_select_max_serial_num('{0}')".format(current_adm)
    #     rows = self.post_db.execute_query(sqlstr)
    #     return rows[0][0]

    # 권역 별 최대 일련번호 확인
    def get_region_serial_code_all(self):
        # 191022 where 절 and 조건 추가
        # 각 3자리로 group
        # 나머지 5자리로 max값 확인
        #
        sqlstr = '''
        select substring(link_id from 1 for 3)
               , max(substring(link_id from 4 for 5)) as serial
          from moct.moct_link_data 
         where substring(link_id from 4 for 1) <> '9'
         group by substring(link_id from 1 for 3)
        '''
        cursor = self.post_db.execute_query_cursor(sqlstr)
        rows = cursor.fetchall()

        _dict = {}
        for row in rows:
            if row[0] is None or len(row[0]) != 3:
                continue
            _dict[int(row[0])] = int(row[1])
            pass
        cursor.close()
        return _dict

    # 링크 별 id 업데이트 및 쌍 링크 업데이트
    def update_link_id(self, is_bigger_t):
        sw = Stopwatch()
        self.logging_info("    is_bigger_t: {0}, {1}".format(is_bigger_t, sw.CheckPoint()))
        sqlstr = ''
        if is_bigger_t:
            sqlstr = "select * from moct.moct_link_data where not (f_node is null or f_node = '') and not (t_node is null or t_node = '') and CAST(f_node AS BIGINT) > CAST(t_node AS BIGINT) AND (link_id is null or link_id = '') AND is_delete IS NOT True"
            pass
        else:
            sqlstr = "select * from moct.moct_link_data where not (f_node is null or f_node = '') and not (t_node is null or t_node = '') and CAST(t_node AS BIGINT) > CAST(f_node AS BIGINT) AND (link_id is null or link_id = '') AND is_delete IS NOT True"
            pass
        print(sqlstr)
        cursor = self.post_db.execute_query_cursor(sqlstr)

        gid_field = [desc[0] for desc in cursor.description].index("gid")
        fnode_field = [desc[0] for desc in cursor.description].index("f_node")
        tnode_field = [desc[0] for desc in cursor.description].index("t_node")
        rank_field = [desc[0] for desc in cursor.description].index("road_rank")
        type_field = [desc[0] for desc in cursor.description].index("road_type")


        # 재생성
        post_db_2 = DbPost(self.islive)
        post_db_2.connect()

        for row in cursor:
            _gid = row[gid_field]
            _rank = row[rank_field]
            _type = row[type_field]
            _fnode = row[fnode_field]
            _tnode = row[tnode_field]

            curs = post_db_2.execute_query_cursor("""
                select region_cd, st_length(
                    st_intersection(
                        _geom, (select _geom from moct.moct_link_data where gid = '{0}')
                    )
                ) from moct.adm_boundary as ab 
                    where ST_Intersects(
                        ab._geom, (select _geom from moct.moct_link_data where gid = '{0}')
                    )
                order by st_length desc
            """.format(_gid))

            try:
                _region_cd = curs.fetchall()[0][0]
            except:
                self.logging_info("    get link's region error gid is {0}, {1}".format(_gid, row))
                continue

            curs.close()

            # self.logging_info("    get link's region: {0}".format(sw.CheckPoint()))

            # 메인
            # _max_num = int(self.link_get_max_num(_region_cd)) + 1
            # _max_num = int(_region_cd + str(self._dict[int(_region_cd)] + 1))

            _max_num = _region_cd + str(self._dict.get(int(_region_cd), 0) + 1).zfill(5)

            # self.logging_info("    calc max_num: {0}, {1}".format(sw.CheckPoint(), _max_num))

            _link_id = _max_num + '00'
            _sqlstr = """ UPDATE moct.moct_link_data
                        SET link_id = %s
                        WHERE gid = %s"""
            self.post_db.execute_with_args(_sqlstr, (_link_id, _gid))
            self._dict[int(_region_cd)] = self._dict.get(int(_region_cd), 0) + 1

            # self.logging_info("    link update: {0}".format(sw.CheckPoint()))
            # print("    link update: {0}".format(_gid))

            # 쌍
            _max_num = _region_cd + str(self._dict.get(int(_region_cd), 0) + 1).zfill(5)
            _link_id = _max_num + '00'
            sqlstr = """ UPDATE moct.moct_link_data
                        SET link_id = %s
                        WHERE f_node = %s AND t_node = %s AND road_rank = %s AND road_type = %s is_delete is not true"""
            self.post_db.execute_with_args(sqlstr, (_link_id, _tnode, _fnode, _rank, _type))
            self._dict[int(_region_cd)] = self._dict.get(int(_region_cd), 0) + 1

            self.logging_info("    pair link update: {0}".format(sw.CheckPoint()))

            pass
        cursor.close()
        pass

    def run(self):
        # 커넥션 get
        self.logging_info("start run")
        logsw = Stopwatch()
        self.logging_info("DB 연결 시도: {0}".format(logsw.CheckPoint()))
        self.post_db.connect()
        self.logging_info("DB 연결: {0}".format(logsw.CheckPoint()))
        self.node_repeat_adm()
        self.logging_info("노드 반복 종료: {0}".format(logsw.CheckPoint()))

        # 권역 번호를 가져와서 리스트 저장한다.
        _dict = self.get_region_serial_code_all()
        self._dict = _dict
        self.update_link_id(True)
        self.logging_info("링크T 반복 종료: {0}".format(logsw.CheckPoint()))
        self.update_link_id(False)
        self.logging_info("링크F 반복 종료: {0}".format(logsw.CheckPoint()))
        self.logging_info("ID 부여 작업 종료: {0}".format(logsw.GetTotal()))
        return True

    def finished(self, result):
        if result:
            QgsMessageLog.logMessage(f'Task UpdateId completed', MESSAGE_CATEGORY, Qgis.Success)
        else:
            QgsMessageLog.logMessage(f'Task UpdateId failed', MESSAGE_CATEGORY, Qgis.Critical)

    def cancel(self):
        QgsMessageLog.logMessage(f'Task UpdateId was canceled', MESSAGE_CATEGORY, Qgis.Info)
        super().cancel()
    pass


def task_create_and_execute(logger, islive):
    logger.info('task start')
    task = UpdateId('UpdateId', logger, islive)
    logger.info('task create')
    #task.run()
    QgsApplication.taskManager().addTask(task)
    logger.info('task add')
    pass
