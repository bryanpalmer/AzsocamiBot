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


roster = wowapi.getGuildRoster("silver-hand", "azsocami")

# print(roster)
nPlayers = 0
classes = wowapi.getClassesList()

for member in roster["members"]:
    if member["character"]["level"] == 60:
        nPlayers += 1
        nClassId = member["character"]["playable_class"]["id"]
        print(f"{member['character']['name']} - {classes[nClassId]}")

print(f"{nPlayers} members found.")