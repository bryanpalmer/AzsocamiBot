# wowapi.py
from urllib.parse import urlparse

import discord

import datetime

# from datetime import datetime
import json
import os
import pytz

# import mariadb
import mysql.connector as mysql
import requests

import umj  # DB calls for TheUndermineJournal items database
import wowclasses
import botlib

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
    # print(lastReset)
    return utc.localize(lastReset)


def getPrevResetDateTime():
    utc = pytz.UTC
    today = datetime.date.today()
    last_tue = today - datetime.timedelta(days=offset)

    last_tue = today - datetime.timedelta(days=offset) - datetime.timedelta(days=7)
    lastReset = datetime(last_tue.year, last_tue.month, last_tue.day, 15, 0, 0)
    # print(lastReset)
    return utc.localize(lastReset)


def getAccessToken():
    """ Get current access token from db or generate new on from API."""
    token, expires = getAccessTokenFromDB()
    # devmode(f"Token: {token}, Expires: {expires}")
    # devmode(f"Current datetime: {datetime.now()}")
    # print(f"getAccessToken: expires={expires}")
    # print(f"getAccessToken: datetime.datetime.now={datetime.datetime.now()}")
    if expires > datetime.datetime.now():
        # print("Using token from database.")
        return token
    else:
        # print("Generating new token.")
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


def api_raiderio_char_mplus_best_runs(playerName, playerRealm):
    raiderio_uri = "https://raider.io/api/v1/characters/profile"
    parameters = {
        "region": "us",
        "realm": playerRealm,
        "name": playerName,
        "fields": "mythic_plus_best_runs",
    }
    response = requests.get(raiderio_uri, params=parameters)
    if response.status_code != 200:
        print(f"Error retrieving {playerName} {playerRealm}")
        dataJson = (
            f"{'{'}" f'"name":"{playerName}",' f'"mythic_plus_best_runs": []' f"{'}'}"
        )
        return dataJson
    else:
        dataJson = json.loads(response.text)
        return dataJson


def api_raiderio_char_mplus_alternate_runs(playerName, playerRealm):
    raiderio_uri = "https://raider.io/api/v1/characters/profile"
    parameters = {
        "region": "us",
        "realm": playerRealm,
        "name": playerName,
        "fields": "mythic_plus_alternate_runs",
    }
    response = requests.get(raiderio_uri, params=parameters)
    if response.status_code != 200:
        print(f"Error retrieving {playerName} {playerRealm}")
        dataJson = (
            f"{'{'}"
            f'"name":"{playerName}",'
            f'"mythic_plus_alternate_runs": []'
            f"{'}'}"
        )
        return dataJson
    else:
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


def api_raiderio_char_mplus_previous(playerName, playerRealm):
    raiderio_uri = "https://raider.io/api/v1/characters/profile"
    parameters = {
        "region": "us",
        "realm": playerRealm,
        "name": playerName,
        "fields": "mythic_plus_scores_by_season:previous",
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


def api_raiderio_mythicplus_ranks(playerName, playerRealm="silver-hand"):
    raiderio_uri = "https://raider.io/api/v1/characters/profile"
    parameters = {
        "region": "us",
        "realm": playerRealm,
        "name": playerName,
        "fields": "mythic_plus_ranks",
    }
    response = requests.get(raiderio_uri, params=parameters)
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


def getClassIconUrl(className):
    retVal = ""
    if className == "Warrior":
        retVal = "https://render.worldofwarcraft.com/us/icons/56/classicon_warrior.jpg"
    elif className == "Paladin":
        retVal = "https://render.worldofwarcraft.com/us/icons/56/classicon_paladin.jpg"
    elif className == "Hunter":
        retVal = "https://render.worldofwarcraft.com/us/icons/56/classicon_hunter.jpg"
    elif className == "Rogue":
        retVal = "https://render.worldofwarcraft.com/us/icons/56/classicon_rogue.jpg"
    elif className == "Priest":
        retVal = "https://render.worldofwarcraft.com/us/icons/56/classicon_priest.jpg"
    elif className == "Death Knight":
        retVal = (
            "https://render.worldofwarcraft.com/us/icons/56/classicon_deathknight.jpg"
        )
    elif className == "Shaman":
        retVal = "https://render.worldofwarcraft.com/us/icons/56/classicon_shaman.jpg"
    elif className == "Mage":
        retVal = "https://render.worldofwarcraft.com/us/icons/56/classicon_mage.jpg"
    elif className == "Warlock":
        retVal = "https://render.worldofwarcraft.com/us/icons/56/classicon_warlock.jpg"
    elif className == "Monk":
        retVal = "https://render.worldofwarcraft.com/us/icons/56/classicon_monk.jpg"
    elif className == "Druid":
        retVal = "https://render.worldofwarcraft.com/us/icons/56/classicon_druid.jpg"
    elif className == "Demon Hunter":
        retVal = (
            "https://render.worldofwarcraft.com/us/icons/56/classicon_demonhunter.jpg"
        )
    return retVal


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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
            "lvl5qty": 0,
            "lvl5cost": 0,
            "lvl6qty": 0,
            "lvl6cost": 0,
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
    conn = create_connection()
    cur = conn.cursor()
    expiresDT = calcExpiresDateTime(expires_in)
    # print(f"updateAccessToken: token={accessToken} expires_in={expiresDT}")
    try:
        cur.execute(
            """UPDATE config
            SET value = %s, expires=%s
            WHERE id = 'access_token';""",
            (accessToken, expiresDT),
        )
        conn.commit()
        print(f"Updating access token to: {accessToken} and expiration to: {expiresDT}")
    except mysql.Error as e:
        print(e.args[0])

    conn.close()


def updateAccessTokenInDB(accessToken, expires_in):
    # print(f"updateAccessTokenInDB: token={accessToken} expires_in={expires_in}")
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
        print(f"Updating access token to: {accessToken} and expiration to: {expiresDT}")
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
    sql = "SELECT id, name, realmslug FROM members ORDER BY name;"
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


# def cmdRaidMats():
#     raidMats = getRaidMats()
#     ahData = getAuctionHouseData()
#     umjConn = umj.create_connection()

#     for mat in raidMats:
#         # fill out class/subclass info from items db
#         curId = raidMats[mat]["id"]
#         item = umj.getItemById(umjConn, curId)
#         raidMats[mat]["classname"] = item.classname
#         raidMats[mat]["subclass"] = item.subclass

#     for auction in ahData["auctions"]:
#         # check auction data for raw mats
#         if auction["item"]["id"] in raidMats:
#             curID = auction["item"]["id"]
#             raidMats[curID]["quantity"] += auction["quantity"]
#             if (
#                 raidMats[curID]["unitcost"] == 0
#                 or auction["unit_price"] / 10000 < raidMats[curID]["unitcost"]
#             ):
#                 raidMats[curID]["unitcost"] = auction["unit_price"] / 10000

#     umjConn.close()
#     setLastRun("AUCTION_HOUSE")
#     lastRun = datetime.now()

#     foodTxt = ""
#     alchTxt = ""
#     lwTxt = ""
#     oreTxt = ""
#     goodsTxt = ""
#     miscTxt = ""

#     for key in raidMats:
#         name = raidMats[key]["name"]
#         qty = raidMats[key]["quantity"]
#         ttlcost = raidMats[key]["unitcost"]
#         mattype = raidMats[key]["subclass"]
#         matclass = raidMats[key]["classname"]
#         # assign each mat to a specific embed field
#         if matclass == "Tradeskill" and (mattype == "Herb" or mattype == "Other"):
#             if qty > 0:
#                 alchTxt += f"{ name }: {qty} - *{round(ttlcost,0)}g*\n"
#             else:
#                 alchTxt += f"{ name }: None Available\n"

#         elif matclass == "Tradeskill" and mattype == "Cooking":
#             if qty > 0:
#                 foodTxt += f"{ name }: {qty} - *{round(ttlcost,0)}g*\n"
#             else:
#                 foodTxt += f"{ name }: None Available\n"

#         elif matclass == "Tradeskill" and mattype == "Metal & Stone":
#             if qty > 0:
#                 oreTxt += f"{ name }: {qty} - *{round(ttlcost,0)}g*\n"
#             else:
#                 oreTxt += f"{ name }: None Available\n"

#         elif matclass == "Tradeskill" and (mattype == "Leather" or mattype == "Cloth"):
#             if qty > 0:
#                 lwTxt += f"{ name }: {qty} - *{round(ttlcost,0)}g*\n"
#             else:
#                 lwTxt += f"{ name }: None Available\n"

#         elif (
#             matclass == "Consumable"
#             and (
#                 mattype == "Potion"
#                 or mattype == "Flask"
#                 or mattype == "Other"
#                 or mattype == "Food & Drink"
#                 or mattype == "Vantus Runes"
#             )
#         ) or (matclass == "Item Enhancement" and mattype == "Misc"):
#             if qty > 0:
#                 goodsTxt += f"[{ name }](https://www.wowhead.com/item={key}): {qty} - *{round(ttlcost,0)}g*\n"
#             else:
#                 goodsTxt += (
#                     f"[{ name }](https://www.wowhead.com/item={key}): None Available\n"
#                 )

#         else:
#             if qty > 0:
#                 miscTxt += f"{ name }: {qty} - *{round(ttlcost,0)}g*\n"
#             else:
#                 miscTxt += f"{ name }: None Available\n"
#             print(f"{key} - {name} missing category:  {matclass} | {mattype}")

#     response = discord.Embed(
#         title="Raid Mats",
#         url="https://www.wowhead.com/",
#         description="Current auction house prices for common raid mats on our server.",
#         color=discord.Color.blue(),
#     )
#     aLines = botlib.str2embedarray(alchTxt)
#     for i, line in enumerate(aLines):
#         if len(line) > 0:
#             fieldName = f"Alchemy Mats{'' if i==0 else ' cont.'}"
#             response.add_field(name="Alchemy Mats", value=line, inline=False)

#     aLines = botlib.str2embedarray(foodTxt)
#     for i, line in enumerate(aLines):
#         if len(line) > 0:
#             fieldName = f"Cooking Mats{'' if i==0 else ' cont.'}"
#             response.add_field(name=fieldName, value=line, inline=False)

#     # response.add_field(name="\u200b", value="\u200b", inline=False)

#     aLines = botlib.str2embedarray(lwTxt)
#     for i, line in enumerate(aLines):
#         if len(line) > 0:
#             fieldName = f"LW / Cloth Mats{'' if i==0 else ' cont.'}"
#             response.add_field(name=fieldName, value=line, inline=False)

#     aLines = botlib.str2embedarray(oreTxt)
#     for i, line in enumerate(aLines):
#         if len(line) > 0:
#             fieldName = f"Smithing Mats{'' if i==0 else ' cont.'}"
#             response.add_field(name=fieldName, value=line, inline=False)

#     aLines = botlib.str2embedarray(goodsTxt)
#     for i, line in enumerate(aLines):
#         if len(line) > 0:
#             fieldName = f"Finished Goods{'' if i==0 else ' cont.'}"
#             response.add_field(name=fieldName, value=line, inline=False)

#     aLines = botlib.str2embedarray(miscTxt)
#     for i, line in enumerate(aLines):
#         if len(line) > 0:
#             fieldName = f"Uncategorized Items{'' if i==0 else ' cont.'}"
#             response.add_field(name=fieldName, value=line, inline=False)

#     response.set_footer(
#         text=f"Auction house data last collected at {botlib.localTimeStr(lastRun)}"
#     )

#     return response
#     # await botlib.send_embed(ctx, response)


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
            "select id, name, realmslug, highscore from mythicplus where active=1 ORDER BY highscore desc, name asc;"
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


def getMythicPlusPlayers():
    devmode(f"Retrieving mythic plus scores")
    conn = create_connection()
    cursor = conn.cursor()
    retList = []
    try:
        cursor.execute(
            "select id, name, realmslug, highscore from mythicplus where active=1 ORDER BY name asc;"
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
    devmode(f"Retrieving mythic plus players list")
    conn = create_connection()
    cursor = conn.cursor()
    retList = []
    cursor.execute(
        "select id, name, realmslug, highscore, prevscore from mythicplus where active=1;"
    )
    rows = cursor.fetchall()
    for row in rows:
        # print(row)
        playerName = row[1].title()
        playerRealm = row[2].lower()
        playerScore = row[3]
        playerPrev = row[4]
        resultData = api_raiderio_char_mplus_score(playerName, playerRealm)
        if "mythic_plus_scores_by_season" in resultData:
            currentScore = int(
                resultData["mythic_plus_scores_by_season"][0]["scores"]["all"]
            )
        else:
            currentScore = 0

        ## New high score incoming
        if playerScore < currentScore:
            previousScore = playerScore
            highScore = currentScore
            ## also add player data to return list for processing messages
            mbr = {
                "name": playerName,
                "realm": playerRealm,
                "high": highScore,
                "prev": previousScore,
            }
            retList.append(mbr)
        else:
            previousScore = playerPrev
            highScore = currentScore

        thumbnail = resultData.get("thumbnail_url")

        updateMythicPlusById(conn, row[0], highScore, previousScore, thumbnail)
    if len(retList) > 0:
        print(f"M+ Updates: {retList}")
    return retList


def updateMythicPlusById(conn, recId, highScore, prevScore, thumbnail):
    sql = "UPDATE mythicplus SET highscore = %s, prevscore = %s, thumbnail_url = %s WHERE id = %s;"
    mbr = (highScore, prevScore, thumbnail, recId)
    try:
        cur = conn.cursor()
        cur.execute(sql, mbr)
        conn.commit()
    except mysql.Error as e:
        print(f"Error:  {e}")


def updateMythicPlusScoreById(recId, highScore, prevScore):
    mbr = (highScore, prevScore, recId)
    sql = "UPDATE mythicplus SET highscore = %s, prevscore = %s WHERE id = %s;"
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute(sql, mbr)
        conn.commit()
        conn.close()
    except mysql.Error as e:
        print(f"Error:  {e}")


def getMythicPlusByName(playerName):
    playerName = playerName.title()
    retVal = None
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, name, realmslug, highscore, prevscore, active FROM mythicplus WHERE name=%s;",
            (playerName,),
        )
        row = cur.fetchone()
        # print(row)
        retVal = row
        conn.close()
    except mysql.Error as e:
        print(f"Error:  {e.args[0]}")
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
        # print(resp.text)
        accessTokenResponse = json.loads(resp.text)
        # print(accessTokenResponse)
        if accessTokenResponse.get("access_token") is None:
            # no access token
            status = "fail"
            message = "Something went wrong trying to get an access token."
            # print(message)
        else:
            # access token returned
            # print(f"New access token generated: {accessTokenResponse}")
            status = "ok"
            message = "New access token save and ready for use."
            updateAccessTokenInDB(
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


def getTokenInfo():
    token = getAccessToken()
    # https://us.api.blizzard.com/data/wow/token/index?namespace=dynamic-us&locale=en_US&access_token=
    profile_uri = f"https://us.api.blizzard.com/data/wow/token/index"
    response = requests.get(
        profile_uri,
        params={
            "namespace": "dynamic-us",
            "locale": "en_US",
            "region": "us",
            "access_token": token,
        },
    )
    tokenData = json.loads(response.text)
    # print(tokenData)
    return tokenData


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
                id              INTEGER   PRIMARY KEY AUTO_INCREMENT,
                name            NVARCHAR (30) UNIQUE,
                realmslug       VARCHAR (25) DEFAULT ('silver-hand'),
                highscore       INTEGER DEFAULT (0),
                prevscore       INTEGER DEFAULT (0),
                thumbnail_url   VARCHAR (255) DEFAULT(''),
                active          TINYINT(1) DEFAULT (1)
            );"""
        cursor.execute(sql)
        conn.commit()
        memberList = [
            ("Aaryn", "silver-hand", 0, 1),
            ("Murinn", "silver-hand", 0, 1),
            ("Kaitaa", "silver-hand", 0, 1),
            ("Razzlectria", "silver-hand", 0, 1),
            ("Cradon", "silver-hand", 0, 1),
            ("Ragebear", "silver-hand", 0, 1),
            ("Agaviss", "silver-hand", 0, 1),
            ("Frënchie", "silver-hand", 0, 1),
            ("Areisda", "silver-hand", 0, 1),
            ("Aryxi", "silver-hand", 0, 1),
            ("Ekkoe", "farstriders", 0, 1),
            ("Pert", "farstriders", 0, 1),
            ("Pertnok", "farstriders", 0, 1),
            ("Antigen", "silver-hand", 0, 1)
            # ,("Bubblebutt", "bloodhoof", 0, 1),
        ]
        cursor.executemany(
            "insert into mythicplus (name, realmslug, highscore, active) values (%s,%s,%s,%s);",
            memberList,
        )
        conn.commit()
        conn.close()
    except mysql.Error as e:
        print(e)


## WIP - NOT ACTIVE YET
def initMythicPlusRanksTable():
    print("Reinitializing MythicRanks Table")
    try:
        conn = create_connection()
        cursor = conn.cursor()
        # drop existing table
        cursor.execute("DROP TABLE IF EXISTS mythicranks;")
        sql = """CREATE TABLE mythicranks (
                id              INTEGER   PRIMARY KEY AUTO_INCREMENT,
                name            NVARCHAR (30) UNIQUE,
                realmslug       VARCHAR (25) DEFAULT ('silver-hand'),
                tankrank        INTEGER DEFAULT (0),
                dpsrank         INTEGER DEFAULT (0),
                healsrank       INTEGER DEFAULT (0),
                tankurl         VARCHAR (255) DEFAULT(''),
                dpsurl          VARCHAR (255) DEFAULT(''),
                healsurl        DEFAULT('')
            );"""
        cursor.execute(sql)
        conn.commit()
        memberList = [
            ("Aaryn", "silver-hand"),
            ("Murinn", "silver-hand"),
            ("Kaitaa", "silver-hand"),
            ("Razzlectria", "silver-hand"),
            ("Cradon", "silver-hand"),
            ("Ragebear", "silver-hand"),
            ("Agaviss", "silver-hand"),
            ("Frënchie", "silver-hand"),
            ("Areisda", "silver-hand"),
            ("Aryxi", "silver-hand"),
            ("Velalda", "silver-hand"),
        ]
        cursor.executemany(
            "insert into mythicplus (name, realmslug) values (%s,%s);",
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
                name        NVARCHAR (30) UNIQUE,
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
