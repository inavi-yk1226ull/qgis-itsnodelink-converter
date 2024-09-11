# -*- coding: utf-8 -*-
from qgis.core import QgsDataSourceUri, QgsVectorLayer, QgsProject

import psycopg2 as psycopg

# 배포 VM
PG_HOST = "10.10.82.177"
PG_DB_NAME = "kslink"
PG_PORT = "54003"
PG_USER = "postgres"
PG_PASSWORD = "p58v3VTLypDDAG"
PG_GEOM = "geom"
PG_EPSG = "5186"

# 로컬
# PG_HOST = "127.0.0.1"
# PG_DB_NAME = "kslink"
# PG_PORT = "5432"
# PG_USER = "postgres"
# PG_PASSWORD = "inavi9610"
# PG_GEOM = "geom"
# PG_EPSG = "5186"

PG_CONNECTION_STRING = (
    f"host='{PG_HOST}' port={PG_PORT} dbname='{PG_DB_NAME}' user='{PG_USER}' password='{PG_PASSWORD}'"
)
def get_conn():
    conn = psycopg.connect(PG_CONNECTION_STRING)
    cur = conn.cursor()
    return cur, conn

class DbPost:
    def __init__(self, _isLive):
        self.conn = psycopg.connect(PG_CONNECTION_STRING)

    def pg_query_insert(self, _sqlstr):
        cur = self.conn.cursor()
        cur.execute(_sqlstr)
        self.conn.commit()
        cur.close()

    def connect(self):
        if self.conn is None:
            self.conn = psycopg.connect(PG_CONNECTION_STRING)
        return self.conn.closed  # 0이면 연결, 1이면 실패 or close

    def execute(self, _sqlstr):
        cur = self.conn.cursor()
        cur.execute(_sqlstr)
        self.conn.commit()
        cur.close()

    def execute_query(self, _sqlstr):
        try:
            result = None
            cur, conn = get_conn()
            with conn:
                with cur:
                    cur.execute(_sqlstr)
                    result = cur.fetchall()
                conn.commit()
            if conn.closed == 0:
                conn.close()
        except Exception as e:
            print(f"Error fetching data: {e}")
        return result

    def execute_query_cursor(self, _sqlstr):
        cur = self.conn.cursor()
        cur.execute(_sqlstr)
        self.conn.commit()
        return cur

    def load_pg_layer(self, host='', port='', data='', user='', pw='',
                      _type='', srid='', schema='', table='',
                      geom_field='', where='', layer_name=''):
        # 호스트, 포트, 디비, 계정, 비밀번호
        # Wkb타입, Srid, 스키마, 테이블
        # geom컬럼, where절, 생성할 레이어 명칭
        uri = QgsDataSourceUri()
        uri.setSrid(srid)
        uri.setWkbType(_type)
        uri.setConnection(host, port, data, user, pw)
        uri.setDataSource(schema, table, geom_field, where)
        new_layer = QgsVectorLayer(uri.uri(), layer_name, 'postgres')
        QgsProject.instance().addMapLayer(new_layer)

    def execute_with_args(self, sqlstr, param):
        cur = self.conn.cursor()
        cur.execute(sqlstr, param)
        self.conn.commit()
        cur.close()
