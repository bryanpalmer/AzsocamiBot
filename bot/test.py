from os.path import dirname, join, os
from dotenv import load_dotenv

## Load up required environment variables if .env exists
## else vars are already loaded via heroku environment
## This must be done before importing wowapi and wowclasses
dotenv_path = join(dirname(__file__), "../.env")
print("Env vars in:", dotenv_path)
load_dotenv(
    dotenv_path,
    verbose=True,
)

import asyncio
import datetime
from pytz import timezone
from operator import itemgetter
import time
import os

import botlib
import wowapi
import wowclasses

playersList = wowapi.getMythicPlusPlayers()
results = []
for playerRow in playersList:
    realm = playerRow[2]
    player = playerRow[1].title()
    print(f"Retrieving {player} {realm}")
    rioBest = wowapi.api_raiderio_char_mplus_best_runs(player, realm)
    rioAlts = wowapi.api_raiderio_char_mplus_alternate_runs(player, realm)
    dDict = {
        "DOS": {
            "shortname": "DOS",
            "best_level": 0,
            "best_result": 0,
            "best_score": 0,
            "alt_level": 0,
            "alt_result": 0,
            "alt_score": 0,
        },
        "HOA": {
            "shortname": "HOA",
            "best_level": 0,
            "best_result": 0,
            "best_score": 0,
            "alt_level": 0,
            "alt_result": 0,
            "alt_score": 0,
        },
        "MISTS": {
            "shortname": "MISTS",
            "best_level": 0,
            "best_result": 0,
            "best_score": 0,
            "alt_level": 0,
            "alt_result": 0,
            "alt_score": 0,
        },
        "NW": {
            "shortname": "NW",
            "best_level": 0,
            "best_result": 0,
            "best_score": 0,
            "alt_level": 0,
            "alt_result": 0,
            "alt_score": 0,
        },
        "PF": {
            "shortname": "PF",
            "best_level": 0,
            "best_result": 0,
            "best_score": 0,
            "alt_level": 0,
            "alt_result": 0,
            "alt_score": 0,
        },
        "SD": {
            "shortname": "SD",
            "best_level": 0,
            "best_result": 0,
            "best_score": 0,
            "alt_level": 0,
            "alt_result": 0,
            "alt_score": 0,
        },
        "SOA": {
            "shortname": "SOA",
            "best_level": 0,
            "best_result": 0,
            "best_score": 0,
            "alt_level": 0,
            "alt_result": 0,
            "alt_score": 0,
        },
        "TOP": {
            "shortname": "TOP",
            "best_level": 0,
            "best_result": 0,
            "best_score": 0,
            "alt_level": 0,
            "alt_result": 0,
            "alt_score": 0,
        },
    }

    for run in rioBest["mythic_plus_best_runs"]:
        affix = run["affixes"][0]["name"]
        dung = run["short_name"]
        mlvl = run["mythic_level"]
        result = run["num_keystone_upgrades"]
        score = run["score"]

        if affix == "Fortified" and dDict[dung]["best_score"] == 0:
            dDict[dung]["best_score"] = score
            dDict[dung]["best_level"] = mlvl
            dDict[dung]["best_result"] = result
        elif affix == "Tyrannical" and dDict[dung]["alt_score"] == 0:
            dDict[dung]["alt_score"] = score
            dDict[dung]["alt_level"] = mlvl
            dDict[dung]["alt_result"] = result

    for run in rioAlts["mythic_plus_alternate_runs"]:
        affix = run["affixes"][0]["name"]
        dung = run["short_name"]
        mlvl = run["mythic_level"]
        result = run["num_keystone_upgrades"]
        score = run["score"]
        if affix == "Fortified" and dDict[dung]["best_score"] == 0:
            dDict[dung]["best_score"] = score
            dDict[dung]["best_level"] = mlvl
            dDict[dung]["best_result"] = result
        elif affix == "Tyrannical" and dDict[dung]["alt_score"] == 0:
            ## Only recording alternate run scores here
            dDict[dung]["alt_score"] = score
            dDict[dung]["alt_level"] = mlvl
            dDict[dung]["alt_result"] = result

    results.append((player, dDict))

# print(results)

msg = f"{'Player'.ljust(13)} {'DOS'.ljust(7)} {'HOA'.ljust(7)} {'MST'.ljust(7)} {'NW'.ljust(7)} {'PF'.ljust(7)} {'SD'.ljust(7)} {'SOA'.ljust(7)} {'TOP'.ljust(7)}\n"
for player in results:
    playerName = player[0]
    dDict = player[1]
    # print(player[0])
    fDOS = dDict["DOS"]["best_level"] if dDict["DOS"]["best_score"] > 0 else 0
    tDOS = dDict["DOS"]["alt_level"] if dDict["DOS"]["alt_score"] > 0 else 0
    fHOA = dDict["HOA"]["best_level"] if dDict["HOA"]["best_score"] > 0 else 0
    tHOA = dDict["HOA"]["alt_level"] if dDict["HOA"]["alt_score"] > 0 else 0
    fMISTS = dDict["MISTS"]["best_level"] if dDict["MISTS"]["best_score"] > 0 else 0
    tMISTS = dDict["MISTS"]["alt_level"] if dDict["MISTS"]["alt_score"] > 0 else 0
    fNW = dDict["NW"]["best_level"] if dDict["NW"]["best_score"] > 0 else 0
    tNW = dDict["NW"]["alt_level"] if dDict["NW"]["alt_score"] > 0 else 0
    fPF = dDict["PF"]["best_level"] if dDict["PF"]["best_score"] > 0 else 0
    tPF = dDict["PF"]["alt_level"] if dDict["PF"]["alt_score"] > 0 else 0
    fSD = dDict["SD"]["best_level"] if dDict["SD"]["best_score"] > 0 else 0
    tSD = dDict["SD"]["alt_level"] if dDict["SD"]["alt_score"] > 0 else 0
    fSOA = dDict["SOA"]["best_level"] if dDict["SOA"]["best_score"] > 0 else 0
    tSOA = dDict["SOA"]["alt_level"] if dDict["SOA"]["alt_score"] > 0 else 0
    fTOP = dDict["TOP"]["best_level"] if dDict["TOP"]["best_score"] > 0 else 0
    tTOP = dDict["TOP"]["alt_level"] if dDict["TOP"]["alt_score"] > 0 else 0

    msg += f"{playerName.ljust(13)} "
    msg += f"{fDOS:>2}/{tDOS:>2} | "
    msg += f"{fHOA:>2}/{tHOA:>2} | "
    msg += f"{fMISTS:>2}/{tMISTS:>2} | "
    msg += f"{fNW:>2}/{tNW:>2} | "
    msg += f"{fPF:>2}/{tPF:>2} | "
    msg += f"{fSD:>2}/{tSD:>2} | "
    msg += f"{fSOA:>2}/{tSOA:>2} | "
    msg += f"{fTOP:>2}/{tTOP:>2}\n"

print(msg)