# wowapi.py

import datetime
import json
import os

import mariadb
import requests

import umj  # DB calls for TheUndermineJournal items database
import wowclasses


# Environment vars already loaded from dotenv or Heroku vars
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = 3306
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
        conn = mariadb.connect(
            user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT, database=DB_NAME
        )
    except mariadb.Error as e:
        print(e)
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
    except mariadb.Error as e:
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
            SET value = ?, expires=?
            WHERE id = 'access_token';""",
            (accessToken, expiresDT),
        )
        conn.commit()
        devmode(
            f"Updating access token to: {accessToken} and expiration to: {expiresDT}"
        )
    except mariadb.Error as e:
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
            "insert into members (name, realmslug, role) values (?,?,?);", memberData
        )
        conn.commit()
        statusMsg = (
            f"Added {playerName.title()}, ({playerRealm.lower()}) as {playerRole}"
        )
    except mariadb.Error as e:
        print("Error: " + e.args[0])
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
        cursor.execute("delete from members where name=?;", (playerName.title(),))
        conn.commit()
        statusMsg = f"Successfully removed {playerName.title()}."
    except mariadb.Error as e:
        print("Error: " + e.args[0])
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
        cursor.execute("UPDATE members SET role=? WHERE name=?;", memberData)
        conn.commit()
        statusMsg = f"{playerName.title()} changed to {playerRole}."

    except mariadb.Error as e:
        print("Error: " + e.args[0])

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


def updateMemberById(conn, recId, charObj):
    sql = """UPDATE members
        SET 
            wowid       = ?,
            name        = ?,
            class       = ?,
            spec        = ?,
            level       = ?,
            gender      = ?,
            realmname   = ?,
            realmslug   = ?,
            realmid     = ?,
            guild       = ?,
            faction     = ?,
            race        = ?,
            covenant    = ?,
            ilevel      = ?, 
            expires     = ?
        WHERE id = ?;"""

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
    except mariadb.Error as e:
        print("Error: " + e.args[0])


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


def getLastRun(procName):
    retVal = None
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT lastrun FROM dtcache WHERE process=?;", (procName,))
        row = cur.fetchone()
        retVal = row[0]
        conn.close()

    except mariadb.Error as e:
        print("Error: " + e.args[0])

    return retVal


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
    resp = requests.post(
        token_uri,
        data={
            "grant_type": "client_credentials",
            "client_id": BNET_CLIENTID,
            "client_secret": BNET_SECRET,
        },
    )
    # devmode(resp.text)
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
    return {"status": status, "message": message, "raw_response": accessTokenResponse}


def getCharacterInfo(charName, charRealm):
    token = getAccessToken()
    profile_uri = f"https://us.api.blizzard.com/profile/wow/character/{charRealm}/"
    response = requests.get(
        profile_uri + charName.lower(),
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


def getAuctionHouseData():
    # returns json for all auction house data
    print("getAuctionHouseData()...")
    token = getAccessToken()
    # server realm is hardcoded to silver-hand:12
    auctionHouse_uri = (
        "https://us.api.blizzard.com/data/wow/connected-realm/12/auctions"
    )
    response = requests.get(
        auctionHouse_uri,
        params={"namespace": "dynamic-us", "locale": "en_US", "access_token": token},
    )
    ahdata = json.loads(response.text)
    return ahdata


###############################################################
###############################################################
###                                                         ###
###              DATABASE TABLE DEFINITIONS                 ###
###                                                         ###
###############################################################
###############################################################
# https://lingojam.com/GiantTextGenerator

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
            "insert into dtcache (process, lastrun) values (?,?);", activitiesList
        )
        conn.commit()
        conn.close()
    except mariadb.Error as e:
        print(e.args[0])


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
            ("Isage", "silver-hand", "Melee DPS"),
            ("Murinn", "silver-hand", "Tank"),
            ("Antigen", "silver-hand", "Healer"),
            ("Kaitaa", "silver-hand", "Healer"),
            ("Innestra", "silver-hand", "Tank"),
            ("Nixena", "silver-hand", "Alt"),
        ]
        cursor.executemany(
            "insert into members (name, realmslug, role) values (?,?,?);", memberList
        )
        conn.commit()
        conn.close()
    except mariadb.Error as e:
        print(e.args[0])


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
        ]
        cursor.executemany("insert into raidmats (id, name) values (?,?);", matList)
        conn.commit()
        conn.close()
    except mariadb.Error as e:
        print(e.args[0])
