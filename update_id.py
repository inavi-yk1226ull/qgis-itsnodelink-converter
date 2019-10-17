from .stopwatch import Stopwatch
from .db_post import DbPost
import logging
import os


class UpdateId:
    def __init__(self, _logger):
        self.post_db = DbPost()
        # 로그
        absFilePath = os.path.abspath(__file__)
        os.chdir(os.path.dirname(absFilePath))
        self.logpath = os.path.join(os.getcwd(), "logging.log")
        self.mlogger = _logger

        # 링크의 권역 별 최대 일련번호 적재
        self._dict = {}
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
            self.logging_info("  region_{0} get_max_num: {1}".format(region_cd, sw.CheckPoint()))
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
        sqlstr = "select * from moct.fn_select_max_serial_num_node('{0}')".format(_int)
        rows = self.post_db.execute_query(sqlstr)
        return rows[0][0]

    # 권역 내 노드의 일련번호 & id 부여
    def node_update_id(self, current_adm, serial_num, sw):
        sqlstr = "select * from moct.fn_select_node_if_nodeid_is_null('{0}')".format(current_adm)
        cursor = self.post_db.execute_query_cursor(sqlstr)

        rows = cursor.fetchall()
        # get id field
        gid_field = [desc[0] for desc in cursor.description].index("gid")
        tmp_field = [desc[0] for desc in cursor.description].index("tmpid")

        self.logging_info("    대상 노드 select 완료: {0}".format(sw.CheckPoint()))

        for row in rows:
            sqlstr = """ UPDATE moct.moct_node_data
                                SET node_id = %s
                                WHERE gid = %s"""
            node_id = str(serial_num) + '00'
            serial_num = serial_num + 1
            gid = row[gid_field]
            self.post_db.execute_with_args(sqlstr, (node_id, gid))

            self.logging_info("    node id update complete: {0}".format(sw.CheckPoint()))

            # 연결된 링크 업데이트 _f
            tmpid = row[tmp_field]
            sqlstr = '''
            Update moct.moct_link_data
            SET f_node = %s
            WHERE sosfnodeid = %s
            '''
            self.post_db.execute_with_args(sqlstr, (node_id, tmpid))

            self.logging_info("    F link id update complete: {0}".format(sw.CheckPoint()))

            # 연결된 링크 업데이트 _t
            tmpid = row[tmp_field]
            sqlstr = '''
            Update moct.moct_link_data
            SET t_node = %s
            WHERE sostnodeid = %s
            '''
            self.post_db.execute_with_args(sqlstr, (node_id, tmpid))

            self.logging_info("    T link id update complete: {0}".format(sw.CheckPoint()))

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
        sqlstr = '''
        select substring(link_id from 1 for 3)
            , max(substring(link_id from 4 for 5)) as serial
        from moct.moct_link_data 
        where is_delete is False
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
            sqlstr = "select * from moct.moct_link_data where CAST(f_node AS BIGINT) > CAST(t_node AS BIGINT) AND (link_id is null or link_id = '') AND is_delete IS NOT True"
            pass
        else:
            sqlstr = "select * from moct.moct_link_data where CAST(t_node AS BIGINT) > CAST(f_node AS BIGINT) AND (link_id is null or link_id = '') AND is_delete IS NOT True"
            pass

        cursor = self.post_db.execute_query_cursor(sqlstr)

        gid_field = [desc[0] for desc in cursor.description].index("gid")
        fnode_field = [desc[0] for desc in cursor.description].index("f_node")
        tnode_field = [desc[0] for desc in cursor.description].index("t_node")

        # 재생성
        post_db_2 = DbPost()
        post_db_2.connect()

        for row in cursor:
            _gid = row[gid_field]
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

            self.logging_info("    get link's region: {0}".format(sw.CheckPoint()))

            # 메인
            # _max_num = int(self.link_get_max_num(_region_cd)) + 1
            _max_num = int(_region_cd + str(self._dict[int(_region_cd)] + 1))

            _link_id = str(_max_num) + '00'
            _sqlstr = """ UPDATE moct.moct_link_data
                        SET link_id = %s
                        WHERE gid = %s"""
            self.post_db.execute_with_args(_sqlstr, (_link_id, _gid))
            self._dict[int(_region_cd)] = self._dict[int(_region_cd)] + 1

            self.logging_info("    link update: {0}".format(sw.CheckPoint()))

            # 쌍
            _max_num = _max_num + 1
            _link_id = str(_max_num) + '00'
            sqlstr = """ UPDATE moct.moct_link_data
                        SET link_id = %s
                        WHERE f_node = %s AND t_node = %s """
            self.post_db.execute_with_args(sqlstr, (_link_id, _tnode, _fnode))
            self._dict[int(_region_cd)] = self._dict[int(_region_cd)] + 1

            self.logging_info("    pair link update: {0}".format(sw.CheckPoint()))

            pass
        cursor.close()
        pass

    def main_process(self):
        # 커넥션 get
        logsw = Stopwatch()
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
        pass

    pass
