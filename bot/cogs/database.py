import discord
from discord.ext import commands
import os, sys, inspect
import asyncio

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
import botlib
import wowapi

DEVMODE = os.getenv("DEVMODE") == "TRUE"  # Boolean flag for devmode


class Database(commands.Cog):
    def __init__(self, client):
        self.client = client

    ## On_Ready event for cog
    @commands.Cog.listener()
    async def on_ready(self):
        print("Database is initialized.")

    ### db_members
    @commands.command()
    @commands.is_owner()
    async def db_members(self, ctx):
        membersList = wowapi.getAllTableRows("members")
        msg = ""
        for member in membersList:
            print(member)
            for x in range(len(member)):
                msg += f"{member[x]} "
            msg += "\n"
        await ctx.send(msg)

    ### get_table_structure
    @commands.command()
    @commands.is_owner()
    async def get_table_structure(self, ctx, table):
        retList = wowapi.getTableStructure(table)
        msg = ""
        for item in retList:
            for x in range(len(item)):
                msg += f"{item[x]} "
            msg += "\n"
        await ctx.send(msg)

    ### get_table_contents
    @commands.command()
    @commands.is_owner()
    async def get_table_contents(self, ctx, table):
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

    @commands.command(hidden=True)
    @commands.is_owner()
    async def recreate_members_table(self, ctx):
        wowapi.initMembersTable()
        # wowapi.updateAllMemberData()
        await ctx.send("Members table is created and set to initial values.")

    @commands.command()
    @commands.is_owner()
    async def recreate_full_database(self, ctx):
        wowapi.initConfigTable()
        wowapi.initMembersTable()
        wowapi.initRaidmatsTable()
        wowapi.initDTCacheTable()
        # wowapi.updateAllMemberData()
        await ctx.send("Fresh database initialized.")

    @commands.command()
    @commands.is_owner()
    async def recreate_mythicplus_database(self, ctx):
        wowapi.initMythicPlusTable()
        await ctx.send("Mythic Plus database initialized.")

    @commands.command()
    @commands.is_owner()
    async def reset_all_mythicplus_scores(self, ctx):
        # wowapi.resetMythicPlusScores()
        await ctx.send("Run .update instead to grab zeroed scores from raider.io.")

    @commands.command()
    @commands.is_owner()
    async def recreate_raidmats_table(self, ctx):
        wowapi.initRaidmatsTable()
        # wowapi.updateAllMemberData()
        await ctx.send("Raidmats table is created and set to initial values.")

    @commands.command()
    @commands.is_owner()
    async def recreate_config_table(self, ctx):
        wowapi.initConfigTable()
        # wowapi.updateAllMemberData()
        await ctx.send("Config table is created and set to initial values.")


## Initialize cog
def setup(client):
    client.add_cog(Database(client))
