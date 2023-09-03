import sqlite3
import os

dbPath = os.path.dirname(os.path.realpath(__file__)) + "/bots.db"


def sqlite_get_first(table, col, query):
    global dbPath
    connectLite = sqlite3.connect(dbPath)
    connectLite.row_factory = dict_factory
    if query is None:
        sql = 'SELECT * FROM "{0}" WHERE {1} IS NULL AND status=1'.format(table, col)
    else:
        sql = 'SELECT * FROM "{0}" WHERE "{1}"="{2}" AND status=1'.format(table, col, query)
    cur = connectLite.cursor()
    cur.execute(sql)
    return cur.fetchone()


def sqlite_first(table, where):
    global dbPath
    connectLite = sqlite3.connect(dbPath)
    connectLite.row_factory = dict_factory
    sql = 'SELECT * FROM "{0}" {1}'.format(table, where)
    cur = connectLite.cursor()
    cur.execute(sql)
    return cur.fetchone()


def sqlite_insert(table, row):
    global dbPath
    connectLite = sqlite3.connect(dbPath)
    cols = ', '.join('"{}"'.format(col) for col in row.keys())
    vals = ', '.join(':{}'.format(col) for col in row.keys())
    sql = 'INSERT INTO "{0}" ({1}) VALUES ({2})'.format(table, cols, vals)
    connectLite.cursor().execute(sql, row)
    connectLite.commit()


def sqlite_update(table, newData, whereCol, whereVal):
    global dbPath
    connectLite = sqlite3.connect(dbPath)
    sql = 'UPDATE {0} SET {1} WHERE {2} = "{3}" AND status=1'.format(table, newData, whereCol, whereVal)
    connectLite.cursor().execute(sql)
    connectLite.commit()


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def sqlite_random(table):
    global dbPath
    connectLite = sqlite3.connect(dbPath)
    connectLite.row_factory = dict_factory
    cur = connectLite.cursor()
    cur.execute('SELECT * FROM "{0}" ORDER BY RANDOM() LIMIT 1;'.format(table))
    return cur.fetchone()


def sqlite_delete(table, col, id):
    global dbPath
    connectLite = sqlite3.connect(dbPath)
    sql = 'DELETE FROM "{0}" WHERE "{1}"={2}'.format(table, col, id)
    cur = connectLite.cursor()
    cur.execute(sql)
    connectLite.commit()
    return "ok"
