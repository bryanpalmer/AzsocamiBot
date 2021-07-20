import discord
from discord.ext import commands, tasks
import os, sys, inspect
import asyncio

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
import botlib

# import wowapi

DEVMODE = os.getenv("DEVMODE") == "TRUE"  # Boolean flag for devmode
ENVVERSION = os.getenv("ENV_VERSION")  # Local .env or server vars
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX")  # Bot command prefix


class Core(commands.Cog):
    """
    Core bot discord functions
    """

    def __init__(self, client):
        self.client = client

    ## On_Ready event for cog
    @commands.Cog.listener()
    async def on_ready(self):
        print("Core is initialized.")
        actMsg = "Let's Blame Ben"
        if DEVMODE == False:
            # updateTeamDataBG.start()
            # updateMythicPlusDataBG.start()
            self.botAliveCheckBG.start()
            logsChannel = self.client.get_channel(799290844862480445)
            await logsChannel.send(f"AzsocamiBot starting up: {botlib.localNow()}")
        if DEVMODE == True:
            actMsg = "DEVMODE"
            # self.botAliveCheckBG.start()
            logsChannel = self.client.get_channel(790667200197296138)
            await logsChannel.send(f"AzsocamiBot starting up: {botlib.localNow()}")

        await self.client.change_presence(
            status=discord.Status.idle, activity=discord.Game(f"{actMsg}")
        )
        # print(f"AzsocamiBot version {VERSION} is now online.")
        # print(f"Bot name is {bot.user.name}, ID={bot.user.id}")
        # print(f"Using {ENVVERSION}")
        # print(f"Command prefix is:  {COMMAND_PREFIX}")

    # region HelpCommand
    # HELP
    # @bot.command()
    # async def help(ctx):
    #     author = ctx.message.author
    #     embed = discord.Embed(color=discord.Color.orange())
    #     embed.set_author(name="Help")
    #     # embed.add_field(
    #     #     name=".ping", value="Returns Pong to check bot latency.", inline=False
    #     # )
    #     embed.add_field(
    #         name=".mats or .raidmats",
    #         value="Current Auction House pricing on common raid mats.",
    #         inline=False,
    #     )
    #     embed.add_field(
    #         name=".lpc or .legendaries",
    #         value=".lpc [armorType] - Auction House pricing on legendary base armors.",
    #         inline=False,
    #     )
    #     embed.add_field(
    #         name=".tc",
    #         value=".tc - Shows current Twisting Corridors achievement for team.",
    #         inline=False,
    #     )
    #     embed.add_field(
    #         name=".gvault or .gv",
    #         value="Shows current Great Vault loot from M+ keys.",
    #         inline=False,
    #     )
    #     embed.add_field(
    #         name=".bestruns or .br",
    #         value="Shows best timed mythic runs for season, all members.",
    #         inline=False,
    #     )
    #     embed.add_field(
    #         name=".team or .raidteam",
    #         value="team [update] - List current team members data. Update is Optional.",
    #         inline=False,
    #     )
    #     embed.add_field(
    #         name=".add_member",
    #         value="add_member <playername> [<realm>] Add new member. Realm defaults to silver-hand.",
    #         inline=False,
    #     )
    #     embed.add_field(
    #         name=".remove_member",
    #         value="remove_member <playername> Remove member.",
    #         inline=False,
    #     )
    #     embed.add_field(
    #         name=".change_member_role",
    #         value="change_member_role <playername> Change member role.",
    #         inline=False,
    #     )
    #     embed.add_field(
    #         name=".rules", value="Guild rules to live by.  Esp rule #1.", inline=False
    #     )
    #     embed.add_field(
    #         name=".clean",
    #         value="Cleans all AzsocamiBot messages and commands from channel.",
    #         inline=False,
    #     )
    #     embed.add_field(
    #         name=".cleanbot",
    #         value="Cleans certain bot messages and commands from channel.",
    #         inline=False,
    #     )
    #     embed.add_field(
    #         name=".changelog",
    #         value="AzsocamiBot change log.",
    #         inline=False,
    #     )
    #     embed.add_field(
    #         name=".version",
    #         value="AzsocamiBot version info.",
    #         inline=False,
    #     )
    #     await ctx.send(embed=embed)
    #     if author.name.lower() == "aaryn":
    #         embed2 = discord.Embed(color=discord.Color.orange())
    #         embed2.set_author(name="Admin Only Commands")
    #         # embed2.add_field(
    #         #     name=".db_members", value="ADMIN: List members database rows.", inline=False
    #         # )
    #         embed2.add_field(
    #             name=".get_table_contents",
    #             value="ADMIN: get_table_contents <tablename> List table contents.",
    #             inline=False,
    #         )
    #         embed2.add_field(
    #             name=".get_table_structure",
    #             value="ADMIN: get_table_structure <tablename> List table structure.",
    #             inline=False,
    #         )
    #         embed2.add_field(
    #             name=".add_item",
    #             value="ADMIN: add_item <ItemID> Add itemid to raidmats.",
    #             inline=False,
    #         )
    #         embed2.add_field(
    #             name=".remove_item",
    #             value="ADMIN: remove_item <ItemID> Remove itemid from raidmats.",
    #             inline=False,
    #         )

    #         await ctx.send(embed=embed2)
    # endregion

    @commands.command()
    async def rules(self, ctx):
        """ Rules to live by """
        msg = """
            **Rule #1:  It's Ben's fault.  Always.**
            Rule #2:  Be respectful to one another.
            Rule #3:  No Politics and No Religion talk.
            **Rule #4:  Keep voice chatter to a minimum during boss pulls.**
            Rule #5:  Thou shall not upset thy tank or thy healer.
            """
        await ctx.send(msg)

    @commands.command()
    async def ping(self, ctx):
        """ Generic latency test for bot """
        await ctx.send(f"🏓 Pong with {str(round(self.client.latency, 2))} seconds.")

    @commands.command(name="whoami", hidden=True)
    async def whoami(self, ctx):
        await ctx.send(f"You are {ctx.message.author.name}, using {ENVVERSION}")

    @commands.command()
    async def clean(self, ctx, number=50):
        """ Clean <number=50> AzsocamiBot commands and responses from channel """
        mgs = []
        number = int(number)
        cleaned = 0

        async for x in ctx.message.channel.history(limit=number):
            if x.author.id == self.client.user.id:
                mgs.append(x)
                cleaned += 1
                # print(x)
            if x.content[:1] == COMMAND_PREFIX:
                mgs.append(x)
                cleaned += 1
                # print(x.content[:1])
        await ctx.message.channel.delete_messages(mgs)
        print(f"Removed {cleaned} messages and commands.")

    @commands.command()
    async def cleanbot(self, ctx, number=50):
        """ Clean <number=50> bot commands and responses from channel """
        mgs = []
        number = int(number)
        cleaned = 0
        # M+ bot, this bot,
        botsList = [378005927493763074, self.client.user.id]
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

    async def botAliveCheck(self):
        if DEVMODE == False:
            botChannel = self.client.get_channel(799290844862480445)
        if DEVMODE == True:
            botChannel = self.client.get_channel(790667200197296138)
        await botChannel.send(f"botAliveCheckBG: {botlib.localNow()}")

    ###################################################################
    ###################################################################
    ##                                                               ##
    ##                       BACKGROUND TASKS                        ##
    ##                                                               ##
    ###################################################################
    ###################################################################

    @tasks.loop(minutes=15)
    async def botAliveCheckBG(self):
        print("Core:AliveCheckBG process")
        await self.botAliveCheck()

    ###################################################################
    ###################################################################
    ##                                                               ##
    ##             NOT IMPLEMENTED YET                               ##
    ##                                                               ##
    ###################################################################
    ###################################################################

    # region NotImplemented

    # @commands.command()
    # @commands.is_owner()
    # async def status(self, ctx):
    #     msg = f"AzsocamiBot version {VERSION}, released {VERSIONDATE}.\n"
    #     # msg += "Bot running as "
    #     # if TESTBOT:
    #     #     msg += "TEST BOT.\n"
    #     # else:
    #     #     msg += "PRODUCTION BOT.\n"
    #     # msg += f"Server Timezone:  {time.tzname}\n"
    #     # msg += f"Server Time:  {datetime.datetime.now().strftime(TIMEFORMAT)}\n"
    #     msg += f"Bot Local Time:  {botlib.localNow()}\n"
    #     msg += f"Bot source is at https://github.com/bryanpalmer/AzsocamiBot\n"
    #     msg += f"Bot running on heroku.com\n"
    #     await ctx.send(msg)

    # endregion


## Initialize cog
def setup(client):
    client.add_cog(Core(client))
