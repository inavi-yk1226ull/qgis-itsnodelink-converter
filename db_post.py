# -*- coding: utf-8 -*-
from qgis.core import QgsDataSourceUri, QgsVectorLayer, QgsProject

from .psycopg2 import psycopg

isLocal = True


class DbPost:

    def __init__(self):
        pass

    def pg_query_insert(self, _sqlstr):
        global isLocal
        if isLocal:
            conn = psycopg.connect(database='spatialdb', user='dev',
                                   password='12qwaszx', host='127.0.0.1', port='5432')
        else:
            conn = psycopg.connect(database='kslink', user='kslink_agent',
                                   password='ag9TmuS875', host='61.33.249.242', port='5432')
        cur = conn.cursor()
        cur.execute(_sqlstr)
        conn.commit()
        cur.close()
        pass

    def connect(self):
        conn = psycopg.connect(database='kslink', user='kslink_agent',
                               password='ag9TmuS875', host='61.33.249.242', port='5432')
        conn = psycopg.connect(database='spatialdb', user='dev',
                               password='12qwaszx', host='127.0.0.1', port='5432')
        return conn.closed  # 0이면 연결, 1이면 실패 or close

    def execute(self, _sqlstr):
        global isLocal
        if isLocal:
            conn = psycopg.connect(database='spatialdb', user='dev',
                                   password='12qwaszx', host='127.0.0.1', port='5432')
        else:
            conn = psycopg.connect(database='kslink', user='kslink_agent',
                                   password='ag9TmuS875', host='61.33.249.242', port='5432')
        cur = conn.cursor()
        cur.execute(_sqlstr)
        conn.commit()
        cur.close()
        pass

    def execute_query(self, _sqlstr):
        global isLocal
        if isLocal:
            conn = psycopg.connect(database='spatialdb', user='dev',
                                   password='12qwaszx', host='127.0.0.1', port='5432')
        else:
            conn = psycopg.connect(database='kslink', user='kslink_agent',
                                   password='ag9TmuS875', host='61.33.249.242', port='5432')
        cur = conn.cursor()
        cur.execute(_sqlstr)
        results = cur.fetchall()
        cur.close()
        return results

    def execute_query_cursor(self, _sqlstr):
        global isLocal
        if isLocal:
            conn = psycopg.connect(database='spatialdb', user='dev',
                                   password='12qwaszx', host='127.0.0.1', port='5432')
        else:
            conn = psycopg.connect(database='kslink', user='kslink_agent',
                                   password='ag9TmuS875', host='61.33.249.242', port='5432')
        cur = conn.cursor()
        cur.execute(_sqlstr)
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
        global isLocal
        if isLocal:
            conn = psycopg.connect(database='spatialdb', user='dev',
                                   password='12qwaszx', host='127.0.0.1', port='5432')
        else:
            conn = psycopg.connect(database='kslink', user='kslink_agent',
                                   password='ag9TmuS875', host='61.33.249.242', port='5432')
        cur = conn.cursor()
        cur.execute(sqlstr, param)
        conn.commit()
        cur.close()
        pass
