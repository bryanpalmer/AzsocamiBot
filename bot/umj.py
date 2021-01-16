# umj.py
"""UMJ module provides database calls to TheUnderMineJournal items database."""

import json

import mysql.connector as mysql
import wowclasses


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
