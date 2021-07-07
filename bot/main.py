# main.py
# TODO: Add automatic versioning system
# versioneer
VERSION = "0.1.63"
VERSIONDATE = "2021-07-07"

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

# TODO: Set up logging for bot
# import logging

# logging.basicConfig(level=logging.INFO)

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
bot.remove_command("help")


@bot.event
async def on_ready():
    actMsg = "Let's Blame Ben"
    if DEVMODE == False:
        updateTeamDataBG.start()
    if DEVMODE == True:
        actMsg = "DEVMODE"

    await bot.change_presence(
        status=discord.Status.idle, activity=discord.Game(f"{actMsg}")
    )
    print(f"AzsocamiBot version {VERSION} is now online.")
    print(f"Bot name is {bot.user.name}, ID={bot.user.id}")
    print(f"Using {ENVVERSION}")
    print(f"Command prefix is:  {COMMAND_PREFIX}")


@tasks.loop(hours=1)
async def updateTeamDataBG():
    print("Updating Team data in background.")
    wowapi.updateAllMemberData()


# @tasks.loop(hours=1)
# async def updateMythicPlusDataBG():
#     botChannel = 742388489038987374
#     print("Updating M+ data in background.")
#     wowapi.updateMythicPlusData()


@bot.event
async def on_message(message):
    # channel = bot.get_channel(799290844862480445)
    # await channel.send(message.content)
    await bot.process_commands(message)


# @bot.event
# async def on_error(err, *args, **kwargs):
#     if err == "on_command_error":
#         await args[0].send("Something went wrong.")
#     # raise


@bot.event
async def on_command_error(ctx, exc):
    if isinstance(exc, CommandNotFound):
        # We just want to ignore Command Not Found errors
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

# HELP
@bot.command()
async def help(ctx):
    author = ctx.message.author
    embed = discord.Embed(color=discord.Color.orange())
    embed.set_author(name="Help")
    # embed.add_field(
    #     name=".ping", value="Returns Pong to check bot latency.", inline=False
    # )
    embed.add_field(
        name=".mats or .raidmats",
        value="Current Auction House pricing on common raid mats.",
        inline=False,
    )
    embed.add_field(
        name=".lpc or .legendaries",
        value=".lpc [armorType] - Auction House pricing on legendary base armors.",
        inline=False,
    )
    embed.add_field(
        name=".tc",
        value=".tc - Shows current Twisting Corridors achievement for team.",
        inline=False,
    )
    embed.add_field(
        name=".gvault or .gv",
        value="Shows current Great Vault loot from M+ keys.",
        inline=False,
    )
    embed.add_field(
        name=".bestruns or .br",
        value="Shows best timed mythic runs for season, all members.",
        inline=False,
    )
    embed.add_field(
        name=".team or .raidteam",
        value="team [update] - List current team members data. Update is Optional.",
        inline=False,
    )
    embed.add_field(
        name=".add_member",
        value="add_member <playername> [<realm>] Add new member. Realm defaults to silver-hand.",
        inline=False,
    )
    embed.add_field(
        name=".remove_member",
        value="remove_member <playername> Remove member.",
        inline=False,
    )
    embed.add_field(
        name=".change_member_role",
        value="change_member_role <playername> Change member role.",
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
    embed.add_field(
        name=".cleanbot",
        value="Cleans certain bot messages and commands from channel.",
        inline=False,
    )
    embed.add_field(
        name=".changelog",
        value="AzsocamiBot change log.",
        inline=False,
    )
    embed.add_field(
        name=".version",
        value="AzsocamiBot version info.",
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
            name=".get_table_contents",
            value="ADMIN: get_table_contents <tablename> List table contents.",
            inline=False,
        )
        embed2.add_field(
            name=".get_table_structure",
            value="ADMIN: get_table_structure <tablename> List table structure.",
            inline=False,
        )
        embed2.add_field(
            name=".add_item",
            value="ADMIN: add_item <ItemID> Add itemid to raidmats.",
            inline=False,
        )
        embed2.add_field(
            name=".remove_item",
            value="ADMIN: remove_item <ItemID> Remove itemid from raidmats.",
            inline=False,
        )

        await ctx.send(embed=embed2)


### RULES
@bot.command()
async def rules(ctx):
    msg = """
        Rule #1:  It's Ben's fault.  Always.
        Rule #2:  Loot Priority Order: Everyone else, then Ben.
        Rule #3:  When speaking to Ben, please use small words.
        Rule #4:  If you are a priest, and Ben runs past you on a narrow walkway, you must yank him back.
        Rule #5:  Thou shall not upset thy tank or thy healer.
        """
    await ctx.send(msg)


### db_members
@bot.command()
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


@bot.command()
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


@bot.command()
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
        await ctx.send("You didn't reply in time!  Cancelling player deletion.")
        await msgId.delete()


@bot.command()
@commands.has_any_role("RAID LEAD", "ADMIN", "MEMBER")
async def add_item(ctx, itemId):
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
            await ctx.send(wowapi.addItemIdToDB(itemId))
        await msg.delete()
        await msgId.delete()
    except asyncio.TimeoutError:
        await ctx.send("You didn't reply in time!  Cancelling item add.")
        await msgId.delete()


@bot.command()
@commands.has_any_role("RAID LEAD", "ADMIN", "MEMBER")
async def remove_item(ctx, itemId):
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
            await ctx.send(wowapi.deleteItemFromDB(itemId))
        await msg.delete()
        await msgId.delete()
    except asyncio.TimeoutError:
        await ctx.send("You didn't reply in time!  Cancelling item delete.")
        await msgId.delete()


@bot.command()
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


@bot.command(aliases=["tc"])
async def twistingcorridors(ctx):
    msgId = await ctx.send("Gathering member data...  Please wait.")
    teamList = wowapi.getMembersList()
    # conn = wowapi.create_connection()
    members = []
    for person in teamList:
        await msgId.edit(content=f"Retrieving {person[1]}")
        charData = wowapi.getCharacterAchievements(person[1], person[2])
        highestCompleted = 0
        completed = [(0, "None")]
        for item in charData["achievements"]:
            if item["id"] in (14468, 14469, 14470, 14471, 14472, 14568, 14569, 14570):
                if item["id"] > highestCompleted:
                    highestCompleted = item["id"]
                    completed.append((item["id"], item["achievement"]["name"]))
        HighestFinished = max(completed, key=itemgetter(1))[1]
        members.append((person[1].title(), HighestFinished))
    # conn.close()
    # print(members)
    # Build response embed
    # response = discord.Embed(
    #     title="Twisting Corridors Achievements",
    #     description=f"""Current Twisting Corridors achievements for guild team roster.""",
    #     color=discord.Color.blue(),
    # )
    # reqBy = ctx.message.author.name
    # reqPic = ctx.message.author.avatar_url
    # response.set_footer(
    #     text=f"Requested by {reqBy} | Last crawled at {localTimeStr(datetime.datetime.now())}",
    #     icon_url=reqPic,
    # )
    respVal = f"```{'Name'.ljust(15,' ')}\t{'Highest Completed'}\n"
    for member in members:
        respVal += f"{member[0].ljust(15,' ')}\t{member[1].ljust(30,' ')}\n"
    respVal += "```"
    # response.add_field(
    #     name="Roster",
    #     value=respVal,
    #     inline=False,
    # )
    await ctx.send(respVal)
    await msgId.delete()


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
        description=f"""Current guild raid team roster as of { localTimeStr(lastRun) }.\nType **{COMMAND_PREFIX}team update** to force update from WoW armory.""",
        color=discord.Color.blue(),
    )
    reqBy = ctx.message.author.name
    reqPic = ctx.message.author.avatar_url
    response.set_footer(
        text=f"Requested by {reqBy} | Last crawled at {localTimeStr(lastRun)}",
        icon_url=reqPic,
    )
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


@bot.command(aliases=["lpc"])
async def legendaries(ctx, armortype="All"):
    msgId = await ctx.send("Gathering data, please wait...")

    if armortype.lower() not in ("all", "cloth", "leather", "mail", "plate", "misc"):
        # bad argument passed, defaulting to 'All'
        armorType = "ALL"
    else:
        armorType = armortype.upper()

    armors = wowapi.getLegendaryArmorsList()
    ahData = wowapi.getAuctionHouseData()
    for auction in ahData["auctions"]:
        # check auction data for legendaries
        if auction["item"]["id"] in armors:
            curID = auction["item"]["id"]
            context = auction["item"]["context"]
            # print(curID, context)
            if context == 63:
                armors[curID]["lvl1qty"] += auction["quantity"]
                if (
                    armors[curID]["lvl1cost"] == 0
                    or auction["buyout"] / 10000 < armors[curID]["lvl1cost"]
                ):
                    armors[curID]["lvl1cost"] = auction["buyout"] / 10000
            if context == 64:
                armors[curID]["lvl2qty"] += auction["quantity"]
                if (
                    armors[curID]["lvl2cost"] == 0
                    or auction["buyout"] / 10000 < armors[curID]["lvl2cost"]
                ):
                    armors[curID]["lvl2cost"] = auction["buyout"] / 10000
            if context == 65:
                armors[curID]["lvl3qty"] += auction["quantity"]
                if (
                    armors[curID]["lvl3cost"] == 0
                    or auction["buyout"] / 10000 < armors[curID]["lvl3cost"]
                ):
                    armors[curID]["lvl3cost"] = auction["buyout"] / 10000
            if context == 66:
                armors[curID]["lvl4qty"] += auction["quantity"]
                if (
                    armors[curID]["lvl4cost"] == 0
                    or auction["buyout"] / 10000 < armors[curID]["lvl4cost"]
                ):
                    armors[curID]["lvl4cost"] = auction["buyout"] / 10000

    heading = f"{'Name'.ljust(25,' ')}\t{'iLvl 190'.rjust(10,' ')}\t{'iLvl 210'.rjust(10,' ')}\t{'iLvl 225'.rjust(10,' ')}\t{'iLvl 235'.rjust(10,' ')}\n"
    cloth = heading
    leather = heading
    mail = heading
    plate = heading
    misc = heading
    for armorId in armors:
        msgLine = f"{armors[armorId]['name'].ljust(25,' ')}\t{armors[armorId]['lvl1cost']:>10,.2f}\t{armors[armorId]['lvl2cost']:>10,.2f}\t{armors[armorId]['lvl3cost']:>10,.2f}\t{armors[armorId]['lvl4cost']:>10,.2f}\n"
        if (
            armors[armorId]["subclass"] == "Cloth"
            and "Cape" not in armors[armorId]["name"]
        ):
            cloth += msgLine
        elif armors[armorId]["subclass"] == "Leather":
            leather += msgLine
        elif armors[armorId]["subclass"] == "Mail":
            mail += msgLine
        elif armors[armorId]["subclass"] == "Plate":
            plate += msgLine
        elif (
            armors[armorId]["subclass"] == "Miscellaneous"
            or "Cape" in armors[armorId]["name"]
        ):
            misc += msgLine

    msg1 = f"**Legendary Armors**\n"
    if armorType in ("ALL", "CLOTH"):
        msg1 += f"**Cloth Armors**\n```{cloth}```\n"
    if armorType in ("ALL", "LEATHER"):
        msg1 += f"**Leather Armors**\n```{leather}```"
    msg2 = f"**Legendary Armors**\n"
    if armorType in ("ALL", "MAIL"):
        msg2 += f"**Mail Armor**\n```{mail}```\n"
    if armorType in ("ALL", "PLATE"):
        msg2 += f"**Plate Armor**\n```{plate}```"
    msg3 = f"**Legendary Armors**\n"
    if armorType in ("ALL", "MISC"):
        msg3 += f"**Miscellaneous**\n```{misc}```"

    if armorType in ("ALL", "CLOTH", "LEATHER"):
        await ctx.send(msg1)
    if armorType in ("ALL", "MAIL", "PLATE"):
        await ctx.send(msg2)
    if armorType in ("ALL", "MISC"):
        await ctx.send(msg3)
    await msgId.delete()


@bot.command(aliases=["mats"])
async def raidmats(ctx):
    raidMats = wowapi.getRaidMats()
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
    wowapi.setLastRun("AUCTION_HOUSE")
    lastRun = datetime.datetime.now()

    foodTxt = ""
    alchTxt = ""
    lwTxt = ""
    oreTxt = ""
    goodsTxt = ""
    miscTxt = ""

    for key in raidMats:
        name = raidMats[key]["name"]
        qty = raidMats[key]["quantity"]
        ttlcost = raidMats[key]["unitcost"]
        mattype = raidMats[key]["subclass"]
        matclass = raidMats[key]["classname"]
        # assign each mat to a specific embed field
        if matclass == "Tradeskill" and (mattype == "Herb" or mattype == "Other"):
            if qty > 0:
                alchTxt += f"{ name }: {qty} - *{round(ttlcost,0)}g*\n"
            else:
                alchTxt += f"{ name }: None Available\n"

        elif matclass == "Tradeskill" and mattype == "Cooking":
            if qty > 0:
                foodTxt += f"{ name }: {qty} - *{round(ttlcost,0)}g*\n"
            else:
                foodTxt += f"{ name }: None Available\n"

        elif matclass == "Tradeskill" and mattype == "Metal & Stone":
            if qty > 0:
                oreTxt += f"{ name }: {qty} - *{round(ttlcost,0)}g*\n"
            else:
                oreTxt += f"{ name }: None Available\n"

        elif matclass == "Tradeskill" and (mattype == "Leather" or mattype == "Cloth"):
            if qty > 0:
                lwTxt += f"{ name }: {qty} - *{round(ttlcost,0)}g*\n"
            else:
                lwTxt += f"{ name }: None Available\n"

        elif (
            matclass == "Consumable"
            and (
                mattype == "Potion"
                or mattype == "Flask"
                or mattype == "Other"
                or mattype == "Food & Drink"
                or mattype == "Vantus Runes"
            )
        ) or (matclass == "Item Enhancement" and mattype == "Misc"):
            if qty > 0:
                goodsTxt += f"[{ name }](https://www.wowhead.com/item={key}): {qty} - *{round(ttlcost,0)}g*\n"
            else:
                goodsTxt += (
                    f"[{ name }](https://www.wowhead.com/item={key}): None Available\n"
                )

        else:
            if qty > 0:
                miscTxt += f"{ name }: {qty} - *{round(ttlcost,0)}g*\n"
            else:
                miscTxt += f"{ name }: None Available\n"
            print(f"{key} - {name} missing category:  {matclass} | {mattype}")

    response = discord.Embed(
        title="Raid Mats",
        url="https://www.wowhead.com/",
        description="Current auction house prices for common raid mats on our server.",
        color=discord.Color.blue(),
    )
    aLines = botlib.str2embedarray(alchTxt)
    for i, line in enumerate(aLines):
        if len(line) > 0:
            fieldName = f"Alchemy Mats{'' if i==0 else ' cont.'}"
            response.add_field(name="Alchemy Mats", value=line, inline=False)

    aLines = botlib.str2embedarray(foodTxt)
    for i, line in enumerate(aLines):
        if len(line) > 0:
            fieldName = f"Cooking Mats{'' if i==0 else ' cont.'}"
            response.add_field(name=fieldName, value=line, inline=False)

    # response.add_field(name="\u200b", value="\u200b", inline=False)

    aLines = botlib.str2embedarray(lwTxt)
    for i, line in enumerate(aLines):
        if len(line) > 0:
            fieldName = f"LW / Cloth Mats{'' if i==0 else ' cont.'}"
            response.add_field(name=fieldName, value=line, inline=False)

    aLines = botlib.str2embedarray(oreTxt)
    for i, line in enumerate(aLines):
        if len(line) > 0:
            fieldName = f"Smithing Mats{'' if i==0 else ' cont.'}"
            response.add_field(name=fieldName, value=line, inline=False)

    aLines = botlib.str2embedarray(goodsTxt)
    for i, line in enumerate(aLines):
        if len(line) > 0:
            fieldName = f"Finished Goods{'' if i==0 else ' cont.'}"
            response.add_field(name=fieldName, value=line, inline=False)

    aLines = botlib.str2embedarray(miscTxt)
    for i, line in enumerate(aLines):
        if len(line) > 0:
            fieldName = f"Uncategorized Items{'' if i==0 else ' cont.'}"
            response.add_field(name=fieldName, value=line, inline=False)

    response.set_footer(
        text=f"Auction house data last collected at {localTimeStr(lastRun)}"
    )
    await ctx.send(embed=response)


####################
####################


@bot.command(aliases=["mats2"])
async def raidmats2(ctx):
    raidMats = wowapi.getRaidMats()
    ahData = wowapi.getAuctionHouseData()
    # umjConn = umj.create_connection()

    # for mat in raidMats:
    #     # fill out class/subclass info from items db
    #     curId = raidMats[mat]["id"]
    #     # item = umj.getItemById(umjConn, curId)
    #     # raidMats[mat]["classname"] = item.classname
    #     # raidMats[mat]["subclass"] = item.subclass

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

    # umjConn.close()
    wowapi.setLastRun("AUCTION_HOUSE")
    lastRun = datetime.datetime.now()

    # print(raidMats)

    ingNightShade = raidMats[171315]["unitcost"]  # 3
    ingRisingGlory = raidMats[168586]["unitcost"]  # 4
    ingMarrowRoot = raidMats[168589]["unitcost"]  # 4
    ingWidowBloom = raidMats[168583]["unitcost"]  # 4
    ingVigilsTorch = raidMats[170554]["unitcost"]  # 4
    ingFlask = raidMats[171276]["unitcost"]
    flaskCost = (
        (ingNightShade * 3)
        + (ingRisingGlory * 4)
        + (ingMarrowRoot * 4)
        + (ingWidowBloom * 4)
        + (ingVigilsTorch * 4)
    )

    msg = f"{raidMats[171276]['name']} AH Price - {ingFlask}\n"
    msg += f"{raidMats[171276]['name']} Crafted Cost - {flaskCost}\n"
    msg += f"{'Cheaper to craft your own,' if flaskCost<ingFlask else 'Cheaper to buy on AH,'} {round(ingFlask-flaskCost,2) if flaskCost<ingFlask else round(flaskCost-ingFlask,2)} savings."

    await ctx.send(msg)


####################
####################


@bot.command(aliases=["gv"])
async def gvault(ctx):
    ## id, name, realmslug, role, expires FROM members ORDER BY name
    teamList = wowapi.getMembersList()
    gvList = []
    lastReset = wowapi.getLastResetDateTime()
    for member in teamList:
        keysRun = []
        runsData = wowapi.api_raiderio_char_mplus_recent_runs(member[1], member[2])
        for run in runsData["mythic_plus_recent_runs"]:
            keyLvl = run["mythic_level"]
            rt = datetime.datetime.fromisoformat(
                run["completed_at"].replace("Z", "+00:00")
            )
            print(rt, lastReset)
            if rt > lastReset:
                keysRun.append(keyLvl)
        keysRun.sort(reverse=True)
        gvList.append((member[1].title(), keysRun))
    msg = "```| Name            | M+ Vault |   Count    |\n"
    msg += "|-----------------+----------+------------|\n"
    for member in gvList:
        # print(member)
        m1 = 0
        m4 = 0
        m10 = 0
        if len(member[1]) > 0:
            m1 = member[1][0]
        if len(member[1]) > 3:
            m4 = member[1][3]
        if len(member[1]) > 9:
            m10 = member[1][9]
        msg += f"| {member[0].ljust(15,' ')} | {(str(m1) + '/' + str(m4) + '/' + str(m10)).rjust(8,' ') } |  {str(len(member[1])).rjust(2,' ')} {'run ' if len(member[1])==1 else 'runs'}   |\n"
    msg += "```"
    print(f"Msg length: {len(msg)}")
    await ctx.send(msg)


@bot.command(aliases=["br"])
async def bestruns(ctx, seasonId=6):
    # await ctx.send(
    #     "The manually updated guild progress sheet is [online here](<https://docs.google.com/spreadsheets/d/1SULr3J7G2TkHbzHhJQJZUGYFk9LPAfX44s499NA01tw/edit#gid=0>)."
    # )
    msgId = await ctx.send(
        f"Gathering members mythic+ data for Season {seasonId}, please wait..."
    )
    ## id, name, realmslug, role, expires FROM members ORDER BY name
    teamList = wowapi.getMembersList()
    # teamRuns = []
    dungeons = {
        "Mists of Tirna Scithe": 0,
        "Sanguine Depths": 0,
        "De Other Side": 0,
        "The Necrotic Wake": 0,
        "Theater of Pain": 0,
        "Halls of Atonement": 0,
        "Spires of Ascension": 0,
        "Plaguefall": 0,
    }
    teamRuns = {}
    for member in teamList:
        if member[3] != "Alt":
            cName = member[1]
            cRealm = member[2]
            teamRuns[cName] = {
                "Name": cName,
                "Mists of Tirna Scithe": 0,
                "Sanguine Depths": 0,
                "De Other Side": 0,
                "The Necrotic Wake": 0,
                "Theater of Pain": 0,
                "Halls of Atonement": 0,
                "Spires of Ascension": 0,
                "Plaguefall": 0,
            }
            runsData = wowapi.getCharacterSeasonDetails(cName, cRealm, seasonId)
            if bool(runsData):
                print(f"Runs data for {cName}")
                # print(runsData)
                for run in runsData["best_runs"]:
                    if run["is_completed_within_time"] == True:
                        dName = run["dungeon"]["name"]
                        teamRuns[cName][dName] = run["keystone_level"]
                        # print(f"{dName} - {run['keystone_level']}")
        # print("")

    # print(teamRuns)
    msg = "```| Name                | DOS | HOA | MST |  NW |  PF |  SD | SOA | TOP | 5s|10s|15s|\n"
    msg += "|---------------------+-----+-----+-----+-----+-----+-----+-----+-----+---+---+---|\n"
    for member in teamRuns:
        print(teamRuns[member])
        mbr5s = (
            teamRuns[member]["De Other Side"] > 4
            and teamRuns[member]["Halls of Atonement"] > 4
            and teamRuns[member]["Mists of Tirna Scithe"] > 4
            and teamRuns[member]["The Necrotic Wake"] > 4
            and teamRuns[member]["Plaguefall"] > 4
            and teamRuns[member]["Sanguine Depths"] > 4
            and teamRuns[member]["Spires of Ascension"] > 4
            and teamRuns[member]["Theater of Pain"] > 4
        )
        mbr10s = (
            teamRuns[member]["De Other Side"] > 9
            and teamRuns[member]["Halls of Atonement"] > 9
            and teamRuns[member]["Mists of Tirna Scithe"] > 9
            and teamRuns[member]["The Necrotic Wake"] > 9
            and teamRuns[member]["Plaguefall"] > 9
            and teamRuns[member]["Sanguine Depths"] > 9
            and teamRuns[member]["Spires of Ascension"] > 9
            and teamRuns[member]["Theater of Pain"] > 9
        )
        mbr15s = (
            teamRuns[member]["De Other Side"] > 14
            and teamRuns[member]["Halls of Atonement"] > 14
            and teamRuns[member]["Mists of Tirna Scithe"] > 14
            and teamRuns[member]["The Necrotic Wake"] > 14
            and teamRuns[member]["Plaguefall"] > 14
            and teamRuns[member]["Sanguine Depths"] > 14
            and teamRuns[member]["Spires of Ascension"] > 14
            and teamRuns[member]["Theater of Pain"] > 14
        )

        lineval = ""
        lineval += f"| {teamRuns[member]['Name'].ljust(19,' ')} "
        lineval += f"| {str(teamRuns[member]['De Other Side']).rjust(3,' ')} "
        lineval += f"| {str(teamRuns[member]['Halls of Atonement']).rjust(3,' ')} "
        lineval += f"| {str(teamRuns[member]['Mists of Tirna Scithe']).rjust(3,' ')} "
        lineval += f"| {str(teamRuns[member]['The Necrotic Wake']).rjust(3,' ')} "
        lineval += f"| {str(teamRuns[member]['Plaguefall']).rjust(3,' ')} "
        lineval += f"| {str(teamRuns[member]['Sanguine Depths']).rjust(3,' ')} "
        lineval += f"| {str(teamRuns[member]['Spires of Ascension']).rjust(3,' ')} "
        lineval += f"| {str(teamRuns[member]['Theater of Pain']).rjust(3,' ')} "
        lineval += f"| {'*' if mbr5s else ' '} | {'*' if mbr10s else ' '} | {'*' if mbr15s else ' '} |\n"
        msg += lineval
    msg += "```"
    print(f"BestRuns msg length is: {len(msg)}")
    await ctx.send(msg)
    response = discord.Embed(
        title="Mythic+ Spreadsheet",
        description="Online manually-updated spreadsheet for mythic+ tracking is [found here](https://docs.google.com/spreadsheets/d/1SULr3J7G2TkHbzHhJQJZUGYFk9LPAfX44s499NA01tw/edit#gid=0).",
        color=discord.Color.blue(),
    )
    await ctx.send(embed=response)
    await msgId.delete()


# @bot.command(aliases=["br4"])
# async def bestrunsfor(ctx, charName, seasonId=5):
#     msgId = await ctx.send(f"Gathering mythic+ data for {charName}, please wait...")
#     ## id, name, realmslug, role, expires FROM members ORDER BY name
#     teamList = wowapi.getMembersList()
#     runsList = []
#     msg = ""
#     for member in teamList:
#         cName = member[1]
#         cRealm = member[2]
#         if cName.upper() == charName.upper():
#             msg += f"Best runs for **{cName}:** (SeasonId {seasonId})\n"
#             runsData = wowapi.getCharacterSeasonDetails(cName, cRealm, seasonId)
#             if bool(runsData):
#                 # print(f"Runs data for {cName}")
#                 # print(runsData)
#                 for run in runsData["best_runs"]:
#                     keyLvl = run["keystone_level"]
#                     keyTimed = run["is_completed_within_time"] == True
#                     kT = "**" if keyTimed else ""
#                     keyName = run["dungeon"]["name"]
#                     keyDuration = int(run["duration"] / 1000)
#                     msg += f"{kT}{keyLvl} {keyName} - {wowapi.format_duration(keyDuration)}{kT} - "
#                     keyAffixes = []
#                     for affix in run["keystone_affixes"]:
#                         keyAffixes.append(affix["name"])
#                         msg += f"{affix['name']} "
#                     runsList.append(
#                         {
#                             "name": keyName,
#                             "level": keyLvl,
#                             "timed": keyTimed,
#                             "duration": keyDuration,
#                             "affixes": keyAffixes,
#                         }
#                     )
#                     msg += f"\n"

#     await ctx.send(msg)
#     await msgId.delete()


@bot.command(aliases=["br4"])
async def bestrunsfor(ctx, charName, seasonId=6):
    # await ctx.send(
    #     "The manually updated guild progress sheet is [online here](<https://docs.google.com/spreadsheets/d/1SULr3J7G2TkHbzHhJQJZUGYFk9LPAfX44s499NA01tw/edit#gid=0>)."
    # )
    msgId = await ctx.send(f"Gathering mythic+ data for {charName}, please wait...")
    ## id, name, realmslug, role, expires FROM members ORDER BY name
    teamList = wowapi.getMembersList()
    runsList = []
    msg = ""
    for member in teamList:
        cName = member[1]
        cRealm = member[2]
        if cName.upper() == charName.upper():
            msg += f"Best runs for **{cName}:** (SeasonId {seasonId})\n"
            runsData = wowapi.getCharacterSeasonDetails(cName, cRealm, seasonId)
            if bool(runsData):
                for run in runsData["best_runs"]:
                    keyLvl = run["keystone_level"]
                    keyTimed = run["is_completed_within_time"] == True
                    kT = "**" if keyTimed else ""
                    keyName = run["dungeon"]["name"]
                    keyDuration = int(run["duration"] / 1000)
                    keyAffixes = []
                    for affix in run["keystone_affixes"]:
                        keyAffixes.append(affix["name"])
                    runsList.append(
                        {
                            "name": keyName,
                            "level": keyLvl,
                            "timed": keyTimed,
                            "duration": keyDuration,
                            "affixes": keyAffixes,
                        }
                    )
            else:
                msg = "No data found."

    sortedList = sorted(runsList, key=lambda k: k["name"])
    for item in sortedList:
        # print(item)
        iName = item["name"]
        iLvl = item["level"]
        iTimed = item["timed"]
        iDuration = item["duration"]
        iAffixes = item["affixes"]
        kT = "**" if iTimed else ""
        msg += f"{kT}{iLvl} {iName} - {wowapi.format_duration(iDuration)}{kT} - "
        for affix in iAffixes:
            msg += f"{affix} "
        msg += f"\n"

    await ctx.send(msg)
    await msgId.delete()


@bot.command()
async def roster(ctx):
    rosterJson = wowapi.getGuildRoster("silver-hand", "azsocami")
    rosterList = []

    # for member in roster["members"]:
    #     if member["character"]["level"] == 60:
    #         nPlayers += 1
    #         nClassId = member["character"]["playable_class"]["id"]
    #         print(f"{member['character']['name']} - {classes[nClassId]}")
    classes = wowapi.getClassesList()

    for member in rosterJson["members"]:
        if member["character"]["level"] == 60:
            playerName = member["character"]["name"]
            playerRealm = member["character"]["realm"]["slug"]
            playerClass = classes[member["character"]["playable_class"]["id"]]
            rosterList.append(
                {"name": playerName, "realm": playerRealm, "class": playerClass}
            )
        else:
            # Player not lvl 60, so skip
            pass
    # print(rosterList)

    sortedRoster = sorted(rosterList, key=lambda i: i["name"])

    msg = ""

    for member in sortedRoster:
        msg += f"{member['name']} ({member['realm']}) - {member['class']}\n"

    await ctx.send(msg)


###############################################################
###############################################################
###                                                         ###
###               MYTHIC BOT COMMANDS                       ###
###                                                         ###
###############################################################
###############################################################

## FOLLOW <PLAYERNAME>
@bot.command()
async def follow(ctx, playerName, realmName="silver-hand"):
    msg = wowapi.addPlayerToMythicPlus(playerName, realmName)
    await ctx.send(msg)


## UnFollow <playername>
@bot.command()
async def unfollow(ctx, playerName):
    msg = wowapi.removePlayerFromMythicPlus(playerName)
    await ctx.send(msg)


## Compare <playername> and <playername>
@bot.command()
async def compare(ctx, player1, player2):
    pass


## score <playername>
@bot.command()
async def score(ctx, playerName):
    playerRow = wowapi.getMythicPlusByName(playerName)
    print(playerRow)
    if playerRow != "":
        realm = playerRow[2]
        player = playerRow[1]
        rioScore = wowapi.api_raiderio_char_mplus_score(player, realm)
        rioPrev = wowapi.api_raiderio_char_mplus_previous(player, realm)
        rioBest = wowapi.api_raiderio_char_mplus_best_runs(player, realm)
        rioRecent = wowapi.api_raiderio_char_mplus_recent_runs(player, realm)
        # rioRank = wowapi.api_raiderio_char_mplus_rank(player, realm)

        playerClass = rioBest["class"]
        classIcon = wowapi.getClassIconUrl(playerClass)
        playerThumb = rioBest["thumbnail_url"]
        playerSpec = rioScore["active_spec_name"]
        lastCrawled = rioScore["last_crawled_at"]
        profileUrl = rioScore["profile_url"]
        playerScoreAll = rioScore["mythic_plus_scores_by_season"][0]["scores"]["all"]
        playerScorePrev = rioPrev["mythic_plus_scores_by_season"][0]["scores"]["all"]
        playerScoreTank = 0
        if "tank" in rioScore["mythic_plus_scores_by_season"][0]["scores"]:
            playerScoreTank = rioScore["mythic_plus_scores_by_season"][0]["scores"][
                "tank"
            ]

        playerScoreDps = 0
        if "dps" in rioScore["mythic_plus_scores_by_season"][0]["scores"]:
            playerScoreDps = rioScore["mythic_plus_scores_by_season"][0]["scores"][
                "dps"
            ]

        playerScoreHeals = 0
        if "healer" in rioScore["mythic_plus_scores_by_season"][0]["scores"]:
            playerScoreHeals = rioScore["mythic_plus_scores_by_season"][0]["scores"][
                "healer"
            ]
        # playerRankOverall = rioRank["mythic_plus_ranks"]["overall"]["realm"]
        # playerRankClass = rioRank["mythic_plus_ranks"]["class"]["realm"]

        # playerRankTank = rioRank["mythic_plus_ranks"]["tank"]["realm"]
        # playerRankDps = rioRank["mythic_plus_ranks"]["dps"]["realm"]
        # ##playerRankHeals = rioRank["mythic_plus_ranks"]["healer"]["realm"]

        # playerRankClassTank = rioRank["mythic_plus_ranks"]["class_tank"]["realm"]
        # playerRankClassDps = rioRank["mythic_plus_ranks"]["class_dps"]["realm"]
        # ##playerRankClassHeals = rioRank["mythic_plus_ranks"]["class_healer"]["realm"]

        # recentDungeon = rioRecent["mythic_plus_recent_runs"][0]["dungeon"]
        # recentLevel = rioRecent["mythic_plus_recent_runs"][0]["mythic_level"]
        # recentResult = rioRecent["mythic_plus_recent_runs"][0]["num_keystone_upgrades"]
        # recentScore = rioRecent["mythic_plus_recent_runs"][0]["score"]
        # recentUrl = rioRecent["mythic_plus_recent_runs"][0]["url"]

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
                "shortname": "NM",
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
            dung = run["short_name"]
            mlvl = run["mythic_level"]
            result = run["num_keystone_upgrades"]
            score = run["score"]

            ## first dungeon entry, all zeros
            if dDict[dung]["best_score"] == 0:
                dDict[dung]["best_score"] = score
                dDict[dung]["best_level"] = mlvl
                dDict[dung]["best_result"] = result
            ## something in best_score, let's check to see
            ## if current best needs to move to alt_ slots
            elif dDict[dung]["best_score"] < score:
                dDict[dung]["alt_score"] = dDict[dung]["best_score"]
                dDict[dung]["alt_level"] = dDict[dung]["best_level"]
                dDict[dung]["alt_result"] = dDict[dung]["best_result"]
                dDict[dung]["best_score"] = score
                dDict[dung]["best_level"] = mlvl
                dDict[dung]["best_result"] = result
            ## new score is less than recorded best score
            elif dDict[dung]["best_score"] > score:
                dDict[dung]["alt_score"] = score
                dDict[dung]["alt_level"] = mlvl
                dDict[dung]["alt_result"] = result

        response = discord.Embed(
            title=f"{playerScoreAll} Mythic+ Score",
            description=f"**Tank Score:** {int(playerScoreTank)}\n**Healer Score:** {int(playerScoreHeals)}\n**DPS Score:** {int(playerScoreDps)}\n**Last Season Score:** {int(playerScorePrev)}",
            color=discord.Color.red(),
        )
        classIconUrl = classIcon
        response.set_author(
            name=f"{player}, {playerSpec} {playerClass}",
            icon_url=classIconUrl,
        )
        response.set_thumbnail(url=playerThumb)

        dMsg = ""
        sMsg = ""
        aMsg = ""
        for dungeon in dDict:
            # print(dungeon)
            dName = dDict[dungeon]["shortname"]
            bestLvl = dDict[dungeon]["best_level"]
            bestScore = dDict[dungeon]["best_score"]
            bestResult = dDict[dungeon]["best_result"]
            altLvl = dDict[dungeon]["alt_level"]
            altScore = dDict[dungeon]["alt_score"]
            altResult = dDict[dungeon]["alt_result"]

            baffix = (
                "\*\*\*"
                if bestResult == 3
                else "\*\*"
                if bestResult == 2
                else "\*"
                if bestResult == 1
                else ""
            )

            aaffix = (
                "\*\*\*"
                if altResult == 3
                else "\*\*"
                if altResult == 2
                else "\*"
                if altResult == 1
                else ""
            )

            dMsg += f"{dName.upper()}\n"
            sMsg += f"{'--' if bestLvl==0 else '+'+str(bestLvl)}{baffix} ({int(bestScore)})\n"
            aMsg += f"*{'--' if altLvl==0 else '+'+str(altLvl)}{aaffix} ({int(altScore)})*\n"
        dMsg += "Highest This Week: --"

        response.add_field(name="Dungeon", value=dMsg, inline=True)
        response.add_field(name="Best (Points)", value=sMsg, inline=True)
        response.add_field(name="Alt (Points)", value=aMsg, inline=True)

        if (
            not "mythic_plus_recent_runs" in rioRecent
            or len(rioRecent["mythic_plus_recent_runs"]) == 0
        ):
            recentDungeon = "None"
            recentLevel = 0
            recentResult = 0
            recentScore = 0
            recentUrl = "#"
        else:
            recentDungeon = rioRecent["mythic_plus_recent_runs"][0]["dungeon"]
            recentLevel = rioRecent["mythic_plus_recent_runs"][0]["mythic_level"]
            recentResult = rioRecent["mythic_plus_recent_runs"][0][
                "num_keystone_upgrades"
            ]
            recentScore = rioRecent["mythic_plus_recent_runs"][0]["score"]
            recentUrl = rioRecent["mythic_plus_recent_runs"][0]["url"]

        lrMsg = f"**Dungeon:** {recentDungeon}\n"
        lrMsg += f"**Level:** +{recentLevel}\n"
        lrMsg += f"**Result:** +{recentResult}\n"
        lrMsg += f"**Points:** {recentScore}\n"
        lrMsg += f"[Group Info]({recentUrl})"
        response.add_field(name="Last Run", value=lrMsg, inline=False)

        response.set_footer(
            text=f"AzsocamiBot w/ Raider.IO Data | Last crawled at {lastCrawled}",
        )
        await ctx.send(embed=response)

    else:
        ctx.send("Player not found.")


## scores
@bot.command()
async def scores(ctx):

    scores = wowapi.getMythicPlusScores()
    scoreNames = ""
    scoreValues = ""
    currentRow = 0
    curSet = 0
    sNames = []
    sValues = []
    for row in scores:
        curSet += 1
        if curSet > 10:
            ## Exceeded 10 rows, time to reset
            sNames.append(scoreNames)
            sValues.append(scoreValues)
            scoreNames = ""
            scoreValues = ""
            curSet = 1
        ## Set values for the strings
        currentRow += 1
        scoreNames += f"{currentRow}) [{ row[1] }](https://raider.io/characters/us/{row[2].lower()}/{row[1]})\n"
        scoreValues += f"{row[3]}\n"
    ## all rows processed, add strings to the lists
    sNames.append(scoreNames)
    sValues.append(scoreValues)

    response = discord.Embed(
        title="Followed Characters for Azsocami",
        description="Sorted by Score",
        color=0x990000
        # discord.Color.blue(),
    )

    j = len(sNames)
    i = 0
    for nam, scor in zip(sNames, sValues):
        fieldName = f"Character{'' if i==0 else ' cont.'}"
        response.add_field(name=fieldName, value=nam, inline=True)
        response.add_field(name="Score", value=scor, inline=True)
        ## this is an ugly fix to keep inline fields from appearing 3 wide
        i += 1
        if i < j:
            response.add_field(name=".", value=".", inline=False)

    # response.add_field(name="Character", value=scoreNames, inline=True)
    # response.add_field(name="Score", value=scoreValues, inline=True)

    response.set_footer(
        text=f"AzsocamiBot w/ Raider.IO Data | Last crawled at {localTimeStr(datetime.datetime.now())}",
    )

    await ctx.send(embed=response)


@bot.command(aliases=["update"])
async def update_scores(ctx):
    msgId = await ctx.send("Running update.")
    updates = wowapi.updateMythicPlusScores()
    if len(updates) > 0:
        for rec in updates:
            print(rec)
            announceUpdate(rec)
    await ctx.send("Mythic+ scores updated.")
    await msgId.delete()


async def announceUpdate(ctx, rec):
    botChannel = bot.get_channel(742388489038987374)
    # "name": playerName,
    # "realm": playerRealm,
    # "high": highScore,
    # "prev": previousScore,
    await botChannel.send(
        f"{rec['name']}'s score has increased from {rec['prev']} to {rec['high']}!"
    )


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
    msg = f"AzsocamiBot version {VERSION}, released {VERSIONDATE}.\n"
    msg += "Bot running as "
    if TESTBOT:
        msg += "TEST BOT.\n"
    else:
        msg += "PRODUCTION BOT.\n"
    msg += f"Server Timezone:  {time.tzname}\n"
    msg += f"Server Time:  {datetime.datetime.now().strftime(TIMEFORMAT)}\n"
    msg += f"Bot Local Time:  {localTimeStr(datetime.datetime.now())}\n"
    msg += f"Bot source is at https://github.com/bryanpalmer/AzsocamiBot\n"
    msg += f"Bot running on heroku.com\n"
    await ctx.send(msg)


### get_table_structure
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


### get_table_contents
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
async def recreate_mythicplus_database(ctx):
    wowapi.initMythicPlusTable()
    await ctx.send("Mythic Plus database initialized.")


@bot.command()
@commands.is_owner()
async def recreate_raidmats_table(ctx):
    wowapi.initRaidmatsTable()
    # wowapi.updateAllMemberData()
    await ctx.send("Raidmats table is created and set to initial values.")


@bot.command()
async def version(ctx):
    await ctx.send(f"AzsocamiBot version {VERSION}, released {VERSIONDATE}.")


@bot.command()
async def clean(ctx, number=50):
    mgs = []
    number = int(number)
    cleaned = 0

    async for x in ctx.message.channel.history(limit=number):
        if x.author.id == bot.user.id:
            mgs.append(x)
            cleaned += 1
            # print(x)
        if x.content[:1] == COMMAND_PREFIX:
            mgs.append(x)
            cleaned += 1
            # print(x.content[:1])
    await ctx.message.channel.delete_messages(mgs)
    print(f"Removed {cleaned} messages and commands.")


@bot.command()
async def cleanbot(ctx, number=50):
    mgs = []
    number = int(number)
    cleaned = 0
    # M+ bot, this bot,
    botsList = [378005927493763074, bot.user.id]
    prefixList = [".", "*", "!", ";"]
    async for x in ctx.message.channel.history(limit=number):
        if x.author.id in botsList:
            mgs.append(x)
            cleaned += 1
            # print(x)
        elif x.content[:1] in prefixList:
            mgs.append(x)
            cleaned += 1
            # print(x.content[:1])
    await ctx.message.channel.delete_messages(mgs)
    print(f"Removed {cleaned} messages and commands.")


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


bot.run(DISCORD_BOT_TOKEN)
