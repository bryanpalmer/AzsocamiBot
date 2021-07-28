# main.py
# TODO: Add automatic versioning system
# versioneer
VERSION = "0.2.11"
VERSIONDATE = "2021-07-28"

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

import discord
from discord.ext import commands, tasks
from discord.ext.commands import CommandNotFound

import botlib
import wowapi
import wowclasses
import umj

# Critical Vars and Settings
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX")  # Bot command prefix
ENVVERSION = os.getenv("ENV_VERSION")  # Local .env or server vars
TIMEZONE = "US/Central"  # Timezone for bot responses
TIMEFORMAT = "%Y-%m-%d %H:%M:%S %Z"

# In Test mode, bot uses non bot-test token instead of production bot token
BOTMODE = os.getenv("BOTMODE")  # TEST or PROD
TESTBOT = os.getenv("BOTMODE") == "TEST"
if TESTBOT:
    DISCORD_BOT_TOKEN = os.getenv("TEST_BOT_TOKEN")
else:
    DISCORD_BOT_TOKEN = os.getenv("AZSOCAMIBOT_TOKEN")

# In dev mode, certain functions are more verbose than normal
DEVMODE = os.getenv("DEVMODE") == "TRUE"  # Boolean flag for devmode
DEBUG_MODE = os.getenv("DEBUG_MODE") == "TRUE"  # Currently unused
if DEVMODE:
    print("Environment vars: ", ENVVERSION)
    print("Current Bot: ", BOTMODE)
    print("Bot Token: ", DISCORD_BOT_TOKEN)
    print("Debug mode: ", DEBUG_MODE)


bot = commands.Bot(command_prefix=COMMAND_PREFIX)
# Remove built-in help command
# bot.remove_command("help")


@bot.event
async def on_ready():
    print(f"AzsocamiBot version {VERSION} is now online.")
    print(f"Bot name is {bot.user.name}, ID={bot.user.id}")
    print(f"Using {ENVVERSION}")
    print(f"Command prefix is:  {COMMAND_PREFIX}")


@bot.event
async def on_message(message):
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, exc):
    if isinstance(exc, CommandNotFound):
        pass
    else:
        print(exc)


###############################################################
###############################################################
###                                                         ###
###                 BOT COMMANDS                            ###
###                                                         ###
###############################################################
###############################################################


@bot.command()
@commands.is_owner()
async def status(ctx):
    msg = f"AzsocamiBot version {VERSION}, released {VERSIONDATE}.\n"
    msg += "Bot running as "
    if TESTBOT:
        msg += "TEST BOT.\n"
    else:
        msg += "PRODUCTION BOT.\n"
    msg += f"Server Timezone:  {time.tzname}\n"
    msg += f"Server Time:  {datetime.datetime.now().strftime(TIMEFORMAT)}\n"
    msg += f"Bot Local Time:  {botlib.localNow()}\n"
    msg += f"Bot source is at https://github.com/bryanpalmer/AzsocamiBot\n"
    msg += f"Bot running on heroku.com\n"
    await ctx.send(msg)


@bot.command(hidden=True)
@commands.is_owner()
async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")


@bot.command(hidden=True)
@commands.is_owner()
async def unload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")


@bot.command()
async def version(ctx):
    await ctx.send(f"AzsocamiBot version {VERSION}, released {VERSIONDATE}.")


@bot.command()
async def getlastreset(ctx):
    await ctx.send(
        f"The last reset datetime was {wowapi.getLastResetDateTime()} Local ({localTimeStr(wowapi.getLastResetDateTime())})"
    )


def localTimeStr(utcTime):
    return utcTime.astimezone(timezone(TIMEZONE)).strftime(TIMEFORMAT)


@bot.command()
async def changelog(ctx):
    msg = """
```## 0.1.60 - 2021-06-29
 - Added .br4 <charname> <seasonId> command.

## 0.1.50 - 2021-03-31
 - Fixed .mats to include Vantus runes.

## 0.1.48 - 2021-03-04
 - Added .bestruns command to track Mythic+ Season best runs.

## 0.1.46 - 2021-02-05
 - Fixed LastReset datetime variables to Tuesday, 15:00 UTC.

## 0.1.44 - 2021-01-26
 - Added .gvault command to track weekly m+ runs for vault.

## 0.1.43 - 2021-01-25
 - Added .tc command to track Twisting Corridors runs.

## 0.1.42 - 2021-01-25
 - Added commands to add and remove raidmats items.
 - Changed clean to handle bulk messages without rate-limiting.

## 0.1.41 - 2021-01-22
 - Changed .lpc to accept armorType as argument, ie .lpc plate.
 - Changed .lpc getLegendaryArmorsList() to avoid lengthy item lookups.
 - Changed .help to show all current commands.

## 0.1.40 - 2021-01-18
 - Added .lpc (.legendaries) command
 - Added automatic hourly background updates of member data.

## 0.1.38 - 2021-01-17
 - Added .changelog command.
 - Added .version command.
 - Added .status command.
 - Changed time displays to use CST instead of UTC.
 - Fixed getAuctionHouse() to handle bad responses.
 - Fixed WoW API auth token calls to handle bad responses.

## 0.1.35 - 2021-01-16
 - Added .team update to force armory update.
 - Added auto-deployment from repo to Heroku server
 - Changed code now lives on github (Ask Bryan for access)
 - Changed .team to get data from db instead of armory
 - Changed .mats and .team now record time last run in db
 - Changed db access from mariadb to mysql
```"""
    await ctx.send(msg)


def devmode(msg):
    if DEVMODE:
        print(msg)


# @tasks.loop(hours=2)
# async def updateTeamDataBG():
#     print("Updating Team data in background.")
#     if DEVMODE == False:
#         # bot-logs channel 799290844862480445
#         botLogs = bot.get_channel(799290844862480445)
#     if DEVMODE == True:
#         botLogs = bot.get_channel(790667200197296138)
#     await botLogs.send(f"UpdateTeamDataBG: {localTimeStr(datetime.datetime.now())}")
#     wowapi.updateAllMemberData()


# @tasks.loop(hours=1)
# async def updateMythicPlusDataBG():
#     print("Updating M+ data in background.")
#     if DEVMODE == False:
#         # bot-logs channel 799290844862480445
#         botLogs = bot.get_channel(799290844862480445)
#     if DEVMODE == True:
#         botLogs = bot.get_channel(790667200197296138)
#     await botLogs.send(
#         f"UpdateMythicPlusDataBG: {localTimeStr(datetime.datetime.now())}"
#     )
#     updates = wowapi.updateMythicPlusScores()
#     if len(updates) > 0:
#         for rec in updates:
#             await announceUpdate(rec)
#             await hiddenAnnouncedScoreUpdate(rec["name"])


print(os.getcwd())

## Load in and activate cogs
# for filename in os.listdir("./bot/cogs"):
#     if filename.endswith(".py"):
#         bot.load_extension(f"cogs.{filename[:-3]}")

bot.load_extension(f"cogs.core")
bot.load_extension(f"cogs.members")
bot.load_extension(f"cogs.mythicplus")
bot.load_extension(f"cogs.auctionhouse")
bot.load_extension(f"cogs.database")
# bot.load_extension(f"cogs.customhelp")
# bot.load_extension(f"cogs.events")

bot.run(DISCORD_BOT_TOKEN)
