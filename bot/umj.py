# umj.py
"""UMJ module provides database calls to TheUnderMineJournal items database."""

import json

import mysql.connector as mysql
import wowclasses

# DEFS for my implementation
HOUSE_ID = 68

# common price check, returns house, item, level, price, quantity, lastseen
# SELECT * FROM `tblItemSummary` where house=68 and item=171276

# get last ah datetime, returns house, nextcheck, lastdaily, lastcheck, lastchecksuccess
# SELECT * FROM `tblHouseCheck` where house=68

# READ https://medium.com/opex-analytics/database-connections-in-python-extensible-reusable-and-secure-56ebcf9c67fe
class umj_connection(object):
    """MySql db connection to UMJ"""

    def __init__(self):
        # self.connection_string = connection_string
        self.connector = None

    def __enter__(self):
        self.connector = mysql.connect(
            user="",
            password="",
            host="newswire.theunderminejournal.com",
            port=3306,
            database="newsstand",
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb is None:
            self.connector.commit()
        else:
            self.connector.rollback()
        self.connector.close()


def umj_connector(func):
    def with_connection_(*args, **kwargs):
        # conn_str = os.environ["CONN"]
        cnn = mysql.connect(
            user="",
            password="",
            host="newswire.theunderminejournal.com",
            port=3306,
            database="newsstand",
        )
        try:
            rv = func(cnn, *args, **kwargs)
        except Exception:
            cnn.rollback()
            print("UMJ database connection error")
            raise
        else:
            cnn.commit()
        finally:
            cnn.close()
        return rv

    return with_connection_


def create_connection():
    conn = None
    try:
        conn = mysql.connect(
            user="",
            password="",
            host="newswire.theunderminejournal.com",
            port=3306,
            database="newsstand",
        )
    except mysql.Error as e:
        print(e)
    finally:
        return conn


@umj_connector
def getLastHouseCheck(cnn):
    """Returns last weekly datetime umj database was updated."""

    cur = cnn.cursor()
    cur.execute(f"SELECT lastcheck from tblHouseCheck WHERE house={HOUSE_ID};")
    row = cur.fetchone()
    return row[0]


# get last ah datetime, returns house, nextcheck, lastdaily, lastcheck, lastchecksuccess
# SELECT * FROM `tblHouseCheck` where house=68


@umj_connector
def getItemsListById(cnn, itemList):
    retList = []
    cur = cnn.cursor()
    sql = """SELECT i.id, i.name_enus, i.quality, i.level, i.class, s.name_enus, i.icon, i.stacksize, i.buyfromvendor
        FROM tblDBCItem i
        LEFT JOIN tblDBCItemSubClass s ON s.class=i.class AND s.subclass=i.subclass
        WHERE id=%s;"""
    for item in itemList:
        cur.execute(sql, (item[0],))
        rec = cur.fetchone()
        retList.append(wowclasses.Item(rec))
    return retList


def getItemById(conn, itemId):
    retVal = None
    try:
        sql = """SELECT i.id, i.name_enus, i.quality, i.level, i.class, s.name_enus, i.icon, i.stacksize, i.buyfromvendor
            FROM tblDBCItem i
            LEFT JOIN tblDBCItemSubClass s ON s.class=i.class AND s.subclass=i.subclass
            WHERE id=%s;"""
        cur = conn.cursor()
        cur.execute(sql, (itemId,))
        record = cur.fetchone()
        # print(type(record))
        retVal = wowclasses.Item(record)
    except mysql.Error as e:
        print(e.args[0])
    return retVal


def getItemByName(conn, itemName):
    retVal = None
    searchVal = itemName.lower()
    try:
        sql = """SELECT i.id, i.name_enus, i.quality, i.level, i.class, s.name_enus, i.icon, i.stacksize, i.buyfromvendor
            FROM tblDBCItem i
            LEFT JOIN tblDBCItemSubClass s ON s.class=i.class AND s.subclass=i.subclass
            WHERE lower(name_enus)=%s;"""
        cur = conn.cursor()
        cur.execute(sql, (searchVal,))
        record = cur.fetchone()
        # print(type(record))
        retVal = wowclasses.Item(record)
    except mysql.Error as e:
        print(e.args[0])
    return retVal
