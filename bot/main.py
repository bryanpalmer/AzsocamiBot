# main.py

from os.path import join, dirname, os

import asyncio
import os
import datetime

import discord
from discord.ext import commands
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), "../.env")
load_dotenv(
    dotenv_path,
    verbose=True,
)
import wowapi
import wowclasses

# import jsonpickle

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
if DEVMODE:
    print("Environment vars: ", ENVVERSION)
    print("Current Bot: ", BOTMODE)
    print("Bot Token: ", DISCORD_BOT_TOKEN)
    print("Debug mode: ", DEBUG_MODE)
    COMMAND_PREFIX = ";"
else:
    COMMAND_PREFIX = "."


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
        embed2.add_field(
            name=".db_members", value="ADMIN: List members database rows.", inline=False
        )
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
        await ctx.send(embed=embed2)


### db_members (hidden)
@bot.command(hidden=True)
@commands.is_owner()
async def db_members(ctx):
    membersList = wowapi.getAllTableRows("members")
    msg = ""
    for member in membersList:
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
            "message", check=check, timeout=10
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
async def raidteam(ctx):
    conn = wowapi.create_connection()        
    lastRun = wowapi.getLastRun("UPDATE_MEMBERS")
    print(f"Last updated {lastRun}, current datetime {datetime.datetime.now()}")

    teamList = wowapi.getMembersList()
    team = {"Tank": [], "Healer": [], "Melee DPS": [], "Ranged DPS": [], "Alt": []}
    msgId = await ctx.send("Gathering member data...  Please wait.")

    ttlIlvl = 0
    memberCount = 0
    # waitMsg = "Gathering member data..."
    for key in teamList:
        await msgId.edit(content=f"Researching {key[1]}")
        # waitMsg += "."
        # await msgId.edit(content=waitMsg)
        charData = wowapi.getCharacterInfo(key[1], key[2])
        character = wowclasses.Character(charData)
        wowapi.updateMemberById(conn, recId, charObj):
        # devmode(vars(character))
        memberRole = key[3]
        team[memberRole].append(character)
        if memberRole != "Alt":
            ttlIlvl += character.ilvl
            memberCount += 1

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
        description="Current guild raid team roster.",
        color=discord.Color.blue(),
    )
    response.add_field(
        name="Team Roster",
        value=f"""The team consists of {memberCount} members, with an average iLvl of: {round(ttlIlvl / memberCount)}.  *Does not include Alts*""",
        inline=False,
    )
    response.add_field(name="Tanks", value=tanks[0:1023], inline=False)
    response.add_field(name="Healers", value=heals[0:1023], inline=False)
    response.add_field(name="Melee DPS", value=mdps[0:1023], inline=False)
    response.add_field(name="Ranged DPS", value=rdps[0:1023], inline=False)
    if len(alts) > 0:
        response.add_field(name="ALTS", value=alts[0:1023], inline=False)

    await ctx.send("Here are the current raid team members.", embed=response)
    await msgId.delete()
    conn.close()

    # await cmdId.delete()


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
    await ctx.send(msg)


@bot.command()
@commands.is_owner()
async def update_members(ctx):
    msg = "Updating members database with WoW Profile data"
    msgId = await ctx.send(msg)
    wowapi.updateAllMemberData()
    await msgId.edit(content="Members database is updated.")


@bot.command()
@commands.has_role("ADMIN")
async def recreate_members_table(ctx):
    wowapi.initMembersTable()
    # wowapi.updateAllMemberData()
    await ctx.send("Members table is created and set to initial values.")


@bot.command()
@commands.has_role("ADMIN")
async def recreate_raidmats_table(ctx):
    wowapi.initRaidmatsTable()
    # wowapi.updateAllMemberData()
    await ctx.send("Raidmats table is created and set to initial values.")


def devmode(msg):
    if DEVMODE:
        print(msg)


bot.run(DISCORD_BOT_TOKEN)
