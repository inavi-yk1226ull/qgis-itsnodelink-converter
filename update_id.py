from .stopwatch import Stopwatch
from .db_post import DbPost

class UpdateId:
    def __init__(self):
        self.post_db = DbPost()
        pass

    # 노드
    # 권역 반복
    def node_repeat_adm(self, max_adm):
        for current_adm in range(1, max_adm):
            sqlstr = "select region_cd from moct.adm_boundary where gid = '{0}'".format(current_adm)
            rows = self.post_db.execute_query(sqlstr)
            region_cd = rows[0][0]
            serial_num = self.get_max_num(region_cd)
            print("region_cd: {0}, num: {1}".format(region_cd, serial_num))
            self.node_update_id(current_adm, int(serial_num) + 1)
            if current_adm == 30:
                break
            pass
        pass

    # 권역 최대 일련번호 확인
    def get_max_num(self, _int):
        sqlstr = "select * from moct.fn_select_max_serial_num_node('{0}')".format(_int)
        rows = self.post_db.execute_query(sqlstr)
        return rows[0][0]

    # 권역 내 노드의 일련번호 & id 부여
    def node_update_id(self, current_adm, serial_num):
        sqlstr = "select * from moct.fn_select_node_if_nodeid_is_null('{0}')".format(current_adm)
        cursor = self.post_db.execute_query_cursor(sqlstr)

        rows = cursor.fetchall()
        # get id field
        gid_field = [desc[0] for desc in cursor.description].index("gid")
        tmp_field = [desc[0] for desc in cursor.description].index("tmpid")

        for row in rows:
            sqlstr = """ UPDATE moct.moct_node_data
                                SET node_id = %s
                                WHERE gid = %s"""
            node_id = current_adm + serial_num + '00'
            serial_num = serial_num + 1
            gid = row[gid_field]
            self.post_db.execute_with_args(sqlstr, (node_id, gid))

            # 해당 링크를 찾아야한다.
            tmpid = row[tmp_field]
            '''
            Update moct.moct_link_data
            SET f_node = %s
            WHERE f_node = %s
            '''
            self.post_db.execute_with_args(sqlstr, (e, tmpid))
            pass
        cursor.close()

    # ----------------------------------------------------------------------------------------------------------------------
    # 링크
    def link_repeat_adm(self, max_adm):
        for current_adm in range(1, max_adm):
            sqlstr = "select region_cd from moct.adm_boundary where gid = '{0}'".format(current_adm)
            rows = self.post_db.execute_query(sqlstr)
            region_cd = rows[0][0]
            serial_num = self.link_get_max_num(region_cd)
            print("region_cd: {0}, num: {1}".format(region_cd, serial_num))
            self.link_update_id(current_adm, int(serial_num) + 1)
            if current_adm == 30:
                break
            pass
        pass

    # 권역 최대 일련번호 확인
    def link_get_max_num(self, current_adm):
        sqlstr = "select * from moct.fn_select_max_serial_num('{0}')".format(current_adm)
        rows = self.post_db.execute_query(sqlstr)
        return rows[0][0]

    # 권역 내 링크의 일련번호 & id 부여
    def link_update_id(self, current_adm, serial_num):
        sqlstr = "select * from moct.fn_select_link_if_linkid_is_null('{0}')".format(current_adm)
        cursor = self.post_db.execute_query_cursor(sqlstr)

        rows = cursor.fetchall()
        # get id field
        gid_field = [desc[0] for desc in cursor.description].index("gid")
        fnode_field = [desc[0] for desc in cursor.description].index("f_node")
        tnode_field = [desc[0] for desc in cursor.description].index("t_node")
        sosfnode_field = [desc[0] for desc in cursor.description].index("sosfnodeid")
        sostnode_field = [desc[0] for desc in cursor.description].index("sostnodeid")

        for row in rows:
            sqlstr = """ UPDATE moct.moct_link_data
                        SET link_id = %s
                        WHERE gid = %s"""
            link_id = current_adm + serial_num + '00'
            serial_num = serial_num + 1
            gid = row[gid_field]
            self.post_db.execute_with_args(sqlstr, (link_id, gid))

            # 페어 확인 후 update
            link_id = current_adm + serial_num + '00'
            serial_num = serial_num + 1

            fnode = row[fnode_field]
            tnode = row[tnode_field]
            sosfnode = row[sosfnode_field]
            sostnode = row[sostnode_field]

            sqlstr = """ UPDATE moct.moct_link_data
                        SET link_id = %s
                        WHERE f_node = %s AND t_node = %s AND sosfnodeid = %s AND sostnodeid = %s """

            self.post_db.execute_with_args(sqlstr, (link_id, tnode, fnode, sostnode, sosfnode))
            pass
        cursor.close()

    def main_process(self):
        # 커넥션 get
        logsw = Stopwatch()
        self.post_db.connect()

        sqlstr = 'select count(*) from moct.adm_boundary'
        rows = self.post_db.execute_query(sqlstr)

        # 링크 반복 시작
        max_adm = rows[0][0]
        self.link_repeat_adm(max_adm)
        
        # 권역에 걸친 링크 처리
        self.update_id_when_id_is_null()
        pass
    pass

    def update_id_when_id_is_null(self):
        sqlstr = ''
        pass
