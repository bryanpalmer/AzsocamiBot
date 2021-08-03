import discord
from discord.ext import commands, tasks
import os, sys, inspect
import asyncio
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
import botlib
import wowapi
import wowclasses

DEVMODE = os.getenv("DEVMODE") == "TRUE"  # Boolean flag for devmode
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX")  # Bot command prefix


class Members(commands.Cog):
    """
    Guild Member commands
    """

    def __init__(self, client):
        self.client = client

    ## On_Ready event for cog
    @commands.Cog.listener()
    async def on_ready(self):
        print("Members is initialized.")
        if DEVMODE == False:
            self.updateTeamDataBG.start()

    @commands.command()
    async def add_member(self, ctx, playerName, playerRealm="silver-hand"):
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
            msg = await self.client.wait_for(
                "message", check=check, timeout=20
            )  # 20 seconds to reply
            role = wowapi.getRole(msg.content.lower())
            await ctx.send(wowapi.addMemberToDB(playerName, playerRealm, role))
            await msg.delete()
            await msgId.delete()
        except asyncio.TimeoutError:
            await ctx.send("You didn't reply in time!  Cancelling player add.")
            await msgId.delete()

    @commands.command()
    async def remove_member(self, ctx, playerName):
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
            msg = await self.client.wait_for(
                "message", check=check, timeout=20
            )  # 20 seconds to reply
            if msg.content.lower() == "y":
                await ctx.send(wowapi.deleteMemberFromDB(playerName))
            await msg.delete()
            await msgId.delete()
        except asyncio.TimeoutError:
            await ctx.send("You didn't reply in time!  Cancelling player deletion.")
            await msgId.delete()

    @commands.command()
    async def change_member_role(self, ctx, playerName):
        """ Change <playerName> current role """
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
            msg = await self.client.wait_for(
                "message", check=check, timeout=20
            )  # 30 seconds to reply
            role = wowapi.getRole(msg.content.lower())
            await ctx.send(wowapi.changeMemberRole(playerName, role))
            await msg.delete()
            await msgId.delete()
        except asyncio.TimeoutError:
            await ctx.send("You didn't reply in time!  Cancelling role change.")
            await msgId.delete()

    @commands.command(aliases=["team"])
    async def raidteam(self, ctx, arg1="DB"):
        """ Prints list of current raid team members and prominent alts """
        if arg1.lower() == "update":
            teamMode = "API"
            teamList = wowapi.getMembersList()
        else:
            teamMode = "DB"
            teamList = wowapi.getTeamMembersList()
        conn = wowapi.create_connection()
        team = {"Tank": [], "Healer": [], "Melee DPS": [], "Ranged DPS": [], "Alt": []}
        msgId = await ctx.send("Gathering member data...  Please wait.")
        ttlIlvl = 0
        memberCount = 0
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
            lastRun = datetime.now()
        else:
            lastRun = wowapi.getLastRun("UPDATE_MEMBERS")

        armoryUrl = f"https://worldofwarcraft.com/en-us/character/us/"
        # print(jsonpickle.encode(team, indent=2))

        # Tanks field
        tanks = ""
        for member in team["Tank"]:
            tanks += (
                f"**[{member.name}]({armoryUrl}{member.realmslug}/{member.name})** | "
            )
            tanks += f"{member.active_spec} {member.classname} | {member.covenant} | "
            tanks += f"{member.gender} {member.race} | iLvl: {member.ilvl}\n"
        # Healers field
        heals = ""
        for member in team["Healer"]:
            heals += (
                f"**[{member.name}]({armoryUrl}{member.realmslug}/{member.name})** | "
            )
            heals += f"{member.active_spec} {member.classname} | {member.covenant} | "
            heals += f"{member.gender} {member.race} | iLvl: {member.ilvl}\n"
        # Melee DPS field
        mdps = ""
        for member in team["Melee DPS"]:
            mdps += (
                f"**[{member.name}]({armoryUrl}{member.realmslug}/{member.name})** | "
            )
            mdps += f"{member.active_spec} {member.classname} | {member.covenant} | "
            mdps += f"{member.gender} {member.race} | iLvl: {member.ilvl}\n"
        # Ranged DPS field
        rdps = ""
        for member in team["Ranged DPS"]:
            rdps += (
                f"**[{member.name}]({armoryUrl}{member.realmslug}/{member.name})** | "
            )
            rdps += f"{member.active_spec} {member.classname} | {member.covenant} | "
            rdps += f"{member.gender} {member.race} | iLvl: {member.ilvl}\n"
        # Alts field
        alts = ""
        for member in team["Alt"]:
            alts += (
                f"**[{member.name}]({armoryUrl}{member.realmslug}/{member.name})** | "
            )
            alts += f"{member.active_spec} {member.classname} | {member.covenant} | "
            alts += f"{member.gender} {member.race} | iLvl: {member.ilvl}\n"
        # Build response embed
        response = discord.Embed(
            title="Raid Team",
            url="https://www.warcraftlogs.com/guild/calendar/556460/",
            description=f"""Current guild raid team roster as of { botlib.localTimeStr(lastRun) }.\nType **{COMMAND_PREFIX}team update** to force update from WoW armory.""",
            color=discord.Color.blue(),
        )
        reqBy = ctx.message.author.name
        reqPic = ctx.message.author.avatar_url
        response.set_footer(
            text=f"Requested by {reqBy} | Last crawled at {botlib.localTimeStr(lastRun)}",
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

    # @commands.command()
    # async def roster(self, ctx):
    #     pass

    @commands.command(aliases=["tc"])
    async def twistingcorridors(self, ctx):
        msgId = await ctx.send("Gathering member data...  Please wait.")
        teamList = wowapi.getMembersList()
        members = []
        for person in teamList:
            await msgId.edit(content=f"Retrieving {person[1]}")
            charData = wowapi.getCharacterAchievements(person[1], person[2])
            highestCompleted = 0
            completed = [(0, "None")]
            for item in charData["achievements"]:
                if item["id"] in (
                    14468,
                    14469,
                    14470,
                    14471,
                    14472,
                    14568,
                    14569,
                    14570,
                ):
                    if item["id"] > highestCompleted:
                        highestCompleted = item["id"]
                        completed.append((item["id"], item["achievement"]["name"]))
            HighestFinished = max(completed, key=itemgetter(1))[1]
            members.append((person[1].title(), HighestFinished))
        respVal = f"```{'Name'.ljust(15,' ')}\t{'Highest Completed'}\n"
        for member in members:
            respVal += f"{member[0].ljust(15,' ')}\t{member[1].ljust(30,' ')}\n"
        respVal += "```"
        await ctx.send(respVal)
        await msgId.delete()

    # @commands.command(name="gvault", aliases=["gv"])
    # async def greatvault(self, ctx):
    #     pass

    @commands.command()
    @commands.is_owner()
    async def update_members(self, ctx):
        msg = "Updating members database with WoW Profile data"
        msgId = await ctx.send(msg)
        wowapi.updateAllMemberData()
        await msgId.edit(content="Members database is updated.")

    ###################################################################
    ###################################################################
    ##                                                               ##
    ##                       BACKGROUND TASKS                        ##
    ##                                                               ##
    ###################################################################
    ###################################################################

    @tasks.loop(hours=2)
    async def updateTeamDataBG(self):
        print("Members:updateTeamDataBG process (2 hours)")
        if DEVMODE == False:
            # bot-logs channel 799290844862480445
            botLogs = self.client.get_channel(799290844862480445)
        if DEVMODE == True:
            botLogs = self.client.get_channel(790667200197296138)
        await botLogs.send(f"UpdateTeamDataBG: {botlib.localNow()}")
        wowapi.updateAllMemberData()


## Initialize cog
def setup(client):
    client.add_cog(Members(client))
