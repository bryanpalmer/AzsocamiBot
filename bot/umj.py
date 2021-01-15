# umj.py
"""UMJ module provides database calls to TheUnderMineJournal items database."""

import json

import mariadb
import wowclasses

# import requests


def create_connection():
    conn = None
    try:
        conn = mariadb.connect(
            user="",
            password="",
            host="newswire.theunderminejournal.com",
            port=3306,
            database="newsstand",
        )
    except mariadb.Error as e:
        print(e)
    finally:
        return conn


# class Item:
#     def __init__(self, itemRec):
#         if itemRec != None:
#             self.id = itemRec[0]
#             self.name = itemRec[1]
#             self.quality = itemRec[2]
#             self.level = itemRec[3]
#             self.classname = self.getClassName(itemRec[4])
#             self.subclass = itemRec[5]
#             self.icon = itemRec[6]
#             self.stacksize = itemRec[7]
#             self.buyfromvendor = itemRec[8]

#     def getClassName(self, classId):
#         item_classes = {
#             0: "Consumable",
#             1: "Container",
#             2: "Weapon",
#             3: "Gem",
#             4: "Armor",
#             5: "Reagent",
#             6: "Projectile",
#             7: "Tradeskill",
#             8: "Item Enhancement",
#             9: "Recipe",
#             11: "Quiver",
#             12: "Quest",
#             13: "Key",
#             15: "Miscellaneous",
#             16: "Glyph",
#             17: "Battle Pets",
#             18: "WoW Token",
#         }
#         return item_classes[classId]


def getItemById(conn, itemId):
    retVal = None
    try:
        sql = """SELECT i.id, i.name_enus, i.quality, i.level, i.class, s.name_enus, i.icon, i.stacksize, i.buyfromvendor
            FROM tblDBCItem i
            LEFT JOIN tblDBCItemSubClass s ON s.class=i.class AND s.subclass=i.subclass
            WHERE id=?;"""
        cur = conn.cursor()
        cur.execute(sql, (itemId,))
        record = cur.fetchone()
        # print(type(record))
        retVal = wowclasses.Item(record)
    except mariadb.Error as e:
        print(e.args[0])
    return retVal


def getItemByName(conn, itemName):
    retVal = None
    searchVal = itemName.lower()
    try:
        sql = """SELECT i.id, i.name_enus, i.quality, i.level, i.class, s.name_enus, i.icon, i.stacksize, i.buyfromvendor
            FROM tblDBCItem i
            LEFT JOIN tblDBCItemSubClass s ON s.class=i.class AND s.subclass=i.subclass
            WHERE lower(name_enus)=?;"""
        cur = conn.cursor()
        cur.execute(sql, (searchVal,))
        record = cur.fetchone()
        # print(type(record))
        retVal = wowclasses.Item(record)
    except mariadb.Error as e:
        print(e.args[0])
    return retVal


# May not need this, will just use subclass as type for now
# def getMatType(classname, subclass)
#     matType = None
#     if classname == 'Tradeskill' and subclass == "Herb":
#         matType = "Herb"
