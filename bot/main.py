# main.py
from os.path import dirname, join, os

from dotenv import load_dotenv

## Load up required environment variables if .env exists
## else vars are already loaded via heroku environment
## This must be done before importing wowapi and wowclasses
dotenv_path = join(dirname(__file__), "../.env")
load_dotenv(
    dotenv_path,
    verbose=True,
)


import asyncio
import datetime
from pytz import timezone
import time
import os

import discord
from discord.ext import commands

import wowapi
import wowclasses
import umj

# TODO: Set up logging for bot
# import logging

TESTBOT = os.getenv("BOTMODE") == "TEST"
BOTMODE = os.getenv("BOTMODE")
if TESTBOT:
    DISCORD_BOT_TOKEN = os.getenv("TEST_BOT_TOKEN")
else:
    DISCORD_BOT_TOKEN = os.getenv("AZSOCAMIBOT_TOKEN")
# DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ENVVERSION = os.getenv("ENV_VERSION")
DEVMODE = os.getenv("DEVMODE") == "TRUE"
DEBUG_MODE = os.getenv("DEBUG_MODE") == "TRUE"
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX")
TIMEZONE = "US/Central"
TIMEFORMAT = "%Y-%m-%d %H:%M:%S %Z%z"
if DEVMODE:
    print("Environment vars: ", ENVVERSION)
    print("Current Bot: ", BOTMODE)
    print("Bot Token: ", DISCORD_BOT_TOKEN)
    print("Debug mode: ", DEBUG_MODE)
    # COMMAND_PREFIX = ";"
# else:
# COMMAND_PREFIX = "."


bot = commands.Bot(command_prefix=COMMAND_PREFIX)
# Remove built-in help command
bot.remove_command("help")


@bot.event
async def on_ready():
    actMsg = "Let's Blame Ben"
    if DEVMODE == True:
        actMsg = "DEVMODE"

    await bot.change_presence(
        status=discord.Status.idle, activity=discord.Game(f"{actMsg}")
    )
    print("I am online")
    print(f"Using {ENVVERSION}")
    print(f"Command prefix is:  {COMMAND_PREFIX}")


@bot.event
async def on_message(message):
    # channel = bot.get_channel(799290844862480445)
    # await channel.send(message.content)
    await bot.process_commands(message)


###############################################################
###############################################################
###                                                         ###
###                 BOT COMMANDS                            ###
###                                                         ###
###############################################################
###############################################################

# HELP
@bot.command()
async def help(ctx):
    author = ctx.message.author
    embed = discord.Embed(color=discord.Color.orange())
    embed.set_author(name="Help")
    embed.add_field(
        name=".ping", value="Returns Pong to check bot latency.", inline=False
    )
    embed.add_field(
        name=".mats or .raidmats",
        value="Gets current Auction House pricing on common raid mats.",
        inline=False,
    )
    embed.add_field(
        name=".team or .raidteam",
        value="Gets current raid team lookup data.",
        inline=False,
    )
    embed.add_field(
        name=".rules", value="Guild rules to live by.  Esp rule #1.", inline=False
    )
    embed.add_field(
        name=".clean",
        value="Cleans all AzsocamiBot messages and commands from channel.",
        inline=False,
    )
    await ctx.send(embed=embed)
    if author.name.lower() == "aaryn":
        embed2 = discord.Embed(color=discord.Color.orange())
        embed2.set_author(name="Admin Only Commands")
        # embed2.add_field(
        #     name=".db_members", value="ADMIN: List members database rows.", inline=False
        # )
        embed2.add_field(
            name=".add_member",
            value="ADMIN: add_member <playername> <realm> Add new member.",
            inline=False,
        )
        embed2.add_field(
            name=".remove_member",
            value="ADMIN: remove_member <playername> Remove member.",
            inline=False,
        )
        embed2.add_field(
            name=".change_member_role",
            value="ADMIN: change_member_role <playername> Change member role.",
            inline=False,
        )
        embed2.add_field(
            name=".get_table_contents",
            value="ADMIN: get_table_contents <tablename> List table contents.",
            inline=False,
        )
        embed2.add_field(
            name=".get_table_structure",
            value="ADMIN: get_table_structure <tablename> List table structure.",
            inline=False,
        )

        await ctx.send(embed=embed2)


### RULES
@bot.command()
async def rules(ctx):
    msg = """
        Rule #1:  It's Ben's fault.  Always.
        Rule #2:  Priority loot order for plate classes is: Derek, Bryan, Tammie, the new guy, anyone that has a plate alt, anyone that wants to DE the drop for crystal, and finally Ben.
        Rule #3:  When speaking to Ben, please use small words.
        Rule #4:  If you are a priest, and Ben runs past you on a narrow walkway, you must yank him back.
        Rule #5:  Thou shall not upset thy tank or thy healer.
        """
    await ctx.send(msg)


### db_members (hidden)
@bot.command(hidden=True)
@commands.is_owner()
async def db_members(ctx):
    membersList = wowapi.getAllTableRows("members")
    msg = ""
    for member in membersList:
        print(member)
        for x in range(len(member)):
            msg += f"{member[x]} "
        msg += "\n"
    await ctx.send(msg)


@bot.command(hidden=True)
@commands.has_any_role("RAID LEAD", "ADMIN")
async def add_member(ctx, playerName, playerRealm="silver-hand"):
    msgId = await ctx.send(
        f"**T**ank or **H**ealer or **M**elee DPS or **R**anged DPS (or **A**lt)?"
    )
    # This will make sure that the response will only be registered if the following
    # conditions are met:
    def check(msg):
        return (
            msg.author == ctx.author
            and msg.channel == ctx.channel
            and msg.content.lower() in ["t", "h", "m", "r", "a"]
        )

    try:
        msg = await bot.wait_for(
            "message", check=check, timeout=20
        )  # 20 seconds to reply
        role = wowapi.getRole(msg.content.lower())
        await ctx.send(wowapi.addMemberToDB(playerName, playerRealm, role))
        await msg.delete()
        await msgId.delete()
    except asyncio.TimeoutError:
        await ctx.send("You didn't reply in time!  Cancelling player add.")
        await msgId.delete()


@bot.command(hidden=True)
@commands.has_any_role("RAID LEAD", "ADMIN")
async def remove_member(ctx, playerName):
    msgId = await ctx.send(f"Are you sure?  **Y**es or **N**o.")
    # This will make sure that the response will only be registered if the following
    # conditions are met:
    def check(msg):
        return (
            msg.author == ctx.author
            and msg.channel == ctx.channel
            and msg.content.lower() in ["y", "n"]
        )

    try:
        msg = await bot.wait_for(
            "message", check=check, timeout=20
        )  # 20 seconds to reply
        if msg.content.lower() == "y":
            await ctx.send(wowapi.deleteMemberFromDB(playerName))
        await msg.delete()
        await msgId.delete()
    except asyncio.TimeoutError:
        await ctx.send("You didn't reply in time!  Cancelling player add.")
        await msgId.delete()


@bot.command(hidden=True)
@commands.has_any_role("RAID LEAD", "ADMIN")
async def change_member_role(ctx, playerName):
    msgId = await ctx.send(
        f"**T**ank or **H**ealer or **M**elee DPS or **R**anged DPS (or **A**lt)?"
    )
    # This will make sure that the response will only be registered if the following
    # conditions are met:
    def check(msg):
        return (
            msg.author == ctx.author
            and msg.channel == ctx.channel
            and msg.content.lower() in ["t", "h", "m", "r", "a"]
        )

    try:
        msg = await bot.wait_for(
            "message", check=check, timeout=20
        )  # 30 seconds to reply
        role = wowapi.getRole(msg.content.lower())
        await ctx.send(wowapi.changeMemberRole(playerName, role))
        await msg.delete()
        await msgId.delete()
    except asyncio.TimeoutError:
        await ctx.send("You didn't reply in time!  Cancelling role change.")
        await msgId.delete()


###############################################################
###############################################################


@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong with {str(round(bot.latency, 2))}")


@bot.command(name="whoami")
async def whoami(ctx):
    await ctx.send(f"You are {ctx.message.author.name}, using {ENVVERSION}")


@bot.command()
async def clean(ctx, limit: int = 20):
    passed = 0
    failed = 0
    async for msg in ctx.message.channel.history(limit=limit):
        if msg.author.id == bot.user.id or msg.content[0] == COMMAND_PREFIX:
            try:
                await msg.delete()
                passed += 1
            except:
                failed += 1
    devmode(f"[Complete] Removed {passed} messages with {failed} fails")


@bot.command(aliases=["team"])
async def raidteam(ctx, arg1="DB"):

    if arg1.lower() == "update":
        teamMode = "API"
        teamList = wowapi.getMembersList()
    else:
        teamMode = "DB"
        teamList = wowapi.getTeamMembersList()

    conn = wowapi.create_connection()

    # team is dictionary with 5 roles, each with a list of character objects
    # added if the character falls into that role.
    team = {"Tank": [], "Healer": [], "Melee DPS": [], "Ranged DPS": [], "Alt": []}
    msgId = await ctx.send("Gathering member data...  Please wait.")

    ttlIlvl = 0
    memberCount = 0
    # waitMsg = "Gathering member data..."
    for key in teamList:
        if teamMode == "API":
            await msgId.edit(content=f"Retrieving {key[1]}")
            charData = wowapi.getCharacterInfo(key[1], key[2])
            character = wowclasses.Character(charData, "JSON")
            wowapi.updateMemberById(conn, key[0], character)
            memberRole = key[3]
        else:
            character = wowclasses.Character(key, "ROW")
            memberRole = key[15]

        team[memberRole].append(character)
        if memberRole != "Alt":
            ttlIlvl += character.ilvl
            memberCount += 1

    if teamMode == "API":
        wowapi.setLastRun("UPDATE_MEMBERS")
        lastRun = datetime.datetime.now()
    else:
        lastRun = wowapi.getLastRun("UPDATE_MEMBERS")

    armoryUrl = f"https://worldofwarcraft.com/en-us/character/us/"
    # print(jsonpickle.encode(team, indent=2))

    # Tanks field
    tanks = ""
    for member in team["Tank"]:
        tanks += f"**[{member.name}]({armoryUrl}{member.realmslug}/{member.name})** | "
        tanks += f"{member.active_spec} {member.classname} | {member.covenant} | "
        tanks += f"{member.gender} {member.race} | iLvl: {member.ilvl}\n"
    # Healers field
    heals = ""
    for member in team["Healer"]:
        heals += f"**[{member.name}]({armoryUrl}{member.realmslug}/{member.name})** | "
        heals += f"{member.active_spec} {member.classname} | {member.covenant} | "
        heals += f"{member.gender} {member.race} | iLvl: {member.ilvl}\n"
    # Melee DPS field
    mdps = ""
    for member in team["Melee DPS"]:
        mdps += f"**[{member.name}]({armoryUrl}{member.realmslug}/{member.name})** | "
        mdps += f"{member.active_spec} {member.classname} | {member.covenant} | "
        mdps += f"{member.gender} {member.race} | iLvl: {member.ilvl}\n"
    # Ranged DPS field
    rdps = ""
    for member in team["Ranged DPS"]:
        rdps += f"**[{member.name}]({armoryUrl}{member.realmslug}/{member.name})** | "
        rdps += f"{member.active_spec} {member.classname} | {member.covenant} | "
        rdps += f"{member.gender} {member.race} | iLvl: {member.ilvl}\n"
    # Alts field
    alts = ""
    for member in team["Alt"]:
        alts += f"**[{member.name}]({armoryUrl}{member.realmslug}/{member.name})** | "
        alts += f"{member.active_spec} {member.classname} | {member.covenant} | "
        alts += f"{member.gender} {member.race} | iLvl: {member.ilvl}\n"
    # Build response embed
    response = discord.Embed(
        title="Raid Team",
        url="https://www.warcraftlogs.com/guild/calendar/556460/",
        description=f"""Current guild raid team roster as of { lastRun.astimezone(timezone(TIMEZONE)).strftime(TIMEFORMAT) }.\nType **{COMMAND_PREFIX}team update** to force update from WoW armory.""",
        color=discord.Color.blue(),
    )
    reqBy = ctx.message.author.name
    reqPic = ctx.message.author.avatar_url
    response.set_footer(
        text=f"Requested by {reqBy} | Last crawled at {lastRun.astimezone(timezone(TIMEZONE)).strftime(TIMEFORMAT)}",
        icon_url=reqPic,
    )
    # response.set_footer(
    #     text=f"""Member data is current as of { lastRun.strftime("%c") }."""
    # )
    response.add_field(
        name="Team Roster",
        value=f"""The team consists of {memberCount} members, with an average iLvl of: {round(ttlIlvl / memberCount)}.  *Does not include Alts*""",
        inline=False,
    )
    # TODO:  Break value strings down to multiple sub-1024 fields if len()>1024
    if len(tanks) > 0:
        response.add_field(name="Tanks", value=tanks[0:1023], inline=False)
    if len(heals) > 0:
        response.add_field(name="Healers", value=heals[0:1023], inline=False)
    if len(mdps) > 0:
        response.add_field(name="Melee DPS", value=mdps[0:1023], inline=False)
    if len(rdps) > 0:
        response.add_field(name="Ranged DPS", value=rdps[0:1023], inline=False)
    if len(alts) > 0:
        response.add_field(name="ALTS", value=alts[0:1023], inline=False)

    await ctx.send("Here are the current raid team members.", embed=response)
    await msgId.delete()
    conn.close()

    # await cmdId.delete()


@bot.command(aliases=["mats"])
async def raidmats(ctx):
    raidMats = wowapi.getRaidMats()
    # print(raidMats)
    ahData = wowapi.getAuctionHouseData()
    umjConn = umj.create_connection()

    for mat in raidMats:
        # fill out class/subclass info from items db
        curId = raidMats[mat]["id"]
        item = umj.getItemById(umjConn, curId)
        raidMats[mat]["classname"] = item.classname
        raidMats[mat]["subclass"] = item.subclass

    for auction in ahData["auctions"]:
        # check auction data for raw mats
        if auction["item"]["id"] in raidMats:
            curID = auction["item"]["id"]
            raidMats[curID]["quantity"] += auction["quantity"]
            if (
                raidMats[curID]["unitcost"] == 0
                or auction["unit_price"] / 10000 < raidMats[curID]["unitcost"]
            ):
                raidMats[curID]["unitcost"] = auction["unit_price"] / 10000

    umjConn.close()

    # print(raidMats)
    # Herb
    # Potion
    # Flask
    # Other
    # Metal & Stone
    # Food & Drink
    # Cooking
    # Leather
    # Misc
    # Cloth
    # Other

    foodTxt = ""
    alchTxt = ""
    lwTxt = ""
    goodsTxt = ""

    for key in raidMats:
        name = raidMats[key]["name"]
        qty = raidMats[key]["quantity"]
        ttlcost = raidMats[key]["unitcost"]
        mattype = raidMats[key]["subclass"]
        matclass = raidMats[key]["classname"]
        # assign each mat to a specific embed field
        if matclass == "Tradeskill" and (mattype == "Herb" or mattype == "Other"):
            if qty > 0:
                alchTxt += f"{ name }: {qty} - *{round(ttlcost,2)}g*\n"
            else:
                alchTxt += f"{ name }: None Available\n"

        elif matclass == "Tradeskill" and mattype == "Cooking":
            if qty > 0:
                foodTxt += f"{ name }: {qty} - *{round(ttlcost,2)}g*\n"
            else:
                foodTxt += f"{ name }: None Available\n"

        elif matclass == "Tradeskill" and (
            mattype == "Leather" or mattype == "Cloth" or mattype == "Metal & Stone"
        ):
            if qty > 0:
                lwTxt += f"{ name }: {qty} - *{round(ttlcost,2)}g*\n"
            else:
                lwTxt += f"{ name }: None Available\n"

        elif (
            matclass == "Consumable"
            and (
                mattype == "Potion"
                or mattype == "Flask"
                or mattype == "Other"
                or mattype == "Food & Drink"
            )
        ) or (matclass == "Item Enhancement" and mattype == "Misc"):
            if qty > 0:
                goodsTxt += f"[{ name }](https://www.wowhead.com/item={key}): {qty} - *{round(ttlcost,2)}g*\n"
            else:
                goodsTxt += (
                    f"[{ name }](https://www.wowhead.com/item={key}): None Available\n"
                )

        else:
            print(f"{key} - {name} missing category:  {matclass} | {mattype}")

    response = discord.Embed(
        title="Raid Mats",
        url="https://www.wowhead.com/",
        description="Current auction house prices for common raid mats on our server.",
        color=discord.Color.blue(),
    )
    response.add_field(name="Alchemy Mats", value=alchTxt, inline=True)
    response.add_field(name="Cooking Mats", value=foodTxt, inline=True)
    response.add_field(name="Skin/Cloth/Mine Mats", value=lwTxt, inline=False)
    response.add_field(name="Finished Goods", value=goodsTxt, inline=False)
    response.set_footer(
        text="Auction house data is limited to hourly updates, so quantities and prices may vary slightly."
    )
    await ctx.send(embed=response)


###############################################################
###############################################################
###                                                         ###
###            ADMIN ONLY BOT COMMANDS                      ###
###                                                         ###
###############################################################
###############################################################


@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.send("Shutting down for maintenance.  Goodbye.")
    try:
        if DEVMODE:
            devmode("Bot has shut down successfully.")
        await bot.close()

    except Exception as e:
        devmode(f"Exception shutting down:\n{e}")


@bot.command()
@commands.is_owner()
async def status(ctx):
    msg = "Bot running as "
    if TESTBOT:
        msg += "TEST BOT.\n"
    else:
        msg += "PRODUCTION BOT.\n"
    msg += f"TZ:  {time.tzname}\n"
    msg += f"Server Time:  {datetime.datetime.now().strftime(TIMEFORMAT)}\n"
    msg += f"Bot Local Time:  {datetime.datetime.now().astimezone(timezone(TIMEZONE)).strftime(TIMEFORMAT)}"
    await ctx.send(msg)


### get_table_structure (hidden)
@bot.command()
@commands.is_owner()
async def get_table_structure(ctx, table):
    retList = wowapi.getTableStructure(table)
    msg = ""
    for item in retList:
        for x in range(len(item)):
            msg += f"{item[x]} "
        msg += "\n"
    await ctx.send(msg)


### get_table_contents (hidden)
@bot.command()
@commands.is_owner()
async def get_table_contents(ctx, table):
    retList = wowapi.getTableContents(table)
    msgList = []
    msg = "\n"
    for item in retList:
        curLen = len(msg)
        newMsg = "\n"
        for x in range(len(item)):
            newMsg += f"{item[x]} "
        if curLen + len(newMsg) < 2000:
            msg += newMsg
        else:
            msgList.append(msg)
            msg = newMsg
    msgList.append(msg)
    for message in msgList:
        await ctx.send(message)


@bot.command()
@commands.is_owner()
async def update_members(ctx):
    msg = "Updating members database with WoW Profile data"
    msgId = await ctx.send(msg)
    wowapi.updateAllMemberData()
    await msgId.edit(content="Members database is updated.")


@bot.command()
@commands.is_owner()
async def recreate_members_table(ctx):
    wowapi.initMembersTable()
    # wowapi.updateAllMemberData()
    await ctx.send("Members table is created and set to initial values.")


@bot.command()
@commands.is_owner()
async def recreate_full_database(ctx):
    wowapi.initConfigTable()
    wowapi.initMembersTable()
    wowapi.initRaidmatsTable()
    wowapi.initDTCacheTable()
    # wowapi.updateAllMemberData()
    await ctx.send("Fresh database initialized.")


@bot.command()
@commands.is_owner()
async def recreate_raidmats_table(ctx):
    wowapi.initRaidmatsTable()
    # wowapi.updateAllMemberData()
    await ctx.send("Raidmats table is created and set to initial values.")


def devmode(msg):
    if DEVMODE:
        print(msg)


bot.run(DISCORD_BOT_TOKEN)
