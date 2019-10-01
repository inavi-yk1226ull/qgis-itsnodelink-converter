# -*- coding: utf-8 -*-

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
        return results
