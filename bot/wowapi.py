# wowapi.py
from urllib.parse import urlparse

import datetime
import json
import os
import pytz

# import mariadb
import mysql.connector as mysql
import requests

import umj  # DB calls for TheUndermineJournal items database
import wowclasses


# Environment vars already loaded from dotenv or Heroku vars
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = 3306
print(DB_HOST, DB_USER, DB_PASS, DB_NAME, DB_PORT)
BNET_CLIENTID = os.getenv("BATTLENET_CLIENT_ID")
BNET_SECRET = os.getenv("BATTLENET_CLIENT_SECRET")

DEVMODE = os.getenv("DEVMODE") == "TRUE"


###############################################################
###############################################################
###                                                         ###
###                 GENERIC SUPPORT FUNCTIONS               ###
###                                                         ###
###############################################################
###############################################################


def devmode(msg):
    if DEVMODE:
        print(msg)


def calcExpiresDateTime(expires_in):
    retVal = datetime.datetime.now()
    return retVal + datetime.timedelta(0, expires_in)


def format_duration(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)


def getLastResetDateTime():
    # https://www.w3resource.com/python-exercises/date-time-exercise/python-date-time-exercise-19.php
    utc = pytz.UTC
    today = datetime.date.today()
    offset = (today.weekday() - 1) % 7
    last_tue = today - datetime.timedelta(days=offset)
    lastReset = datetime.datetime(last_tue.year, last_tue.month, last_tue.day, 15, 0, 0)
    print(lastReset)
    return utc.localize(lastReset)


def getPrevResetDateTime():
    utc = pytz.UTC
    today = datetime.date.today()
    last_tue = today - datetime.timedelta(days=offset)

    last_tue = today - datetime.timedelta(days=offset) - datetime.timedelta(days=7)
    lastReset = datetime.datetime(last_tue.year, last_tue.month, last_tue.day, 15, 0, 0)
    # print(lastReset)
    return utc.localize(lastReset)


def getAccessToken():
    """ Get current access token from db or generate new on from API."""
    token, expires = getAccessTokenFromDB()
    # devmode(f"Token: {token}, Expires: {expires}")
    # devmode(f"Current datetime: {datetime.datetime.now()}")
    if expires > datetime.datetime.now():
        # devmode("Using token from database.")
        return token
    else:
        # devmode("Generating new token.")
        generateAccessToken()
        token = getAccessTokenFromDB()
    return token


def getRole(charEntered):
    role = "None"
    if charEntered == "t":
        role = "Tank"
    elif charEntered == "h":
        role = "Healer"
    elif charEntered == "m":
        role = "Melee DPS"
    elif charEntered == "r":
        role = "Ranged DPS"
    elif charEntered == "a":
        role = "Alt"
    return role


###############################################################
###############################################################
###                                                         ###
###                RAIDER.IO API CALLS                      ###
###                                                         ###
###############################################################
###############################################################

# https://raider.io/api/v1/characters/profile?region=us&realm=silver-hand&name=aaryn&fields=mythic_plus_recent_runs
def api_raiderio_char_mplus_recent_runs(playerName, playerRealm):
    raiderio_uri = "https://raider.io/api/v1/characters/profile"
    parameters = {
        "region": "us",
        "realm": playerRealm,
        "name": playerName,
        "fields": "mythic_plus_recent_runs",
    }
    response = requests.get(raiderio_uri, params=parameters)
    # print( response.text )
    dataJson = json.loads(response.text)
    return dataJson


def api_raiderio_char_mplus_score(playerName, playerRealm):
    raiderio_uri = "https://raider.io/api/v1/characters/profile"
    parameters = {
        "region": "us",
        "realm": playerRealm,
        "name": playerName,
        "fields": "mythic_plus_scores_by_season:current",
    }
    response = requests.get(raiderio_uri, params=parameters)
    # print( response.text )
    dataJson = json.loads(response.text)
    return dataJson


def api_raiderio_char_mplus_rank(playerName, playerRealm):
    raiderio_uri = "https://raider.io/api/v1/characters/profile"
    parameters = {
        "region": "us",
        "realm": playerRealm,
        "name": playerName,
        "fields": "mythic_plus_ranks",
    }
    response = requests.get(raiderio_uri, params=parameters)
    # print( response.text )
    dataJson = json.loads(response.text)
    return dataJson


def api_raiderio_char_raid_progress(playerName, playerRealm):
    raiderio_uri = "https://raider.io/api/v1/characters/profile"
    parameters = {
        "region": "us",
        "realm": playerRealm,
        "name": playerName,
        "fields": "raid_progression",
    }
    response = requests.get(raiderio_uri, params=parameters)
    # print( response.text )
    dataJson = json.loads(response.text)
    return dataJson


###############################################################
###############################################################


def getClassesList():
    return {
        1: "Warrior",
        2: "Paladin",
        3: "Hunter",
        4: "Rogue",
        5: "Priest",
        6: "Death Knight",
        7: "Shaman",
        8: "Mage",
        9: "Warlock",
        10: "Monk",
        11: "Druid",
        12: "Demon Hunter",
    }


def getLegendaryArmorsList():
    return {
        173241: {
            "id": 173241,
            "name": "Grim-Veiled Robe",
            "classname": "Armor",
            "subclass": "Cloth",
            "type": "CLOTH",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        173243: {
            "id": 173243,
            "name": "Grim-Veiled Sandals",
            "classname": "Armor",
            "subclass": "Cloth",
            "type": "CLOTH",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        173244: {
            "id": 173244,
            "name": "Grim-Veiled Mittens",
            "classname": "Armor",
            "subclass": "Cloth",
            "type": "CLOTH",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        173245: {
            "id": 173245,
            "name": "Grim-Veiled Hood",
            "classname": "Armor",
            "subclass": "Cloth",
            "type": "CLOTH",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        173246: {
            "id": 173246,
            "name": "Grim-Veiled Pants",
            "classname": "Armor",
            "subclass": "Cloth",
            "type": "CLOTH",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        173247: {
            "id": 173247,
            "name": "Grim-Veiled Spaulders",
            "classname": "Armor",
            "subclass": "Cloth",
            "type": "CLOTH",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        173248: {
            "id": 173248,
            "name": "Grim-Veiled Belt",
            "classname": "Armor",
            "subclass": "Cloth",
            "type": "CLOTH",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        173249: {
            "id": 173249,
            "name": "Grim-Veiled Bracers",
            "classname": "Armor",
            "subclass": "Cloth",
            "type": "CLOTH",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        172314: {
            "id": 172314,
            "name": "Umbrahide Vest",
            "classname": "Armor",
            "subclass": "Leather",
            "type": "LEATHER",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        172315: {
            "id": 172315,
            "name": "Umbrahide Treads",
            "classname": "Armor",
            "subclass": "Leather",
            "type": "LEATHER",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        172316: {
            "id": 172316,
            "name": "Umbrahide Gauntlets",
            "classname": "Armor",
            "subclass": "Leather",
            "type": "LEATHER",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        172317: {
            "id": 172317,
            "name": "Umbrahide Helm",
            "classname": "Armor",
            "subclass": "Leather",
            "type": "LEATHER",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        172318: {
            "id": 172318,
            "name": "Umbrahide Leggings",
            "classname": "Armor",
            "subclass": "Leather",
            "type": "LEATHER",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        172319: {
            "id": 172319,
            "name": "Umbrahide Pauldrons",
            "classname": "Armor",
            "subclass": "Leather",
            "type": "LEATHER",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        172320: {
            "id": 172320,
            "name": "Umbrahide Waistguard",
            "classname": "Armor",
            "subclass": "Leather",
            "type": "LEATHER",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        172321: {
            "id": 172321,
            "name": "Umbrahide Armguards",
            "classname": "Armor",
            "subclass": "Leather",
            "type": "LEATHER",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        172322: {
            "id": 172322,
            "name": "Boneshatter Vest",
            "classname": "Armor",
            "subclass": "Mail",
            "type": "MAIL",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        172323: {
            "id": 172323,
            "name": "Boneshatter Treads",
            "classname": "Armor",
            "subclass": "Mail",
            "type": "MAIL",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        172324: {
            "id": 172324,
            "name": "Boneshatter Gauntlets",
            "classname": "Armor",
            "subclass": "Mail",
            "type": "MAIL",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        172325: {
            "id": 172325,
            "name": "Boneshatter Helm",
            "classname": "Armor",
            "subclass": "Mail",
            "type": "MAIL",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        172326: {
            "id": 172326,
            "name": "Boneshatter Greaves",
            "classname": "Armor",
            "subclass": "Mail",
            "type": "MAIL",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        172327: {
            "id": 172327,
            "name": "Boneshatter Pauldrons",
            "classname": "Armor",
            "subclass": "Mail",
            "type": "MAIL",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        172328: {
            "id": 172328,
            "name": "Boneshatter Waistguard",
            "classname": "Armor",
            "subclass": "Mail",
            "type": "MAIL",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        172329: {
            "id": 172329,
            "name": "Boneshatter Armguards",
            "classname": "Armor",
            "subclass": "Mail",
            "type": "MAIL",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        171412: {
            "id": 171412,
            "name": "Shadowghast Breastplate",
            "classname": "Armor",
            "subclass": "Plate",
            "type": "PLATE",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        171413: {
            "id": 171413,
            "name": "Shadowghast Sabatons",
            "classname": "Armor",
            "subclass": "Plate",
            "type": "PLATE",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        171414: {
            "id": 171414,
            "name": "Shadowghast Gauntlets",
            "classname": "Armor",
            "subclass": "Plate",
            "type": "PLATE",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        171415: {
            "id": 171415,
            "name": "Shadowghast Helm",
            "classname": "Armor",
            "subclass": "Plate",
            "type": "PLATE",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        171416: {
            "id": 171416,
            "name": "Shadowghast Greaves",
            "classname": "Armor",
            "subclass": "Plate",
            "type": "PLATE",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        171417: {
            "id": 171417,
            "name": "Shadowghast Pauldrons",
            "classname": "Armor",
            "subclass": "Plate",
            "type": "PLATE",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        171418: {
            "id": 171418,
            "name": "Shadowghast Waistguard",
            "classname": "Armor",
            "subclass": "Plate",
            "type": "PLATE",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        171419: {
            "id": 171419,
            "name": "Shadowghast Armguards",
            "classname": "Armor",
            "subclass": "Plate",
            "type": "PLATE",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        178926: {
            "id": 178926,
            "name": "Shadowghast Ring",
            "classname": "Armor",
            "subclass": "Miscellaneous",
            "type": "MISC",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        178927: {
            "id": 178927,
            "name": "Shadowghast Necklace",
            "classname": "Armor",
            "subclass": "Miscellaneous",
            "type": "MISC",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
        173242: {
            "id": 173242,
            "name": "Grim-Veiled Cape",
            "classname": "Armor",
            "subclass": "Cloth",
            "type": "MISC",
            "lvl1qty": 0,
            "lvl1cost": 0,
            "lvl2qty": 0,
            "lvl2cost": 0,
            "lvl3qty": 0,
            "lvl3cost": 0,
            "lvl4qty": 0,
            "lvl4cost": 0,
        },
    }


###############################################################
###############################################################


###############################################################
###############################################################
###                                                         ###
###                 WOWAPI DATABASE CALLS                   ###
###                                                         ###
###############################################################
###############################################################


def create_connection():
    conn = None
    try:
        conn = mysql.connect(
            user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT, database=DB_NAME
        )
    except mysql.Error as e:
        print(e)
        print(DB_HOST, DB_USER, DB_PASS, DB_NAME, DB_PORT)
    finally:
        return conn


def getAccessTokenFromDB():
    retVal = None
    expires = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        sql_query = """select value, expires as "[timestamp]" from config where id = 'access_token';"""
        cursor.execute(sql_query)
        record = cursor.fetchone()
        retVal = record[0]
        expires = record[1]
        cursor.close()
    except mysql.Error as e:
        print(e.args[0])
    finally:
        if conn:
            conn.close()
    return retVal, expires


def updateAccessToken(accessToken, expires_in):
    """Update access token in wowapi database."""

    conn = create_connection()
    cur = conn.cursor()
    expiresDT = calcExpiresDateTime(expires_in)
    try:
        cur.execute(
            """UPDATE config
            SET value = %s, expires=%s
            WHERE id = 'access_token';""",
            (accessToken, expiresDT),
        )
        conn.commit()
        devmode(
            f"Updating access token to: {accessToken} and expiration to: {expiresDT}"
        )
    except mysql.Error as e:
        print(e.args[0])

    conn.close()


def getMembersList():
    devmode("Retrieving Members List from DB")
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, realmslug, role, expires FROM members ORDER BY name;"
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def getTeamMembersList():
    devmode("Retrieving Team Members List from DB")
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT id, wowid, name, class,
            spec, level, gender, realmname,
            realmslug, realmid, guild, faction,
            race, covenant, ilevel, role
           FROM members ORDER BY name;"""
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def addMemberToDB(playerName, playerRealm, playerRole):
    devmode(
        f"Adding new member {playerName.title()} | {playerRealm.title()} | {playerRole}"
    )

    # charData = getCharacterInfo(playerName, playerRealm)

    conn = create_connection()
    cursor = conn.cursor()
    memberData = (playerName.title(), playerRealm.lower(), playerRole)
    statusMsg = ""
    try:
        cursor.execute(
            "insert into members (name, realmslug, role) values (%s,%s,%s);", memberData
        )
        conn.commit()
        statusMsg = (
            f"Added {playerName.title()}, ({playerRealm.lower()}) as {playerRole}"
        )
    except mysql.Error as e:
        print(f"Error:  {e.args[0]}")
        statusMsg = f"Error adding {playerName.title()}, ERROR: {e.args[0]}"
    finally:
        conn.close()
    return statusMsg


def deleteMemberFromDB(playerName):
    print(f"Removing member {playerName.title()}")
    conn = create_connection()
    cursor = conn.cursor()
    statusMsg = ""
    try:
        cursor.execute("delete from members where name=%s;", (playerName.title(),))
        conn.commit()
        statusMsg = f"Successfully removed {playerName.title()}."
    except mysql.Error as e:
        print(f"Error: {e.args[0]}")
        statusMsg = f"Error removing {playerName.title()}, ERROR: {e.args[0]}"
    finally:
        conn.close()
    return statusMsg


def changeMemberRole(playerName, playerRole):
    print(f"Changing member role {playerName.title()} | {playerRole}")
    statusMsg = "Error changing role.  Contact Bryan."
    try:
        conn = create_connection()
        cursor = conn.cursor()
        memberData = (playerRole, playerName.title())
        cursor.execute("UPDATE members SET role=%s WHERE name=%s;", memberData)
        conn.commit()
        statusMsg = f"{playerName.title()} changed to {playerRole}."

    except mysql.Error as e:
        print(f"Error:  {e.args[0]}")

    finally:
        conn.close()

    return statusMsg


def updateAllMemberData():
    print("Updating Members Data from WoW API")
    conn = create_connection()
    cursor = conn.cursor()
    sql = "SELECT id, name, realmslug FROM members;"
    cursor.execute(sql)
    rows = cursor.fetchall()
    for member in rows:
        memberId = member[0]
        memberName = member[1]
        memberRealm = member[2]
        print(f"Retrieving {memberName}")
        charData = getCharacterInfo(memberName, memberRealm)
        char = wowclasses.Character(charData)
        updateMemberById(conn, memberId, char)
    setLastRun("UPDATE_MEMBERS")


def updateMemberById(conn, recId, charObj):
    sql = """UPDATE members
        SET
            wowid       = %s,
            name        = %s,
            class       = %s,
            spec        = %s,
            level       = %s,
            gender      = %s,
            realmname   = %s,
            realmslug   = %s,
            realmid     = %s,
            guild       = %s,
            faction     = %s,
            race        = %s,
            covenant    = %s,
            ilevel      = %s,
            expires     = %s
        WHERE id = %s;"""

    mbr = (
        charObj.wowid,
        charObj.name,
        charObj.classname,
        charObj.active_spec,
        charObj.level,
        charObj.gender,
        charObj.realmname,
        charObj.realmslug,
        charObj.realmid,
        charObj.guild,
        charObj.faction,
        charObj.race,
        charObj.covenant,
        charObj.ilvl,
        datetime.datetime.now(),
        recId,
    )
    try:
        cur = conn.cursor()
        cur.execute(sql, mbr)
        conn.commit()
    except mysql.Error as e:
        print(f"Error:  {e.args[0]}")


def getAllTableRows(tableName):
    # returns list of table rows
    conn = create_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * from {tableName};")
    rows = cur.fetchall()
    conn.close()
    retList = []
    for row in rows:
        retList.append(row)
        # print(row)
    return retList


def getRaidMatsList():
    sql = "SELECT id, name FROM raidmats;"
    conn = create_connection()
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.close()
    retList = []
    for row in rows:
        retList.append(row[0])
    return retList


def getRaidMats():
    sql = "SELECT id, name FROM raidmats ORDER BY name;"
    conn = create_connection()
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.close()
    retList = {}
    for row in rows:
        retList[row[0]] = {
            "id": row[0],
            "name": row[1],
            "classname": "",
            "subclass": "",
            "type": "Unknown",
            "quantity": 0,
            "unitcost": 0,
        }
        # retList.append(row[0])
    return retList


# def getItemById(conn, itemId):
#         retVal = wowclasses.Item(record)


def addItemIdToDB(itemId):
    devmode(f"Adding new wow item {itemId}")
    umjconn = umj.create_connection()
    item = umj.getItemById(umjconn, itemId)
    itemData = (itemId, item.name)
    umjconn.close()
    conn = create_connection()
    cursor = conn.cursor()
    statusMsg = ""
    try:
        cursor.execute("insert into raidmats (id, name) values (%s, %s);", itemData)
        conn.commit()
        statusMsg = f"Added {itemId} - {item.name} to raidmats."
    except mysql.Error as e:
        print(f"Error:  {e.args[0]}")
        statusMsg = f"Error adding {itemId}, ERROR: {e}"
    finally:
        conn.close()
    return statusMsg


def deleteItemFromDB(itemId):
    print(f"Removing item {itemId}")
    conn = create_connection()
    cursor = conn.cursor()
    statusMsg = ""
    try:
        cursor.execute("delete from raidmats where id=%s;", (itemId,))
        conn.commit()
        statusMsg = f"Successfully removed {itemId}."
    except mysql.Error as e:
        print(f"Error:  {e.args[0]}")
        statusMsg = f"Error removing {itemId}, ERROR: {e}"
    finally:
        conn.close()
    return statusMsg


def getTableStructure(tableName):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute(f"DESCRIBE {tableName};")
    rows = cur.fetchall()
    conn.close()
    retList = []
    for row in rows:
        retList.append(row)
    return retList


def getTableContents(tableName):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {tableName};")
    rows = cur.fetchall()
    conn.close()
    retList = []
    for row in rows:
        retList.append(row)
    return retList


def getLastRun(procName):
    retVal = None
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT lastrun FROM dtcache WHERE process=%s;", (procName,))
        row = cur.fetchone()
        retVal = row[0]
        conn.close()

    except mysql.Error as e:
        print(f"Error:  {e.args[0]}")

    return retVal


def setLastRun(procName):
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE dtcache SET lastrun = %s WHERE process=%s;",
            (datetime.datetime.now(), procName.upper()),
        )
        conn.commit()
        conn.close()
    except mysql.Error as e:
        print(f"Error:  {e.args[0]}")


def addPlayerToMythicPlus(playerName, playerRealm):
    devmode(f"Adding new member {playerName.title()} | {playerRealm.title()}")
    conn = create_connection()
    cursor = conn.cursor()
    memberData = (playerName.title(), playerRealm.lower(), 0, 1)
    statusMsg = ""
    try:
        cursor.execute(
            "INSERT INTO mythicplus (name, realmslug, highscore, active) VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE active=%s",
            (playerName.title(), playerRealm.lower(), 0, 1, 1),
        )
        conn.commit()
        statusMsg = f"Added {playerName.title()}, ({playerRealm.lower()})"
    except mysql.Error as e:
        print(e.args[0])
        print(f"Error:  {e.args[0]}")
        statusMsg = f"{e}"
    finally:
        conn.close()
    return statusMsg


def removePlayerFromMythicPlus(playerName):
    devmode(f"Removing {playerName.title()}")
    conn = create_connection()
    cursor = conn.cursor()
    memberData = playerName.title()
    statusMsg = ""
    try:
        cursor.execute(
            cursor.execute(
                "update mythicplus set active=0 where name=%s;", (playerName.title(),)
            )
        )
        conn.commit()
        statusMsg = f"Unfollowed {playerName.title()}"
    except mysql.Error as e:
        print(f"Error:  {e.args[0]}")
        statusMsg = f"Error unfollowing {playerName.title()}, ERROR: {e.args[0]}"
    finally:
        conn.close()
    return statusMsg


def getMythicPlusScores():
    devmode(f"Retrieving mythic plus scores")
    conn = create_connection()
    cursor = conn.cursor()
    retList = []
    try:
        cursor.execute(
            "select id, name, realmslug, highscore from mythicplus where active=1 ORDER BY highscore desc;"
        )
        rows = cursor.fetchall()
        for row in rows:
            retList.append(row)
    except mysql.Error as e:
        print(e)
        print(f"Error:  {e.args[0]}")
    finally:
        conn.close()
    return retList


def updateMythicPlusScores():
    pass


###############################################################
###############################################################


###############################################################
###############################################################
###                                                         ###
###                 WOW API CALLS                           ###
###                                                         ###
###############################################################
###############################################################


def generateAccessToken():
    token_uri = "https://us.battle.net/oauth/token"
    try:
        resp = requests.post(
            token_uri,
            data={
                "grant_type": "client_credentials",
                "client_id": BNET_CLIENTID,
                "client_secret": BNET_SECRET,
            },
        )
        resp.raise_for_status()
        accessTokenResponse = json.loads(resp.text)
        if accessTokenResponse.get("access_token") is None:
            # no access token
            status = "fail"
            message = "Something went wrong trying to get an access token."
        else:
            # access token returned
            status = "ok"
            message = "New access token save and ready for use."
            updateAccessToken(
                accessTokenResponse["access_token"], accessTokenResponse["expires_in"]
            )

    except requests.exceptions.HTTPError as err:
        print(err)
        status = "fail"
        message = "Something went wrong trying to get an access token."

    finally:
        return {
            "status": status,
            "message": message,
            "raw_response": accessTokenResponse,
        }


def getCharacterInfo(charName, charRealm):
    token = getAccessToken()
    profile_uri = f"https://us.api.blizzard.com/profile/wow/character/{charRealm}/"
    response = requests.get(
        profile_uri + charName.lower(),
        params={"namespace": "profile-us", "locale": "en_US", "access_token": token},
    )
    charData = json.loads(response.text)
    return charData


def getCharacterAchievements(charName, charRealm):
    token = getAccessToken()
    profile_uri = f"https://us.api.blizzard.com/profile/wow/character/{charRealm}/{charName.lower()}/achievements"
    response = requests.get(
        profile_uri,
        params={"namespace": "profile-us", "locale": "en_US", "access_token": token},
    )
    charData = json.loads(response.text)
    return charData


def getCharacterEquipment(charName, charRealm):
    token = getAccessToken()
    profile_uri = f"https://us.api.blizzard.com/profile/wow/character/{charRealm}/"
    response = requests.get(
        profile_uri + charName.lower() + "/equipment",
        params={"namespace": "profile-us", "locale": "en_US", "access_token": token},
    )
    charData = json.loads(response.text)
    return charData


def getCharacterSeasonDetails(charName, charRealm, seasonId):
    token = getAccessToken()
    profile_uri = f"https://us.api.blizzard.com/profile/wow/character/{charRealm.lower()}/{charName.lower()}/mythic-keystone-profile/season/{seasonId}"
    try:
        response = requests.get(
            profile_uri,
            params={
                "namespace": "profile-us",
                "locale": "en_US",
                "access_token": token,
            },
        )
        response.raise_for_status()
        charData = json.loads(response.text)
    except requests.exceptions.HTTPError as err:
        print(err)
        charData = {}
    finally:
        return charData


def getGuildRoster(realmName, guildName):
    token = getAccessToken()
    profile_uri = (
        f"https://us.api.blizzard.com/data/wow/guild/{realmName}/{guildName}/roster"
    )
    try:
        response = requests.get(
            profile_uri,
            params={
                "namespace": "profile-us",
                "locale": "en_US",
                "access_token": token,
            },
        )
        response.raise_for_status()
        rosterData = json.loads(response.text)
    except requests.exceptions.HTTPError as err:
        print(err)
        rosterData = {}
    finally:
        return rosterData


def getAuctionHouseData():
    # returns json for all auction house data
    print("getAuctionHouseData()...")
    token = getAccessToken()
    # server realm is hardcoded to silver-hand:12
    auctionHouse_uri = (
        "https://us.api.blizzard.com/data/wow/connected-realm/12/auctions"
    )
    try:
        response = requests.get(
            auctionHouse_uri,
            params={
                "namespace": "dynamic-us",
                "locale": "en_US",
                "access_token": token,
            },
        )
        response.raise_for_status()
        ahdata = json.loads(response.text)

    except requests.exceptions.HTTPError as err:
        print(err)
        ahdata = {}

    finally:
        return ahdata


###############################################################
###############################################################
###                                                         ###
###              DATABASE TABLE DEFINITIONS                 ###
###                                                         ###
###############################################################
###############################################################
# https://lingojam.com/GiantTextGenerator

#  ████  ███  █   █ █████ █████  ████
# █     █   █ ██  █ █       █   █
# █     █   █ █ █ █ ████    █   █  ██
# █     █   █ █  ██ █       █   █   █
#  ████  ███  █   █ █     █████  ███
def initConfigTable():
    print("Reinitializing Config Table")
    try:
        conn = create_connection()
        cursor = conn.cursor()
        # drop existing table
        cursor.execute("DROP TABLE IF EXISTS config;")
        sql = """CREATE TABLE config (
                id          VARCHAR (20)  PRIMARY KEY,
                value       VARCHAR (200),
                expires     DATETIME);"""
        cursor.execute(sql)
        conn.commit()
        initialRecordsList = [
            ("access_token", "Invalid", datetime.datetime.now()),
        ]
        cursor.executemany(
            "insert into config (id, value, expires) values (%s,%s,%s);",
            initialRecordsList,
        )
        conn.commit()
        conn.close()
    except mysql.Error as e:
        print(e)


#  ████  █████  ████  ███   ████ █   █ █████
#  █   █   █   █     █   █ █     █   █ █
#  █   █   █   █     █████ █     █████ ████
#  █   █   █   █     █   █ █     █   █ █
#  ████    █    ████ █   █  ████ █   █ █████
def initDTCacheTable():
    print("Reinitializing DTCache Table")
    try:
        conn = create_connection()
        cursor = conn.cursor()
        # drop existing table
        cursor.execute("DROP TABLE IF EXISTS dtcache;")
        sql = """CREATE TABLE dtcache (
                process     VARCHAR (20)  PRIMARY KEY,
                lastrun     DATETIME NOT NULL
            );"""
        cursor.execute(sql)
        conn.commit()
        activitiesList = [
            ("UPDATE_MEMBERS", datetime.datetime.now()),
            ("AUCTION_HOUSE", datetime.datetime.now()),
        ]
        cursor.executemany(
            "insert into dtcache (process, lastrun) values (%s,%s);", activitiesList
        )
        conn.commit()
        conn.close()
    except mysql.Error as e:
        print(e)


# █   █ █   █ █████ █   █ █████  ████ ████  █     █   █ █████
# ██ ██  █ █    █   █   █   █   █     █   █ █     █   █ █
# █ █ █   █     █   █████   █   █     ████  █     █   █ █████
# █   █   █     █   █   █   █   █     █     █     █   █     █
# █   █   █     █   █   █ █████  ████ █     █████ █████ █████


def initMythicPlusTable():
    print("Reinitializing MythicPlus Table")
    try:
        conn = create_connection()
        cursor = conn.cursor()
        # drop existing table
        cursor.execute("DROP TABLE IF EXISTS mythicplus;")
        sql = """CREATE TABLE mythicplus (
                id          INTEGER   PRIMARY KEY AUTO_INCREMENT,
                name        VARCHAR (30) UNIQUE,
                realmslug   VARCHAR (25) DEFAULT ('silver-hand'),
                highscore   INTEGER,
                active      TINYINT(1) DEFAULT (1)
            );"""
        cursor.execute(sql)
        conn.commit()
        memberList = [
            ("Aaryn", "silver-hand", 1092, 1),
            ("Murinn", "silver-hand", 1094, 1),
            ("Kaitaa", "silver-hand", 1121, 1),
            ("Razzlectria", "silver-hand", 836, 1),
            ("Cradon", "silver-hand", 1092, 1),
            ("Ragebear", "silver-hand", 866, 1),
            ("Agaviss", "silver-hand", 837, 1),
            ("Frenchie", "silver-hand", 832, 1),
            ("Aresda", "silver-hand", 810, 1),
        ]
        cursor.executemany(
            "insert into mythicplus (name, realmslug, highscore, active) values (%s,%s,%s,%s);",
            memberList,
        )
        conn.commit()
        conn.close()
    except mysql.Error as e:
        print(e)


#  █   █ █████ █   █ ████  █████ ████  █████
#  ██ ██ █     ██ ██ █   █ █     █   █ █
#  █ █ █ ████  █ █ █ ████  ████  ████  █████
#  █   █ █     █   █ █   █ █     █   █     █
#  █   █ █████ █   █ ████  █████ █   █ █████
def initMembersTable():
    print("Reinitializing Members Table")
    try:
        conn = create_connection()
        cursor = conn.cursor()
        # drop existing table
        cursor.execute("DROP TABLE IF EXISTS members;")
        sql = """CREATE TABLE members (
                id          INTEGER   PRIMARY KEY AUTO_INCREMENT,
                wowid       INTEGER,
                name        VARCHAR (30) UNIQUE,
                class       VARCHAR (20),
                spec        VARCHAR (25),
                level       INTEGER,
                gender      VARCHAR (10),
                realmname   VARCHAR (25) DEFAULT ('Silver Hand'),
                realmslug   VARCHAR (25) DEFAULT ('silver-hand'),
                realmid     INTEGER DEFAULT (12),
                guild       VARCHAR (50),
                faction     VARCHAR(10),
                race        VARCHAR (25),
                covenant    VARCHAR (25),
                ilevel      INTEGER,
                role        VARCHAR (15),
                expires     DATETIME
            );"""
        cursor.execute(sql)
        conn.commit()
        memberList = [
            ("Aaryn", "silver-hand", "Melee DPS"),
            ("Nethershade", "silver-hand", "Ranged DPS"),
            ("Winteros", "silver-hand", "Ranged DPS"),
            ("Agaviss", "silver-hand", "Ranged DPS"),
            ("Murinn", "silver-hand", "Tank"),
            ("Antigen", "silver-hand", "Healer"),
            ("Kaitaa", "silver-hand", "Healer"),
            ("Nixena", "silver-hand", "Alt"),
            ("Aresda", "silver-hand", "Healer"),
            ("Cradon", "silver-hand", "Ranged DPS"),
        ]
        cursor.executemany(
            "insert into members (name, realmslug, role) values (%s,%s,%s);", memberList
        )
        conn.commit()
        conn.close()
    except mysql.Error as e:
        print(e)


# ████   ███  █████ ████  █   █  ███  █████ █████
# █   █ █   █   █   █   █ ██ ██ █   █   █   █
# ████  █████   █   █   █ █ █ █ █████   █   █████
# █   █ █   █   █   █   █ █   █ █   █   █       █
# █   █ █   █ █████ ████  █   █ █   █   █   █████
def initRaidmatsTable():
    print("Reinitializing Raidmats Table")
    try:
        conn = create_connection()
        cursor = conn.cursor()
        # drop existing table
        cursor.execute("DROP TABLE IF EXISTS raidmats;")
        sql = """CREATE TABLE raidmats (
                id     INTEGER   PRIMARY KEY,
                name   VARCHAR (250) NOT NULL
            );"""
        cursor.execute(sql)
        conn.commit()
        matList = [
            (169701, "Death Blossom"),
            (168583, "Widowbloom"),
            (168586, "Rising Glory"),
            (168589, "Marrowroot"),
            (170554, "Vigil's Torch"),
            (171315, "Nightshade"),
            (180457, "Shadestone"),
            (171841, "Shaded Stone"),
            (173204, "Lightless Silk"),
            (172089, "Desolate Leather"),
            (172094, "Callous Hide"),
            (172096, "Heavy Desolate Leather"),
            (172097, "Heavy Callous Hide"),
            (172053, "Tenebrous Ribs"),
            (172055, "Phantasmal Haunch"),
            (173034, "Silvergill Pike"),
            (173036, "Spinefin Piranha"),
            (173037, "Elysian Thade"),
            (171266, "Potion of the Hidden Spirit"),
            (171267, "Spiritual Healing Potion"),
            (171270, "Potion of Spectral Agility"),
            (171273, "Potion of Spectral Intellect"),
            (171275, "Potion of Spectral Strength"),
            (171276, "Spectral Flask of Power"),
            (171284, "Eternal Cauldron"),
            (172043, "Feast of Gluttonous Hedonism"),
            (172347, "Heavy Desolate Armor Kit"),
            (171437, "Shaded Sharpening Stone"),
            (171439, "Shaded Weightstone"),
            (181468, "Veiled Augment Rune"),
            (173167, "Vantus Rune: Castle Nathria"),
        ]
        cursor.executemany("insert into raidmats (id, name) values (%s,%s);", matList)
        conn.commit()
        conn.close()
    except mysql.Error as e:
        print(e)
